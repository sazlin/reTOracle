#!
"""
A Python Worker that watches a reTOracle DB and runs
sentiment analysis (SA) on any Tweets that need it. If there are
a lot of Tweets needing SA then use Amazon EMR (Hadoop) to
run SA on those Tweets in parallel
"""

# import sys
import json
import time
import sys
import boto
import sql_queries as sql_q
from boto.s3.key import Key
import boto.emr
from boto.emr.step import StreamingStep
import SA_Mapper
from SentimentAnalysis import agg_sent
from logger import make_logger
import inspect

logger = make_logger(inspect.stack()[0][1], 'retoracle.log')

# At most the worker will check for more Tweets to
# analyze every MIN_EXECUTION_PERIOD seconds
MIN_EXECUTION_PERIOD = 5.0

# If the number of Tweets to analyze is > EMR_THRESHOLD
# Then this worker will use Hadoop to do SA
# But only is ALLOW_EMR is also True
EMR_THRESHOLD = 1000

# When creating a Hadoop job, whats the max batch size to aim for?
MAX_BATCH_SIZE = 5000

# Allow this worker to spin up EMR (Amazon's Hadoop)
# jobs for up to BATCH_SIZE batches of Tweets that need SA?
ALLOW_EMR = False

# Number of total nodes to use for EMR jobs
# 1 Node is always used for Master/Controller node, rest are Slave/Cores
# EMR_NUM_TOTAL_NODES - 1 = # of slave nodes
# Ex: EMR_NUM_TOTAL_NODES = 1 --> 1 master node, 1 core node
# Ex. EMR_NUM_TOTAL_NODES = 4 --> 1 master node, 3 core nodes
EMR_NUM_TOTAL_NODES = 2

# Instance type of slave nodes
EMR_TYPE_SLAVE_NODES = 'm1.small'

# Instance type of master node
EMR_TYPE_MASTER_NODE = 'm1.small'

# AMI_version for Hadoop
# !!! Don't change unless you want to debug config failures !!!
EMR_AMI_VERSION = '2.4.6'

# EC2 Key-Value pair to use for instances
EMR_KP = 'kp1'

# Enable debugging on instances?
EMR_DEBUGGING = False


def _delete_key_if_exists(bucket, key_str):
    """delete a specified key from S3 if the key exists"""
    if bucket:
        key = bucket.get_key(key_str)
        if key:
            print "Deleting ", key.name
            key.delete()


def cleanup(bucket):
    """clean up any existing inputs and output from S3"""
    print "Cleaning up any lingering input and output on S3..."
    _delete_key_if_exists(bucket, 'sa_input')
    _delete_key_if_exists(bucket, 'sa_mapper.py')
    _delete_key_if_exists(bucket, 'sa_reducer.py')
    if bucket:
        for output_part in bucket.list(prefix='sa_output'):
            print "Deleting ", output_part.name
            output_part.delete()
    _delete_key_if_exists(bucket, 'sa_output')
    print "Done."


def _create_sa_input(key, bs):
    """get batch of Tweets from SQL, format into proper string,
        and upload to S3"""

    # put input data on S3 so ElasticMapReduce can get at it
    json_results = sql_q.get_query_results('tweet_batch', [bs])

    #need to have one tweet per line with a \n in it per:
    #https://docs.aws.amazon.com/ElasticMapReduce/latest/DeveloperGuide/emr-plan-input-accept.html
    tweets = json.loads(json_results)
    sa_input = []
    for tweet in tweets:
        tweet[1] = tweet[1].rstrip()
        sa_input.append(json.dumps(tweet))
    key.key = 'sa_input'
    key.set_contents_from_string('\n'.join(sa_input))


def _copy_sa_mapper(key):
    """Put mapper script on S3"""

    key.key = 'sa_mapper.py'
    key.set_contents_from_filename(
        'sa_mapper.py',
        replace=True,
        reduced_redundancy=True,)


def _copy_sa_reducer(key):
    """Put reducer script on S3"""

    key.key = 'sa_reducer.py'
    key.set_contents_from_filename(
        'sa_reducer.py',
        replace=True,
        reduced_redundancy=True,)


def create_inputs(key, bs):
    """Create the sa_input, sa_mapper, and sa_reducer on S3"""

    _create_sa_input(key, bs)
    _copy_sa_mapper(key)
    _copy_sa_reducer(key)


def _get_num_tweets_need_sa():
    json_results = sql_q.get_query_results('num_tweets_need_sa')
    try:
        return json.loads(json_results)[0][0]
    except Exception as x:
        print "Could not parse JSON query results for 'num_tweets_need_sa':", x.args


def _create_sa_job(emr_conn):
    """Create and start an EMR job asynchronously"""

    step = StreamingStep(
        name='reTOracle Sentiment Analysis Step',
        mapper='s3n://retoracle/sa_mapper.py',
        reducer='s3n://retoracle/sa_reducer.py',
        input='s3n://retoracle/sa_input',
        output='s3n://retoracle/sa_output')
    return emr_conn.run_jobflow(
        name='reTOracle Sentiment Analysis Job',
        log_uri='s3://retoracle/jobflow_logs',
        steps=[step],
        num_instances=EMR_NUM_TOTAL_NODES,
        master_instance_type=EMR_TYPE_MASTER_NODE,
        slave_instance_type=EMR_TYPE_SLAVE_NODES,
        ec2_keyname=EMR_KP,
        enable_debugging=EMR_DEBUGGING,
        ami_version=EMR_AMI_VERSION,
        )


def _wait_for_job_to_complete(emr_conn, jobid):
    """Wait for the EMR job to complete. Keep UI responsive."""

    print "Waiting for job to complete..."
    #be careful when calling describe_jobflow()... it doesn't like lots of polling
    job_state = emr_conn.describe_jobflow(jobid).state
    while job_state == "RUNNING" or\
            job_state == "STARTING" or\
            job_state == "WAITING":
            t1 = time.time()
            print "Job in progress, waiting to check",
            #poll about once every 10 seconds, but have UI
            #that is more responsive than that
            while time.time() - t1 < 10.0:
                print ".",
                sys.stdout.flush()
                time.sleep(2)
            print "Checking job status..."
            job_state = emr_conn.describe_jobflow(jobid).state
    print "Job Done"
    print "Last JobState:", job_state


def push_sa_results_to_sql_from_s3(bucket):
    print "Getting results from S3...",
    json_result_list = []
    for output_part in bucket.list(prefix='sa_output'):
        json_result_list.append(output_part.get_contents_as_string())
    json_results = "\n".join(json_result_list)
    print "Done."
    print "Outputting results to SQL..."
    results = json_results.splitlines()
    count = 1
    total = len(results)
    print "Num results: ", total
    for result in iter(results):
        try:
            #make sure the result is valid json, else skip
            tweet_sent = json.loads(result)
        except:
            print "Invalid output on this line, skipping..."
        else:
            sql_q.get_query_results(
                'set_tweet_sent',
                [result],  # must be a iterable, and result is a string
                False)
            print result
            print "[", count, "of", total, "]"
            count += 1
    print "Done."


def main():
    logger.info('SA_Worker: initializing sql...')
    sql_q.init()
    logger.info('SA_Worker: initializing SA_Mapper...')
    SA_Mapper.setup_SA()
    while True:
        logger.info('SA_Worker: Getting number of tweets that need SA...')
        num_todo = _get_num_tweets_need_sa()
        logger.info("SA_Worker: num_todo: %s", num_todo)
        last_check = time.time()
        if num_todo >= EMR_THRESHOLD and ALLOW_EMR:
            logger.info("SA_Worker: Using Hadoop to do SA")
            # There's a lot of Tweets to analyze, so spin up
            # a EMR job to tackle them one BATCH_SIZE at a time

            #Get a connection to S3
            s3_conn = boto.connect_s3()

            #Grab the reTOracle bucket & key
            bucket = s3_conn.get_bucket('retoracle')
            key = Key(bucket)

            #Cleanup any input or output lingering from previous jobs
            cleanup(bucket)

            #Create and upload the data and scripts that the EMR job needs
            #everything up to MAX_BATCH_SIZE
            create_inputs(key, min(num_todo, MAX_BATCH_SIZE))

            #Create and start the EMR job
            emr_conn = boto.emr.connect_to_region('us-west-2')
            jobid = _create_sa_job(emr_conn)
            print "Started EMR Job", jobid

            #Wait for the EMR job to complete
            _wait_for_job_to_complete(emr_conn, jobid)

            #EMR Job is done, so get SA results and push to SQL
            push_sa_results_to_sql_from_s3(bucket)

        else:
            logger.info("SA_Worker: Doing SA locally")
            #Process Tweets using this worker (not EMR)

            #Get the remaining Tweets that need SA
            logger.info("SA_Worker: Getting Tweet batch...")
            tweet_batch = json.loads(
                sql_q.get_query_results(
                    'tweet_batch',
                    [min(num_todo, MAX_BATCH_SIZE)]))

            #Run SA on each Tweet and then upload its results to SQL
            count = 1
            total = len(tweet_batch)
            logger.info("SA_Worker: Running SA on each Tweet...")
            for tweet in tweet_batch:
                #do SA magics locally
                result_dict = SA_Mapper.run_SA(tweet)
                neg_probs = []
                pos_probs = []
                for key in result_dict:
                    if "_neg_" in key.lower():
                        neg_probs.append(result_dict[key])
                    elif "_pos_" in key.lower():
                        pos_probs.append(result_dict[key])
                agg_sent_result = agg_sent.get_agg_sent(neg_probs, pos_probs)
                result_dict['agg_sent'] = agg_sent_result[0]
                result_dict['agg_prob'] = agg_sent_result[1]
                delicious_payload = json.dumps(result_dict)
                sql_q.get_query_results(
                    'set_tweet_sent',
                    [delicious_payload.lower()],  # must be a iterable
                    False)
                #print delicious_payload.lower(), "[", count, "of", total, "]"
                count += 1

        #Wait a short while (if needed) before checking for more Tweets
        time_spent = time.time() - last_check
        if time_spent < MIN_EXECUTION_PERIOD:
            time.sleep(MIN_EXECUTION_PERIOD - time_spent)

if __name__ == "__main__":
    try:
        if sys.argv[2]:
            if sys.argv[2] == 'False':
                ALLOW_EMR = False
    except IndexError:
        pass
    main()

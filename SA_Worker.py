#!
"""
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

MIN_EXECUTION_PERIOD = 5.0
BATCH_SIZE = 10000


def _delete_key_if_exists(bucket, key_str):
    """delete a specified key from S3 if the key exists"""
    if bucket:
        key = bucket.get_key(key_str)
        if key:
            key.delete()


def cleanup(bucket):
    """clean up any existing inputs and output from S3"""
    _delete_key_if_exists(bucket, 'sa_input')
    _delete_key_if_exists(bucket, 'sa_mapper.py')
    _delete_key_if_exists(bucket, 'sa_reducer.py')
    _delete_key_if_exists(bucket, 'sa_output/part-00000')
    _delete_key_if_exists(bucket, 'sa_output/_SUCCESS')
    _delete_key_if_exists(bucket, 'sa_output')


def _create_sa_input(key, bs):
    """get batch of Tweets from SQL, format into proper string,
        and upload to S3"""

    # put input data on S3 so ElasticMapReduce can get at it
    json_results = sql_q.get_query_results('tweet_batch', bs)

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
        json.loads(json_results)
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
        num_instances=1,
        master_instance_type='m1.medium',
        slave_instance_type='m1.medium',
        ec2_keyname='kp1',
        enable_debugging=True,
        # job_flow_role='EMR_EC2_DefaultRole',
        ami_version='2.4.6',
        # api_params={'service-role': 'EMR_DefaultRole'}
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
    output_key = bucket.get_key('sa_output/part-00000')
    if not output_key:
        raise Exception('No output or wrong output key specified')
    print "Getting results from S3...",
    json_results = output_key.get_contents_as_string()
    print "Done."
    print "Outputting results to SQL..."
    for result in iter(json_results.splitlines()):
        try:
            tweet_sent = json.loads(result)
        except:
            print "Invalid output on this line, skipping..."
        else:
            sql_q.get_query_results(
                'set_tweet_sent',
                (tweet_sent[0], int(tweet_sent[1])),
                False)
            print tweet_sent[0], int(tweet_sent[1])
    print "Done."


def main():
    sql_q.init()
    while True:
        num_todo = _get_num_tweets_need_sa()
        last_check = time.time()
        if num_todo >= BATCH_SIZE:
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
            create_inputs(key, BATCH_SIZE)

            #Create and start the EMR job
            emr_conn = boto.emr.connect_to_region('us-west-2')
            jobid = _create_sa_job(emr_conn)
            print "Started EMR Job", jobid

            #Wait for the EMR job to complete
            _wait_for_job_to_complete(emr_conn)

            #EMR Job is done, so get SA results and push to SQL
            push_sa_results_to_sql_from_s3(bucket)

        else:
            #There aren't a lot of Tweets left to analyze, so just
            #process them here

            #Get the remaining Tweets that need SA
            tweet_batch = json.loads(
                sql_q.get_query_results('tweet_batch', [num_todo]))

            #Run SA on each Tweet and then upload its results to SQL
            for tweet in tweet_batch:
                sql_q.get_query_results(
                    'set_tweet_sent',
                    (tweet[0], 1),
                    False)
                print tweet[0], 1

        #Wait a short while (if needed) before checking for more Tweets
        time_spent = time.time() - last_check
        if time_spent < MIN_EXECUTION_PERIOD:
            time.sleep(MIN_EXECUTION_PERIOD - time_spent)

if __name__ == "__main__":
    main()

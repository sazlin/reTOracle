#!/usr/bin/env python
"""
"""

# import sys
import json
import sql_queries as sql_q
import boto
from boto.s3.key import Key
import time

MIN_EXECUTION_PERIOD = 5.0


def main():
    sql_q.init()
    s3_conn = boto.connect_s3()
    bucket = s3_conn.get_bucket('retoracle')
    key = Key(bucket)
    while True:
        json_results = sql_q.get_query_results('num_tweets_need_sa')
        num_todo = json.loads(json_results)
        last_check = time.time()
        if True:
            # put input data on S3 so ElasticMapReduce can get at it
            json_results = sql_q.get_query_results('tweet_batch')
            key.key = 'sa_input'
            key.set_contents_from_string(json_results)

            # put mapper script on S3
            key.key = 'sa_mapper.py'
            key.set_contents_from_filename(
                'sa_mapper.py',
                replace=True,
                reduced_redundancy=True,)

            #TODO: create and run MapReduce job

            #get results and pipe back to db
            key.key = 'sa_results'
            json_results = key.get_contents_as_string()
            results = json.loads(json_results)
            for result in results:
                # import pdb; pdb.set_trace()
                sql_q.get_query_results(
                    'set_tweet_sent',
                    (result[0], 1),
                    False)
                print result[0], 1
        else:
            tweet_batch = json.loads(sql_q.get_query_results('tweet_batch'))
            for tweet in tweet_batch:
                # import pdb; pdb.set_trace()
                sql_q.get_query_results(
                    'set_tweet_sent',
                    (tweet[0], 1),
                    False)
                print tweet[0], 1
        time_spent = time.time() - last_check
        if time_spent < MIN_EXECUTION_PERIOD:
            print "Too fast... sleeping..."
            time.sleep(MIN_EXECUTION_PERIOD - time_spent)
            print "Nap over! Back to work."

if __name__ == "__main__":
    main()

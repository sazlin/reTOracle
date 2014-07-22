#!/usr/bin/env python
"""This mapping function takes in a tweet's text, applies
    sentiment analysis functions against it, and then outputs
    a dictionary of scores for each sentiment analysis function."""

# import sys
import json
import sql_queries as sql_q
import time

MIN_EXECUTION_PERIOD = 5.0

def main(separator='\t'):
    #get batch of tweet
    sql_q.init()
    while True:
        json_results = sql_q.get_query_results('num_tweets_need_sa')
        num_todo = json.loads(json_results)
        last_check = time.time()
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

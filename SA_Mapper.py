#!/usr/bin/env python
"""This mapping function takes in a tweet's text, applies
    sentiment analysis functions against it, and then outputs
    a dictionary of scores for each sentiment analysis function."""

# import sys
import json
import sql_queries as sql_q


def main(separator='\t'):
    #get batch of tweet
    sql_q.init()
    json_results = sql_q.get_query_results('num_tweets_need_sa')
    print "Json results:", json_results
    num_todo = json.loads(json_results)
    print "Num Todo:", num_todo
    tweets_to_analyze = json.loads(sql_q.get_query_results('tweet_batch'))
    #print tweets_to_analyze
    for tweet in tweets_to_analyze:
        # import pdb; pdb.set_trace()
        sql_q.get_query_results(
            'set_tweet_sent',
            (tweet[0], 1),
            False)
        print tweet[0], 1

    # data = read_input(sys.stdin)
    # d = {'test_val': 1}
    #do sentiment analysis on tweet here
    # write the results to STDOUT (standard output);
    # what we output here will be the input for the
    # Reduce step, i.e. the input for reducer.py
    #
     # print json.dumps(d)

if __name__ == "__main__":
    main()

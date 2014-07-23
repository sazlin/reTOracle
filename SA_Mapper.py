#!/usr/bin/python

import json
import sys


def main(argv):
    # try:
    for line in sys.stdin:
        # try:
        try:
            tweet = json.loads(line)
        except Exception:
            pass  # skip this tweet
        else:
            # except Exception as x:
            #     print "Error parsing json: ", x.args
            # print "Done."
            # for tweet in tweet_batch:
            print str(tweet[0]) + '\t' + '1'
    # except Exception as x:
    #     return "Something went wrong: ", x.args

if __name__ == "__main__":
    main(sys.argv)

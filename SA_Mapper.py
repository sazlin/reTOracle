#!/usr/bin/python

import json
import sys


def main(argv):
    try:
        print "reading input..."
        json_result = sys.stdin.read()
        print json_result
        print "parsing json...",
        try:
            tweet_batch = json.loads(json_result)
        except Exception as x:
            print "Error parsing json: ", x.args
        print "Done."
        for tweet in tweet_batch:
            print tweet[0] + '\t' + '1'
    except Exception as x:
        return "Something went wrong: ", x.args

if __name__ == "__main__":
    main(sys.argv)

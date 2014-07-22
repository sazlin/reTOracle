#!/usr/bin/python

import json
import sys


def main(argv):
    try:
        tweet_batch = json.loads(sys.stdin.read())
        for tweet in tweet_batch:
            print tweet[0] + '\t' + '1'
    except "end of file":
        return None

if __name__ == "__main__":
    main(sys.argv)

#!/usr/bin/python

import json
import sys


def main(argv):
    for line in sys.stdin:
        try:
            tweet = json.loads(line)
        except Exception:
            pass  # skip this tweet
        else:
            print str(tweet[0]) + '\t' + '1'

if __name__ == "__main__":
    main(sys.argv)

#!/usr/bin/python

import json
import sys


def _setup_LR():
    pass


def _setup_SVM():
    pass


def _setup_DatumBox():
    pass


def setup_SA():
    _setup_LR()
    _setup_SVM()
    _setup_DatumBox()


def run_SA(tweet, ret_dict=None):
    if not ret_dict:
        ret_dict = {}
    ret_dict = {'tweet_id': tweet[0]}
    _run_LR_SA(tweet, ret_dict)
    _run_SVM_SA(tweet, ret_dict)
    _run_DatumBox(tweet, ret_dict)
    return ret_dict


def _run_LR_SA(tweet, ret_dict):
    ret_dict['LR_SENT'] = 1
    ret_dict['LR_NEG_PROB'] = 0.3
    ret_dict['LR_POS_PROB'] = 0.89
    ret_dict['LR_EXEC_TIME'] = 0.424

    #do magic
    return ret_dict


def _run_SVM_SA(tweet, ret_dict):
    ret_dict['SVM_SENT'] = 0
    ret_dict['SVM_NEG_PROB'] = 0.45
    ret_dict['SVM_POS_PROB'] = 0.55
    ret_dict['SVM_EXEC_TIME'] = 0.674

    #do magic
    return ret_dict


def _run_DatumBox(tweet, ret_dict):
    ret_dict['DatumBox_SENT'] = -1
    ret_dict['DatumBox_NEG_PROB'] = 0.7
    ret_dict['DatumBox_POS_PROB'] = 0.36
    ret_dict['DatumBox_EXEC_TIME'] = 4.8

    #do magic
    return ret_dict


def main(argv):
    setup_SA()
    for line in sys.stdin:
        try:
            tweet = json.loads(line)
        except Exception:
            pass  # skip this tweet
        else:
            #do SA magics
            delicious_payload = json.dumps(run_SA(tweet))
            print delicious_payload.lower()
            #print str(tweet[0]) + '\t' + '1'

if __name__ == "__main__":
    main(sys.argv)

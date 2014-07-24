#!/usr/bin/python

import json
import time
import sys
from sentimentML.ML_builder import ML_builder
from datum_box import box_tweet

# DBox = None
# Datum_Integers = {'positive': 1, 'neutral': 0, 'negative': -1}
SVM = None

def _setup_LR():
    pass


def _setup_SVM():
    global SVM
    SVM = ML_builder()
    SVM.ML_build()


def _setup_DatumBox():
    pass
    # global DBox
    # Datum_api_key = os.getenv('DATUM')
    # DBox = DatumBox(Datum_api_key)


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
    t1 = time.time()
    result = SVM.Predict(tweet)
    t2 = time.time()
    ret_dict['SVM_SENT'] = result[0]
    if result == 1:
        ret_dict['SVM_NEG_PROB'] = -1
        ret_dict['SVM_POS_PROB'] = result[1]
    elif result == -1:
        ret_dict['SVM_NEG_PROB'] = result[1]
        ret_dict['SVM_POS_PROB'] = -1
    else:
        ret_dict['SVM_NEG_PROB'] = -1
        ret_dict['SVM_POS_PROB'] = -1
    ret_dict['SVM_EXEC_TIME'] = t2 - t1

    #do magic
    return ret_dict


def _run_DatumBox(tweet, ret_dict):
    t1 = time.time()
    result = box_tweet(tweet)
    t2 = time.time()
    ret_dict['DatumBox_SENT'] = result
    ret_dict['DatumBox_NEG_PROB'] = -1
    ret_dict['DatumBox_POS_PROB'] = -1
    ret_dict['DatumBox_EXEC_TIME'] = t2 - t1

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

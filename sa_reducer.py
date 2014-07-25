#!/usr/bin/python
import sys
import json
from SentimentAnalysis import agg_sent
#identity reducer
for line in sys.stdin:
    if line == "\n":
        pass
    else:
        try:
            result_dict = json.loads(line)
        except Exception:
            #invalid input, so skip this line
            pass
        else:
            neg_probs = []
            pos_probs = []
            for key in result_dict:
                if "_neg_" in key.lower():
                    neg_probs.append(result_dict[key])
                elif "_pos_" in key.lower():
                    pos_probs.append(result_dict[key])
            agg_sent_result = agg_sent.get_agg_sent(neg_probs, pos_probs)
            result_dict['agg_sent'] = agg_sent_result[0]
            result_dict['agg_prob'] = agg_sent_result[1]
            print json.dumps(result_dict)

#!/usr/bin/python
def get_agg_sent(neg_probs, pos_probs):
    """calculate an aggregate sentiment from the provided probabilities"""
    if not neg_probs:
        raise Exception("neg_probs is None")
    if not pos_probs:
        raise Exception("pos_probs is None")
    if not len(neg_probs) == len(pos_probs):
        raise Exception("length of neg_probs and pos_probs must match")

    sum_pos = sum(pos_probs)
    sum_neg = sum(neg_probs)
    avg_prob = (sum_pos - sum_neg) / len(pos_probs)
    if -1.0 <= avg_prob < -0.025:
        return (-1, avg_prob)
    elif -0.025 <= avg_prob <= 0.025:
        return (0, avg_prob)
    elif 0.025 < avg_prob <= 1.0:
        return (1, avg_prob)
    else:
        raise Exception("avg_prob not within [-1,1]")

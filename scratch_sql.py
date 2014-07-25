def get_tweet_filter():
    tweet_filters = None
    for hashtag in hashtags1:
        hashtag = '#'+hashtag
        for filter_ in filter_list:
            tmp_list = [x.lower() for x in filter_list[filter_]['search_terms']['hashtags']]
            if hashtag.lower() in tmp_list:
                tweet_filters = sql_q.get_query_results('find_filter', [filter_], True, False)
    return tweet_filters[0][0]


fetch_tweets = None
filter_list = None
fetch_agg_vals = None


fetch_tweets = """
SELECT * FROM tweets WHERE filter_name = %s;
"""

fetch_agg_vals = """
SELECT agg_sent FROM tweet_sent WHERE tweet_id in (
    SELECT tweet_id FROM tweets WHERE filter_name = %s);
"""


fetch_recent_sentiment = """
SELECT tweet_id, agg_sent FROM tweet_sent
ORDER BY tweet_id DESC
LIMIT 10;
"""

fetch_recent_tweets = """
SELECT screen_name, text FROM tweets
WHERE tweet_id in (
    SELECT tweet_id, agg_sent FROM tweet_sent
    ORDER BY tweet_id DESC
    LIMIT 10);
"""



@app.route('/q1', methods=['GET'])
def q1_query():
    final_output = []
    for language in filter_list:
        pos, neg, neutral = 0, 0, 0
        # tweet ids needs to be a list of tuples
        agg_vals = sql_q.get_query_results('fetch_agg_vals', language)
        for val in agg_vals:
            if val == 1:
                pos += 1
            elif val == 0:
                neg += 1
            else:
                neutral += 1
        final_output.append([language, pos, neg, neutral])
    resp = Response(response=final_output,
                status=200,
                mimetype="application/json")
    return resp

@app.route('/ticker', methods=['GET'])
def ticker_fetch():
    """Return JSON for recent tweet"""
    json_result = sql_q.get_query_results('ticker1')

    resp = Response(response=json_result,
                    status=200,
                    mimetype="application/json")
    return resp

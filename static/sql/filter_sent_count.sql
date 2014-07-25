SELECT tweet_filter_join.filter_name, tweet_sent.agg_sent,
COUNT(distinct tweet_sent.tweet_id)
FROM tweet_filter_join, tweet_sent
WHERE tweet_filter_join.tweet_id = tweet_sent.tweet_id
GROUP BY filter_name, tweet_sent.agg_sent
ORDER BY filter_name;
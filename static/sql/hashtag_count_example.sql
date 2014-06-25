SELECT hashtag, COUNT(hashtag) as HashTagCount 
FROM (SELECT screen_name, unnest(hashtags) as hashtag FROM massive WHERE screen_name = '@SeanAzlin2') as sub
GROUP BY hashtag
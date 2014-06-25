SELECT hashtag, COUNT(hashtag) as HashTagCount
FROM (SELECT screen_name, unnest(hashtags) as hashtag FROM massive) as subquery
WHERE 
hashtag = 'Java' OR 
hashtag = 'Python' OR 
hashtag = 'JavaScript' OR 
hashtag = 'CPlusPlus' OR 
hashtag = 'Java'
GROUP BY hashtag
ORDER BY HashTagCount DESC
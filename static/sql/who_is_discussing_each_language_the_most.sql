SELECT hashtag, HashTagCount, screen_name
FROM
(
	SELECT hashtag, screen_name, HashTagCount, rank() OVER (PARTITION BY hashtag ORDER BY HashTagCount DESC, screen_name) AS pos
	FROM (
		SELECT hashtag, screen_name, COUNT(hashtag) as HashTagCount
		FROM (	
			SELECT screen_name, unnest(hashtags) as hashtag 
			FROM massive
		) as unwrap
		WHERE 
		hashtag = 'Java' OR 
		hashtag = 'Python' OR 
		hashtag = 'JavaScript' OR 
		hashtag = 'CPlusPlus' OR 
		hashtag = 'Java'
		GROUP BY screen_name, hashtag
		ORDER BY hashtag, HashTagCount DESC
	) as countedhashtags
) as ss
WHERE pos < 4
ORDER BY hashtag, HashTagCount DESC

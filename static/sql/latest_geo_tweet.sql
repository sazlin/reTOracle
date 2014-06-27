SELECT * 
FROM massive 
WHERE json_array_length(location) <> 0
ORDER BY tweet_id DESC
LIMIT 1
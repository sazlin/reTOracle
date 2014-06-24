INSERT INTO massive (
	tweet_id, 
	text, 
	hashtags, 
	user_mentions, 
	created_at, 
	screen_name, 
	url, 
	location, 
	inreplytostatusif, 
	retweetcount)
VALUES (
	'testrecordid12345',
	'This is a fake tweet inserted into the db manually',
	'{#Seattle,#Python}',
	'{@crisewing,@SeanAzlin2}',
	now(),
	'@CodeFellowsOrg',
	'https://twitter.com/SeanAzlin2/status/481243614211620866',
	'["47.614848","-122.3358423"]',
	'False',
	0);
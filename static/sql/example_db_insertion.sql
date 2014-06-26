﻿INSERT INTO massive (
	tweet_id, 
	text, 
	hashtags, 
	user_mentions, 
	created_at, 
	screen_name, 
	urls, 
	location, 
	inreplytostatusif, 
	retweetcount)
VALUES (
	'testrecordid00',
	'This is a fake tweet inserted into the db manually',
	'{Java,Python}',
	'{crisewing,SeanAzlin2}',
	now(),
	'CodeFellowsOrg',
	'{https://twitter.com/SeanAzlin2/status/481243614211620866}',
	'["47.614848","-122.3358423"]',
	'False',
	0),
	('testrecordid1','This is a fake tweet inserted into the db manually','{Java,Python}','{crisewing,SeanAzlin2}',now(),'crisewing','{https://twitter.com/SeanAzlin2/status/481243614211620866}','["47.614848","-122.3358423"]','False',0),
	('testrecordid2','This is a fake tweet inserted into the db manually','{Python}','{crisewing,SeanAzlin2}',now(),'CodeFellowsOrg','{https://twitter.com/SeanAzlin2/status/481243614211620866}','["47.614848","-122.3358423"]','False',0),
	('testrecordid3','This is a fake tweet inserted into the db manually','{Java,Python}','{crisewing}',now(),'SeanAzlin2','{https://twitter.com/SeanAzlin2/status/481243614211620866}','["47.614848","-122.3358423"]','False',0),
	('testrecordid4','This is a fake tweet inserted into the db manually','{Java,Python}','{crisewing}',now(),'SeanAzlin2','{https://twitter.com/SeanAzlin2/status/481243614211620866}','["47.614848","-122.3358423"]','False',0),
	('testrecordid5','This is a fake tweet inserted into the db manually','{Python}','{crisewing,SeanAzlin2}',now(),'CodeFellowsOrg','{https://twitter.com/SeanAzlin2/status/481243614211620866}','["47.614848","-122.3358423"]','False',0),
	('testrecordid6','This is a fake tweet inserted into the db manually','{CPlusPlus,Python}','{crisewing,SeanAzlin2}',now(),'CodeFellowsOrg','{https://twitter.com/SeanAzlin2/status/481243614211620866}','["47.614848","-122.3358423"]','False',0),
	('testrecordid7','This is a fake tweet inserted into the db manually','{Java,Python}','{SeanAzlin2}',now(),'crisewing','{https://twitter.com/SeanAzlin2/status/481243614211620866}','["47.614848","-122.3358423"]','False',0),
	('testrecordid8','This is a fake tweet inserted into the db manually','{Java,JavaScript}','{crisewing,SeanAzlin2}',now(),'CodeFellowsOrg','{https://twitter.com/SeanAzlin2/status/481243614211620866}','["47.614848","-122.3358423"]','False',0),
	('testrecordid9','This is a fake tweet inserted into the db manually','{Java,Python,Flask}','{}',now(),'CodeFellowsOrg','{https://twitter.com/SeanAzlin2/status/481243614211620866}','["47.614848","-122.3358423"]','False',0);

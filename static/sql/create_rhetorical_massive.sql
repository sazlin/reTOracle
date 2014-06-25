--drop the table if it exists
DROP TABLE IF EXISTS massive;

--create a the table
CREATE TABLE massive
(
  tweet_id text NOT NULL PRIMARY KEY,
  text character(140),
  hashtags text[],
  user_mentions text[],
  created_at date,
  screen_name text,
  url text,
  location json,
  inreplytostatusif text,
  retweetcount smallint
)
WITH (
  OIDS=FALSE
);
ALTER TABLE massive
  OWNER TO codefellow;

DROP TABLE users;
DROP TABLE filters;
DROP TABLE user_filter_join;
DROP TABLE tweets;
DROP TABLE tweet_filter_join;

--create a the table
CREATE TABLE users
(
  screen_name text PRIMARY KEY,
  account_url text[],
  tweet_count smallint,
  last_tweet_timestamp timestamp DEFAULT CURRENT_TIMESTAMP,
  CHECK (tweet_count > 0)
);

CREATE TABLE filters(
  filter_name text PRIMARY KEY,
  last_tweet_timestamp timestamp DEFAULT CURRENT_TIMESTAMP,
  tweet_count smallint
);

CREATE TABLE tweets(
  tweet_id text PRIMARY KEY,
  screen_name text,
  tweet_url text[],
  tweet_text char(280),
  hashtags text[],
  location json,
  retweet_count smallint
);
ALTER TABLE tweets ADD FOREIGN KEY (screen_name) REFERENCES users ON DELETE CASCADE;


CREATE TABLE user_filter_join(
  screen_name text REFERENCES users ON DELETE CASCADE,
  filter_name text REFERENCES filters ON DELETE CASCADE,
  tweet_count smallint CHECK (tweet_count > 0),
  first_tweet_timestamp timestamp DEFAULT CURRENT_TIMESTAMP,
  last_tweet_timestamp timestamp DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (screen_name, filter_name)
);


CREATE TABLE tweet_filter_join
(
  tweet_id text NOT NULL,
  filter_name text NOT NULL,
  CONSTRAINT t_f PRIMARY KEY (tweet_id, filter_name),
  CONSTRAINT filter_name FOREIGN KEY (filter_name)
      REFERENCES filters (filter_name) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT tweet_id FOREIGN KEY (tweet_id)
      REFERENCES tweets (tweet_id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);
ALTER TABLE tweet_filter_join
  OWNER TO reto_tester;

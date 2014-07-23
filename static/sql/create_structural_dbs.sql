DROP TABLE users;
DROP TABLE filters;
DROP TABLE user_filter_join;
DROP TABLE tweets;

--create a the table
CREATE TABLE users
(
  screen_name text PRIMARY KEY,
  account_url text,
  tweet_count smallint,
  last_tweet_timestamp timestamp DEFAULT CURRENT_TIMESTAMP,
  CHECK (tweet_count > 0)
);

CREATE TABLE filters(
  filter_name PRIMARY KEY,
  last_tweet_timestamp timestamp DEFAULT CURRENT_TIMESTAMP,
  tweet_count smallint CHECK (tweet_count > 0)
);

CREATE TABLE tweets(
  tweet_id text PRIMARY KEY,
  screen_name REFERENCES users ON DELETE CASCADE,
  tweet_url text UNIQUE,
  tweet_text text(280),
  hashtags text[],
  location json,
  retweet_count smallint CHECK (retweet_count > 0)
  FOREIGN KEY (screen_name)
);

CREATE TABLE user_filter_join(
  screen_name REFERENCES users ON DELETE CASCADE,
  filter_name REFERENCES filters ON DELETE CASCADE,
  tweet_count smallint CHECK (tweet_count > 0),
  first_tweet_timestamp timestamp DEFAULT CURRENT_TIMESTAMP,
  last_tweet_timestamp timestamp DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (screen_name, filter_name),
  FOREIGN KEY (filter_name),
  FOREIGN KEY (screen_name)
);



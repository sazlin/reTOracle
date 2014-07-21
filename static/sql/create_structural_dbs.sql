DROP TABLE users;
DROP TABLE filters;
DROP TABLE user_filter_join;
DROP TABLE tweets;

--create a the table
CREATE TABLE users
(
  user_id SERIAL PRIMARY KEY,
  screen_name text UNIQUE,
  account_url text,
  total_tweet_count smallint,
  last_tweet_timestamp timestamp DEFAULT CURRENT_TIMESTAMP,
  CHECK (total_tweet_count > 0)
);

CREATE TABLE filters(
  filter_id SERIAL PRIMARY KEY,
  filter_name text,
  last_tweeted_timestamp timestamp DEFAULT CURRENT_TIMESTAMP,
  total_tweet_count smallint CHECK (total_tweet_count > 0)
);

CREATE TABLE tweets(
  tweet_id text PRIMARY KEY,
  tweet_url text UNIQUE,
  tweet_text text,
  retweet_count smallint CHECK (retweet_count > 0)
);

CREATE TABLE user_filter_join(
  user_id REFERENCES users ON DELETE CASCADE,
  filter_id REFERENCES users ON DELETE CASCADE,
  tweet_count smallint CHECK (tweet_count > 0),
  first_tweet_timestamp timestamp DEFAULT CURRENT_TIMESTAMP,
  last_tweet_timestamp timestamp DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id, filter_id)
);

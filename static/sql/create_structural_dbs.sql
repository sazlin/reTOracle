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
  tweet_id text REFERENCES tweets,
  filter_name text REFERENCES filters,
  PRIMARY KEY (tweet_id, filter_name)
);
ALTER TABLE tweet_filter_join ADD FOREIGN KEY (tweet_id) REFERENCES tweets;


CREATE TABLE tweet_sent(
  tweet_id text PRIMARY KEY,
  lr_sent integer,
  lr_neg_prob real,
  lr_pos_prob real,
  lr_exec_time real,
  svm_sent integer,
  svm_neg_prob real,
  svm_pos_prob real,
  svm_exec_time real,
  datumbox_sent integer,
  datumbox_neg_prob real,
  datumbox_pos_prob real,
  datumbox_exec_time real,
  nb_sent integer,
  nb_neg_prob real,
  nb_pos_prob real,
  nb_exec_time real,
  agg_sent integer,
  agg_prob real
);


CREATE TABLE tweet_sentiment(
  tweet_id text PRIMARY KEY,
  "TestScore" real
);
ALTER TABLE tweet_sentiment ADD FOREIGN KEY (tweet_id) REFERENCES tweets;


WITH (
  OIDS=FALSE
);
ALTER TABLE tweet_sentiment
  OWNER TO reto_tester;


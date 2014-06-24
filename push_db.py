import pprint
import time
import json
import psycopg2
import SECRETS
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from header import consumer_key, consumer_secret, access_token, access_token_secret


req_tok_url = 'https://api.twitter.com/oauth/request_token'
oauth_url = 'https://api.twitter.com/oauth/authorize'
acc_tok_url = 'https://api.twitter.com/oauth/access_token'


class StdOutListener(StreamListener):
    """ A listener handles tweets are the received from the stream.
    This is a basic listener that just prints received tweets to stdout.

    """
    def __init__(self):
        self.con = self.connect_db()
        self.cur = self.con.cursor()

    def connect_db(self):
        try:
            connection_string = []
            connection_string.append("host=rhetoracle-db-instance.c2vrlkt9v1tp.us-west-2.rds.amazonaws.com")
            connection_string.append("dbname=rhetorical-db")
            connection_string.append("user=" + SECRETS['DB_USERNAME'])
            connection_string.append("password=" + SECRETS['DB_PASSWORD'])
            return psycopg2.connect(" ".join(connection_string))
        except Exception as x:
            print "Error connecting to DB: ", x.args

    def write_entry(self, sql):
        self.cur.execute(sql)

    def on_data(self, data):

        # load json_data
        json_data = json.loads(data)

        tweet_id = json_data.get('id', None)
        text = json_data.get('text', None)
        hashtags = [i['text'] for i in json_data.get('entities', None).get('hashtags', None)]
        user_mentions = [i['screen_name'] for i in json_data.get('entities', None).get('user_mentions', None)]
        created_at = json_data.get('created_at', None)
        screen_name = json_data.get('user', None).get('screen_name', None)
        url = [i['display_url'] for i in json_data.get('entities', None).get('urls', None)]
        location = json_data.get('geo', None)
        if location:
            location = location.get('coordinates', None)
        if not location:
            location = ''
        in_reply_to_screen_name = json_data.get('in_reply_to_screen_name', None)
        if not in_reply_to_screen_name:
            in_reply_to_screen_name = ''
        retweets = json_data.get('retweet_count', None)

        PUSH_SQL = """
            INSERT INTO massive(
                tweet_id, text, hashtags, user_mentions,
                created_at, screen_name, url, location,
                inreplytostatusif, retweetcount)

            VALUES(
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s);
            """(str(tweet_id), text, hashtags, str(user_mentions), created_at,
                screen_name, str(url), location, in_reply_to_screen_name, retweets)

        # write to database
        try:
            self.write_entry(PUSH_SQL)
        except psycopg2.Error:
            # this will catch any errors generated by the database
            print "Oops there was a DB error!"

    def on_error(self, status):
        error_counter = 0
        if status == 420:
            time.sleep(15)
            print "Made too many requests!"
            print '*' * 20
            error_counter += 1
            print "Errors: ", error_counter

if __name__ == '__main__':
    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    stream = Stream(auth, l)
    stream.filter(track=['Python', 'Seattle'])
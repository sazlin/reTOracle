from filters_json import filter_list as filters
import time
import json
import sys
import os
import sql_queries as sql_q
# from SECRETS import SECRETS
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream


req_tok_url = 'https://api.twitter.com/oauth/request_token'
oauth_url = 'https://api.twitter.com/oauth/authorize'
acc_tok_url = 'https://api.twitter.com/oauth/access_token'


def return_filters():
    filter_list = []
    for i in filters:
        for y in filters[i]['search_terms']:
            for x in filters[i]['search_terms'][y]:
                filter_list.append(x)
    return filter_list


def return_blacklist():
    blackList = []
    for i in filters:
        for y in filters[i]['blacklist']:
            for x in filters[i]['blacklist'][y]:
                blackList.append(x)
    return blackList


class StdOutListener(StreamListener):
    """ A listener handles tweets are the received from the stream.
    This is a basic listener that just prints received tweets to stdout.

    """
    # def __init__(self):
    #     self.conn = self.connect_db()
    #     self.cursor = self.create_cursor()
        # self.commit_count = 0

    # def connect_db(self):
    #     """Try to connect to db, return connection if successful"""
    #     try:
    #         connection_string = []
    #         connection_string.append("host=rhetoracle-db-instance.c2vrlkt9v1tp.us-west-2.rds.amazonaws.com")
    #         connection_string.append("dbname=rhetorical-db")
    #         connection_string.append("user=" + SECRETS['DB_USERNAME'])
    #         connection_string.append("password=" + SECRETS['DB_PASSWORD'])
    #         conn = psycopg2.connect(" ".join(connection_string))
    #     except Exception as x:
    #         print "Error connecting to DB: ", x.args
    #     else:
    #         print "Connection made!"
    #         return conn

    # def get_connection(self):
    #     """get the current connection if it exists, else connect."""
    #     if self.conn is not None:
    #         print "connection exists, so reusing it..."
    #         return self.conn
    #     else:
    #         print "no connection found..."
    #         return self.connect_db()

    # def create_cursor(self):
    #     """create a new cursor and store it"""
    #     conn = self.get_connection()
    #     return conn.cursor()

    # def get_cursor(self):
    #     """get the current cursor if it exist, else create a new cursor"""
    #     if self.cursor is not None:
    #         print "cursor exists, using that..."
    #         return self.cursor
    #     else:
    #         print "Created cursor!"
    #         return self.create_cursor()

    def fix_unicode(self, text):
        # text = ''.join([i if ord(i) < 128 else ' ' for i in text])
        # return text
        return text.encode(encoding='UTF-8')

    def fix_tweet_id(self, tweet_id):
        text = str(tweet_id)
        return self.fix_unicode(text)

    def fix_140(self, text):

        xml_dict = {';': '', '&lt': '<', '&amp': '&', '&gt': '>', '&quot': '"', '&apos': '\''}
        for key, value in xml_dict.iteritems():
            text = text.replace(key, value)
        return text

    def fix_text(self, text):
        text = text.replace("'", "")
        text = self.fix_140(text)
        return self.fix_unicode(text)

    def fix_lists(self, hashtags):
        str1 = '{'
        hashtags = ", ".join(hashtags)
        str1 += hashtags
        str1 += '}'
        return self.fix_unicode(str1)

    def fix_location(self, location):
        location = [str(i) for i in location]
        return str(location).replace("'", "")

    def on_data(self, data):

        # load json_data
        json_data = json.loads(data)
        # pprint.pprint(json_data)

        # pprint.pprint(json_data)
        # need to convert for SQL
        tweet_id = json_data.get('id', None)
        tweet_id = self.fix_tweet_id(tweet_id)

        text = json_data.get('text', None)
        text = self.fix_text(text)

        hashtags = [i['text'] for i in json_data.get('entities', None).get('hashtags', None)]
        hashtags = self.fix_lists(hashtags)

        user_mentions = [i['screen_name'] for i in json_data.get('entities', None).get('user_mentions', None)]
        user_mentions = self.fix_lists(user_mentions)

        created_at = json_data.get('created_at', None)
        screen_name = json_data.get('user', None).get('screen_name', None)

        urls = [i['display_url'] for i in json_data.get('entities', None).get('urls', None)]
        urls = self.fix_lists(urls)

        location = json_data.get('geo', None)
        if location:
            location = location.get('coordinates', None)
            location = self.fix_location(location)
        if not location:
            location = '[]'

        in_reply_to_screen_name = json_data.get('in_reply_to_screen_name', None)

        retweets = json_data.get('retweet_count', None)

        # PUSH_SQL = """
        #     INSERT INTO massive(
        #         tweet_id, text, hashtags, user_mentions,
        #         created_at, screen_name, urls, location,
        #         inreplytostatusif, retweetcount)

        #     VALUES(
        #         '{}', '{}', '{}', '{}', '{}', '{}', '{}',
        #         '{}', '{}', {}); """

        # PUSH_SQL = PUSH_SQL.format(tweet_id, text, hashtags, user_mentions,
        #                            created_at, screen_name, urls, location,
        #                            in_reply_to_screen_name, retweets)

        # try:
            # self.cursor.execute(PUSH_SQL)
        sql_q.get_query_results(
            'save_tweet',
            [tweet_id, text, hashtags, user_mentions,
             created_at, screen_name, urls, location,
             in_reply_to_screen_name, retweets])
        # except psycopg2.Error as x:
        #     # this will catch any errors generated by the database
        #     print "*" * 40
        #     print "Oops there was a DB error!", x.args
        #     self.conn.close()
        #     self.conn = None
        #     time.sleep(10)
        #     while self.conn is None:
        #         self.conn = self.get_connection()
        #         self.cursor = self.create_cursor()
        #         time.sleep(5)

        # else:
        #     self.conn.commit()
            # self.commit_count += 1
            # print "Hashtags: ", hashtags
            # print "User mentions: ", user_mentions
            # print "Committed: ", self.commit_count
            # print "*" * 45

    def on_error(self, status):
        error_counter = 0
        if status == 420:
            time.sleep(15)
            print "Made too many requests!"
            print '*' * 45
            error_counter += 1
            print "Errors: ", error_counter

if __name__ == '__main__':
    sql_q.init()
    auth = None
    if sys.args[1] == 'Prod':
        # app.config['DB_HOST'] = os.environ.get('R_DB_HOST')
        # app.config['DB_NAME'] = os.environ.get('R_DB_NAME')
        # app.config['DB_USERNAME'] = os.environ.get('R_DB_USERNAME')
        # app.config['DB_PASSWORD'] = os.environ.get('R_DB_PASSWORD')
        auth = OAuthHandler(os.environ.get('R_TWITTER_CONSUMER_KEY'),
                                        os.environ.get('R_TWITTER_CONSUMER_SECRET'))
        auth.set_access_token(os.environ.get('R_TWITTER_ACCESS_TOKEN'),
                                         os.environ.get('R_TWITTER_ACCESS_TOKEN_SECRET'))
    elif sys.args[1] == 'Test':
        # app.config['DB_HOST'] = os.environ.get('R_TEST_DB_HOST')
        # app.config['DB_NAME'] = os.environ.get('R_TEST_DB_NAME')
        # app.config['DB_USERNAME'] = os.environ.get('R_TEST_DB_USERNAME')
        # app.config['DB_PASSWORD'] = os.environ.get('R_TEST_DB_PASSWORD')
        auth = OAuthHandler(os.environ.get('R_TEST_TWITTER_CONSUMER_KEY'),
                                        os.environ.get('R_TEST_TWITTER_CONSUMER_SECRET'))
        auth.set_access_token(os.environ.get('R_TEST_TWITTER_ACCESS_TOKEN'),
                                         os.environ.get('R_TEST_TWITTER_ACCESS_TOKEN_SECRET'))

    l = StdOutListener()
    # auth = OAuthHandler(SECRETS['consumer_key'], SECRETS['consumer_secret'])
    # auth.set_access_token(SECRETS['access_token'], SECRETS['access_token_secret'])

    stream_filters = return_filters()
    stream = Stream(auth, l)
    stream.filter(track=stream_filters)

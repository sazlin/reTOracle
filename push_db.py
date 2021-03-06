#!/usr/bin/python

from filters_json import filter_list as filters
import time, datetime
import json
import sys
import os
import sql_queries as sql_q
from filters_json import filter_list
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from logger import make_logger


req_tok_url = 'https://api.twitter.com/oauth/request_token'
oauth_url = 'https://api.twitter.com/oauth/authorize'
acc_tok_url = 'https://api.twitter.com/oauth/access_token'

logger = make_logger('push_db', 'retoracle.log')


def return_filters():
    filter_l = []
    for i in filters:
        for y in filters[i]['search_terms']:
            for x in filters[i]['search_terms'][y]:
                filter_l.append(x)
    return filter_l


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

    def fix_unicode(self, text):
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

        json_data = json.loads(data)

        # need to convert for SQL
        tweet_id = json_data.get('id', None)
        tweet_id = self.fix_tweet_id(tweet_id)

        text = json_data.get('text', None)
        text = self.fix_text(text)

        hashtags1 = [i['text'] for i in json_data.get('entities', None).get('hashtags', None)]
        hashtags = self.fix_lists(hashtags1)

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

        # if screen_name user exists, update its tweet_count number
        # else create a new user
        user_row = sql_q.get_query_results('find_user', [screen_name])
        user_row = json.loads(user_row)
        if user_row:
            tw_count = user_row[0][1]+1
            sql_q.get_query_results( 'update_user_tw_count', [tw_count, screen_name], False)
            sql_q.get_query_results( 'update_user_timestamp', [datetime.datetime.now(), screen_name], False)
        else :
            sql_q.get_query_results(
            'save_users',
            [screen_name, urls, 1, datetime.datetime.now()],
            need_fetch=False)


        # Creating Tweet row
        sql_q.get_query_results(
        'save_tweets',
        [tweet_id, screen_name, urls, text, hashtags, location, retweets],
         need_fetch=False)


        def _update_create_join_table(screen_name, filter_):
            json_result = sql_q.get_query_results('find_join', [screen_name, filter_])
            logger.debug("_u_c_j_t: json_result is: %s", json_result)
            try:
                join_row = json.loads(json_result)
            except Exception as x:
                logger.error("-->Error while doing json.loads() on %s: %s", json_result, x.args)
                return
            else:
                logger.debug("-->Success. Results: %s", join_row)
            if len(join_row) > 0:
                #this user has tweeted about this filter before, so let's increment the existing record
                tw_count = join_row[0][0] + 1
                sql_q.get_query_results('update_join_tw_count', [tw_count, screen_name, filter_], False)
                sql_q.get_query_results( 'update_join_timestamp', [datetime.datetime.now(), screen_name, filter_], False)
            else:
                #this user hasn't tweeted about this filter before, so let's create a new one
                now = datetime.datetime.now()
                logger.debug("-->creating user_filter_join record: %s, %s, %s, %s, %s",
                    screen_name, filter_, 1, now, now )
                sql_q.get_query_results('save_user_filter_join',
                    [screen_name, filter_, 1, now, now], False)

        logger.debug("-->checking hashtags and updating tables")
        for hashtag in hashtags1:
            logger.debug("-->hashtag: %s", hashtag)
            hashtag = '#'+hashtag
            for keyword in filter_list:
                tmp_list = [x.lower() for x in filter_list[keyword]['search_terms']['hashtags']]
                if hashtag.lower() in tmp_list:
                    logger.debug("-->finding filter for %s", keyword)
                    filter_row =  json.loads(sql_q.get_query_results('find_filter', [keyword]))
                    logger.debug("-->filter_row: %s", filter_row)
                    if filter_row :
                        logger.debug("-->old tw_count: %s", filter_row[0][1] )
                        tw_count = filter_row[0][1] + 1
                        logger.debug("-->new tw_count: %s", tw_count)
                        sql_q.get_query_results('update_filter_tw_count', [tw_count, keyword], False)
                        sql_q.get_query_results( 'update_filter_timestamp', [datetime.datetime.now(), keyword], False)
                        sql_q.get_query_results('set_tweet_filter', [tweet_id, keyword], False)
                        _update_create_join_table(screen_name, keyword)
                    else:
                        sql_q.get_query_results( 'save_filters',
                                                [keyword, datetime.datetime.now(), 1], False)
                        sql_q.get_query_results('set_tweet_filter', [tweet_id, keyword], False)
                        _update_create_join_table(screen_name, keyword)



    def on_error(self, status):
        error_counter = 0
        try:
            logger.error('Twitter stream error, status: ', status)
        except TypeError as x:
            logger.error("-->Error logging status of... error...?: %s", x.args)
        if status == 420:
            time.sleep(15)
            error_counter += 1
            logger.info('There have been %d 420 errors', error_counter)


if __name__ == '__main__':
    sql_q.init()
    logger.info('Connected to DB')
    auth = None
    if sys.argv[1] == 'Prod':
        auth = OAuthHandler(os.environ.get('R_TWITTER_CONSUMER_KEY'),
                            os.environ.get('R_TWITTER_CONSUMER_SECRET'))
        auth.set_access_token(os.environ.get('R_TWITTER_ACCESS_TOKEN'),
                              os.environ.get('R_TWITTER_ACCESS_TOKEN_SECRET'))
    elif sys.argv[1] == 'Test':
        auth = OAuthHandler(os.environ.get('R_TEST_TWITTER_CONSUMER_KEY'),
                            os.environ.get('R_TEST_TWITTER_CONSUMER_SECRET'))
        auth.set_access_token(os.environ.get('R_TEST_TWITTER_ACCESS_TOKEN'),
                              os.environ.get('R_TEST_TWITTER_ACCESS_TOKEN_SECRET'))

    l = StdOutListener()
    stream_filters = return_filters()
    stream = Stream(auth, l)
    stream.filter(track=stream_filters)

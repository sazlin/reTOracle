#!/usr/bin/python

from filters_json import filter_list as filters
import time
import json
import sys
import os
import sql_queries as sql_q
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from logger import make_logger


req_tok_url = 'https://api.twitter.com/oauth/request_token'
oauth_url = 'https://api.twitter.com/oauth/authorize'
acc_tok_url = 'https://api.twitter.com/oauth/access_token'

logger = make_logger('push_db', 'retoracle.log')


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

        sql_q.get_query_results(
            'save_tweet',
            [tweet_id, text, hashtags, user_mentions,
             created_at, screen_name, urls, location,
             in_reply_to_screen_name, retweets],
            need_fetch=False)

    def on_error(self, status):
        error_counter = 0
        logger.error('Twitter stream error, status: ', status)
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

import pprint
import time
import json
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

        self.hashtags_count = 0
        self.data_count = 0
        self.seattle_count = 0
        self.python_count = 0

    def on_data(self, data):

        json_data = json.loads(data)

        # pprint.pprint(json_data)
        # print "*"*20
        # print
        # print

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
        in_reply_to_screen_name = json_data.get('in_reply_to_screen_name', None)
        retweets = json_data.get('retweet_count', None)

        if location:
            print "Twitter Name: ", screen_name, type(screen_name)
            print "Tweet ID: ", tweet_id, type(tweet_id)
            print "Hashtags: ", hashtags, type(hashtags)
            print "URLs :", url, type(url)
            print "Text: ", text, type(text)
            print "retweets: ", retweets, type(retweets)
            print "User mentions: ", user_mentions, type(user_mentions)
            print "Created at: ", created_at, type(created_at)
            print "Location: ", location, type(location)
            print "In reply to: ", in_reply_to_screen_name, type(in_reply_to_screen_name)

            if hashtags:
                self.hashtags_count += 1

            if 'Python' in text or 'Python' in hashtags:
                self.python_count += 1

            if 'Seattle' in text or 'Seattle' in hashtags:
                self.seattle_count += 1

            self.data_count += 1

            print '*'*20
            print "Data count: ", self.data_count
            print "Hashtag count: ", self.hashtags_count
            print "Python count: ", self.python_count
            print "Seattle Count: ", self.seattle_count
            print "*"*20

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
    stream.filter(track=['Python', 'Seattle', 'wclittle', 'Plone', 'Flask'])

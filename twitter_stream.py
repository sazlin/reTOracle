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
        # with open('twitter_data.text', 'w') as outfile:
        #     outfile.write(data + '\n')
        # pprint.pprint(json_data)
        user_id = json_data.get('user').get('id', None)
        screen_name = json_data.get('user').get('screen_name', None)
        hashtags = json_data.get('entities').get('hashtags', None)
        text = json_data.get('text', None)
        retweets = json_data.get('retweet_count', None)

        print "Twitter Name: ", screen_name
        print "User ID: ", user_id
        print "Hashtags: ", hashtags
        print "Text: ", text
        print "retweets: ", retweets

        if hashtags:
            self.hashtags_count += 1

        if 'python' in text or 'python' in hashtags:
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
    stream.filter(track=['Python', 'Seattle'])

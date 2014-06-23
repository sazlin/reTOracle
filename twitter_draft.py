import tweepy
import header_rheTOracle as h

call_back_url = 'ec2-54-213-173-105.us-west-2.compute.amazonaws.com'
# auth setup
auth = tweepy.OAuthHandler(h.twit_consumer_key, h.twit_consumer_secret, call_back_url)
auth.set_access_token(h.twit_access_token, h.twit_access_token_secret)

# gets the tweets
api = tweepy.API(auth)
public_tweets = api.home_timeline()
for tweet in public_tweets:
    print tweet.text


# sends a tweet
api = tweepy.API(auth)
api.update_status('tweepy + oadads')

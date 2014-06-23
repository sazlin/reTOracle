mport tweepy

consumer_key = 'qpKACSg7dvOjjvFJ0xLwToSy0'
consumer_secret = 'dnFjr3mf7BljHO9riMKE7Aqg9pH5bNeHhrMlwZkUrNAcorOG5C'
access_token = '2584502599-mTHW7xwBXc582UzhDxCP75S1kNP4wFQdb8CbUqL'
access_token_secret = 'X7xXVvBaNSca3H5ssZ2PrbVmH9jNGFOW0OrzuiiqEGrpD'
call_back_url = 'ec2-54-213-173-105.us-west-2.compute.amazonaws.com'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret, call_back_url)
auth.set_access_token(access_token, access_token_secret)


# get the tweets
api = tweepy.API(auth)
public_tweets = api.home_timeline()
for tweet in public_tweets:
    print tweet.text


# send a tweet
api = tweepy.API(auth)
api.update_status('tweepy + oadads')

import tweepy
import header_rheTOracle as h

call_back_url = 'ec2-54-213-173-105.us-west-2.compute.amazonaws.com'


def make_conn():
    auth = tweepy.OAuthHandler(h.twit_consumer_key, h.twit_consumer_secret, call_back_url)
    auth.set_access_token(h.twit_access_token, h.twit_access_token_secret)
    try:
        redirect_url = auth.get_authorization_url()
    except tweepy.TweepError:
        print 'Error! Failed to get request token.'
    return redirect_url, auth


def search(query, auth):
    # max_tweets = 250
    api = tweepy.API(auth)
    f = open('queryoutput4.html', 'w+')
    for tweet in tweepy.Cursor(api.search, q=query).items():
        f.write(str(tweet) + '\n')


if __name__ == '__main__':
    redirect_url, auth = make_conn()
    search("obama", auth)

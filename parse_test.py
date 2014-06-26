import psycopg2
from SECRETS import SECRETS, json_data


def connect_db():
    try:
        connection_string = []
        connection_string.append("host=rhetoracle-db-instance.c2vrlkt9v1tp.us-west-2.rds.amazonaws.com")
        connection_string.append("dbname=rhetorical-db")
        connection_string.append("user=" + SECRETS['DB_USERNAME'])
        connection_string.append("password=" + SECRETS['DB_PASSWORD'])

        con = psycopg2.connect(" ".join(connection_string))
    except Exception as x:
        print "Error connecting to DB: ", x.args

    else:
        cur = con.cursor()
        return cur, con


def fix_unicode(text):
    # text = ''.join([i if ord(i) < 128 else ' ' for i in text])
    # return text
    return text.encode(encoding='UTF-8')


def fix_tweet_id(tweet_id):
    tweet_id = str(tweet_id)
    return fix_unicode(tweet_id)


def fix_140(text):

    xml_dict = {';': '', '&lt': '<', '&amp': '&', '&gt': '>', '&quot': '"', '&apos': '\''}
    for key, value in xml_dict.iteritems():
        text = text.replace(key, value)
    return text


def fix_text(text):
    text = text.replace("'", "")
    text = fix_140(text)
    return fix_unicode(text)


def fix_lists(hashtags):
    str1 = '{'
    hashtags = ", ".join(hashtags)
    str1 += hashtags
    str1 += '}'
    return fix_unicode(str1)


def fix_location(location):
    location = [str(i) for i in location]
    return str(location).replace("'", "")


def on_data():

        # load json_data
        # json_data = SECRETS.json_data

        # need to convert for SQL
        tweet_id = json_data.get('id', None)
        tweet_id = fix_tweet_id(tweet_id)

        text = json_data.get('text', None)
        text = fix_text(text)

        hashtags = [i['text'] for i in json_data.get('entities', None).get('hashtags', None)]
        hashtags = fix_lists(hashtags)


        user_mentions = [i['screen_name'] for i in json_data.get('entities', None).get('user_mentions', None)]
        user_mentions = fix_lists(user_mentions)

        created_at = json_data.get('created_at', None)
        screen_name = json_data.get('user', None).get('screen_name', None)

        urls = [i['display_url'] for i in json_data.get('entities', None).get('urls', None)]
        urls = fix_lists(urls)
        print urls

        location = json_data.get('geo', None)
        if location:
            location = location.get('coordinates', None)
            location = fix_location(location)
        if not location:
            location = '[]'

        in_reply_to_screen_name = json_data.get('in_reply_to_screen_name', None)

        retweets = json_data.get('retweet_count', None)

        PUSH_SQL = """
            INSERT INTO massive(
                tweet_id, text, hashtags, user_mentions, created_at,
                screen_name, urls, location,
                inreplytostatusif, retweetcount)

            VALUES(
                '{}', '{}', '{}', '{}', '{}', '{}', '{}',
                '{}', '{}', {}); """

        PUSH_SQL = PUSH_SQL.format(tweet_id, text, hashtags, user_mentions,
                                   created_at, screen_name, urls, location,
                                   in_reply_to_screen_name, retweets)

        return PUSH_SQL


if __name__ == "__main__":

    cur, con = connect_db()

    PUSH_SQL = on_data()
    try:
        print PUSH_SQL
        cur.execute(PUSH_SQL)
    except psycopg2.Error as x:
        # this will catch any errors generated by the database
        print "Oops there was a DB error!", x.args
    else:
        print "Commit!"
        con.commit()

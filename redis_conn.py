import redis
import psycopg2
from SECRETS import SECRETS

sql_query = {
    u"type1": """
SELECT hashtag, COUNT(hashtag) as HashTagCount
FROM (SELECT screen_name, unnest(hashtags) as hashtag FROM massive) as subquery
WHERE
hashtag = 'Java' OR
hashtag = 'Python' OR
hashtag = 'Ruby'
GROUP BY hashtag
ORDER BY HashTagCount DESC
""",
    'type2': """
 SELECT screen_name, COUNT(screen_name) as TweetCount
FROM massive
WHERE '#Seattle' = ANY (hashtags)
GROUP BY screen_name
""",
    'type3': """
SELECT screen_name, COUNT(screen_name) as TweetCount
FROM massive
WHERE '#Seattle' = ANY (hashtags)
GROUP BY screen_name
""",
    'type4': """
 SELECT screen_name, COUNT(screen_name) as TweetCount
FROM massive
WHERE '#Seattle' = ANY (hashtags)
GROUP BY screen_name
"""
}

POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)
interest_list = {'type1Java': [], "type3Python": [], 'type4Ruby': []}

# x = "('Python', 60L) ('Ruby', 44L) ('Java', 9L)"


def convert_results_list(result_str):
    return re.findall('\([^)]*\)', result_str)


def get_redis_query(key):
    r_server = redis.Redis(connection_pool=POOL)
    return r_server.get(key)


def set_to_redis(key, value):
    r_server = redis.Redis(connection_pool=POOL)
    r_server.set(key, value)


def add_search(key, q_type):
    print u"add_search started"
    my_key = str(q_type)+str(key)
    if my_key not in interest_list.keys() and interest_list.get(my_key):
        # yay , search is in the redis!
        return get_redis_query(my_key)
    if my_key not in interest_list:
        interest_list[my_key] = []
    else:
        # this is the worst time to search for this key
        print u"why are you searching same thing"


def parse_key(key):
    return key[:5], key[5:]


def maint_redis():
    conn = db_connection()
    cur = conn.cursor()

    for my_key in interest_list.keys():
        q_type, key = parse_key(my_key)
        json_result = []
        q_type = str(q_type)
        cur.execute(sql_query.get(q_type))
        json_result = cur.fetchall()
        key_value = ''
        for item in json_result:
            key_value += str(item)+" "
        print key_value
        set_to_redis(my_key, key_value)


def db_connection():
    DB_HOST = "rhetoracle-db-instance.c2vrlkt9v1tp.us-west-2.rds.amazonaws.com"
    DB_NAME = "rhetorical-db"
    DB_USERNAME = SECRETS['DB_USERNAME']
    DB_PASSWORD = SECRETS['DB_PASSWORD']

    connection_string = []
    connection_string.append("host=" + DB_HOST)
    connection_string.append("dbname=" + DB_NAME)
    connection_string.append("user=" + DB_USERNAME)
    connection_string.append("password=" + DB_PASSWORD)
    connection_str = " ".join(connection_string)

    try:
        print "establishing a new connection..."
        conn = psycopg2.connect(connection_str)
    except Exception as x:
        print "Error connecting to DB: ", x.args
    print "Connection established and stored..."
    return conn


"""
def connect_db():
    try:
        connection_string = []
        connection_string.append("host=rhetoracle-db-instance.c2vrlkt9v1tp.us-west-2.rds.amazonaws.com")
        connection_string.append("dbname=rhetorical-db")
        connection_string.append("user=" + "codefellow")
        connection_string.append("password=" + "teamawesome1!")
    except Exception as x:
        print "Error connecting to DB: ", x.args
    conn = psycopg2.connect(" ".join(connection_string))

1 - Her search yapildiginda
A. time_stamp i kontrol et.
    Eger time_stamp  bizim time_stample
A. search yapilan bilgiyi redis-servera ata
2 - Her search yapildiginda get_redis i calistir ve bilgileri getir
3 - her 5 dakikada bir db yi tara ve zaman kisitlamasina gore
        redis_server i guncelle
4 - No3 icin gevent olustur ve arkada redisi calistir

"""

# remove all out-dated keys from dictionary
# add new keys in tmp_interest_list to dictionary
# seek for new datas for my keys in interest list
# check time stamp and add them to the dict
# call this method in rheTOracle.py main

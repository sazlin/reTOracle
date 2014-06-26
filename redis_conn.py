import redis
import psycopg2
import re
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


def convert_results(result_str):
    r = re.findall('\([^)]*\)', result_str)
    l = []
    for item in r:
        t1 = re.findall('\'[^)]*\'', item)
        t2 = re.findall(' [^)]*\)', item)
        l.append((t1[0][1:-1], t2[0][1:-1]))
    return l


def get_redis_query(key):
    r_server = redis.Redis(connection_pool=POOL)
    return convert_results(r_server.get(key))


def set_to_redis(key, value):
    r_server = redis.Redis(connection_pool=POOL)
    r_server.set(key, value)


def add_search(key, q_type):
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
        key_value = ""
        for item in json_result:
            key_value += str(item)
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

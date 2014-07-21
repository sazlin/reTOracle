<<<<<<< HEAD
#!/usr/bin/python

import redis
import os
import sql_queries as sql_q
from logger import make_logger

POOL = None
logger = make_logger('redis_con', 'retoracle.log')


def init_pool():
    global POOL  # HACK, fix later
    r_config = os.environ.get('R_CONFIG')
    if r_config == 'Prod':
        logger.info("REDIS: Using Prod Redis Service")
        POOL = redis.ConnectionPool(host=os.environ.get('R_REDIS_ENDPOINT'), port=6379, db=0)
    elif r_config == 'Test':
        logger.info("REDIS: Using Test Redis Service")
        POOL = redis.ConnectionPool(host=os.environ.get('R_TEST_REDIS_ENDPOINT'), port=6379, db=0)
    else:
        raise Exception('R_CONFIG not set.')
        logger.error('R_CONFIG not set properly', exc_info=True)


def get_redis_query(q_type):
    if not POOL:
        raise Exception('POOL not initiated. Call init_pool().')
    r_server = redis.Redis(connection_pool=POOL)
    if q_type in sql_q.QUERY_STRINGS:
        json_list = r_server.get(q_type)
        return json_list
    else:
        raise ValueError("q_type not in REDIS")
        logger.error('Requested query not in REDIS', exc_info=True)


def _set_to_redis(key, value):
    if not POOL:
        raise Exception('POOL not initiated. Call init_pool().')
    logger.info('getting r_server')
    r_server = redis.Redis(connection_pool=POOL)
    logger.info("setting key value on redis: %s = %s", key, value)
    r_server.set(key, value)
    logger.info('done')


def maint_redis():
    if not POOL:
        raise Exception('POOL not initiated. Call init_pool().')
    for key in sql_q.QUERY_STRINGS.iterkeys():
        # HACK - we don't want to redo 'save_tweet'
        if not key == 'save_tweet':
            logger.info("Redis: Querying SQL and getting results...")
            result = None
            try:
                result = sql_q.get_query_results(key)
            except Exception as x:
                logger.error("Redis: something went wrong getting results for %s : %s", key, x.args, exc_info=True)
            if result is None:
                raise Exception("REDIS: SQL Query result is None for %s ", key, exc_info=True)
                logger.error("SQL query result is none for %s", key, exc_info=True)
            else:
                logger.info("Redis: Settings query results in redis for %s", key)
                try:
                    _set_to_redis(key, result)
                except Exception as x:
                    logger.error("Redis: Something went wrong while setting k,v pair on redis: %S ", x.args, exc_info=True)
                else:
                    logger.info('Redis: [SUCCESS] results set for %s ', key)
=======
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
        print "json_result", json_result
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
>>>>>>> 6d4040e70dd964c6b037ec30067fe8d3b46b62fe

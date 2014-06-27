import redis
import psycopg2
import re
from SECRETS import SECRETS
import sql_queries as sql_q

POOL = redis.ConnectionPool(host='redis-cluster.8uzvxq.0001.usw2.cache.amazonaws.com', port=6379)
interest_list = {'type1': sql_q.build_q1_querystring(), "type2": sql_q.build_q2_querystring()}

# x = "('Python', 60L) ('Ruby', 44L) ('Java', 9L)"


def convert_results(result_str):
    r = re.findall('\([^)]*\)', result_str)
    l = []
    for item in r:
        t1 = re.findall('\'[^)]*\'', item)
        t2 = re.findall(' [^)]*\)', item)
        l.append((t1[0][1:-1], t2[0][1:-1]))
    return l


def get_redis_query(q_type):
    r_server = redis.Redis(connection_pool=POOL)
    return convert_results(r_server.get(q_type))


def set_to_redis(key, value):
    r_server = redis.Redis(connection_pool=POOL)
    r_server.set(key, value)


def maint_redis():
    conn = db_connection()
    cur = conn.cursor()

    for key, value in interest_list.iteritems():
        cur.execute(value)
        json_result = cur.fetchall()
        key_value = ""
        for item in json_result:
            key_value += str(item)
        set_to_redis(key, key_value)


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

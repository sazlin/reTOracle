import redis
import os
#import re
#from SECRETS import SECRETS
import sql_queries as sql_q
# POOL = redis.ConnectionPool(host='127.0.0.1', port=6379)
# interest_list = {'type1': sql_q.build_q1_querystring(), "type2": sql_q.build_q2_querystring(),
#                       'type3': sql_q.build_q3_querystring()}

# x = "('Python', 60L) ('Ruby', 44L) ('Java', 9L)"


# def convert_results_type1(result_str):
#     r = re.findall('\([^)]*\)', result_str)
#     l = []
#     print result_str
#     for item in r:
#         end = len(item)
#         f_index = item.index('\'', 0, end)
#         n_index = item.index('\'', f_index+1, end)
#         f1_index = item.index(',', n_index+1, end)
#         n1_index = item.index(')', f1_index+1, end)
#         l1 = []
#         l1.append(item[f_index+1: n_index])
#         l1.append(int(item[f1_index+2: n1_index-1]))
#         l.append(l1)
#     return l


# def convert_results_type2(result_str):
#     r = re.findall('\([^)]*\)', result_str)
#     l = []
#     print result_str
#     for item in r:
#         end = len(item)
#         f_index = item.index('\'', 0, end)
#         n_index = item.index('\'', f_index+1, end)
#         f1_index = item.index(',', n_index+1, end)
#         n1_index = item.index(',', f1_index+1, end)
#         f2_index = item.index('\'', n1_index+1, end)
#         n2_index = item.index('\'', f2_index+1, end)
#         l1 = []
#         l1.append(item[f_index+1: n_index])
#         l1.append(int(item[f1_index+2: n1_index-1]))
#         l1.append(item[f2_index+1: n2_index])
#         l.append(l1)
#     return l
POOL = None
def init_pool():
    global POOL  # HACK, fix later
    r_config = os.environ.get('R_CONFIG')
    if r_config == 'Prod':
        print "REDIS: Using Prod Redis Service"
        POOL = redis.ConnectionPool(host=os.environ.get('R_REDIS_ENDPOINT'), port=6379, db=0)
    elif r_config == 'Test':
        print "REDIS: Using Test Redis Service"
        POOL = redis.ConnectionPool(host=os.environ.get('R_TEST_REDIS_ENDPOINT'), port=6379,  db=0)
    else:
        raise Exception('R_CONFIG not set.')


def get_redis_query(q_type):
    if not POOL:
        raise Exception('POOL not initiated. Call init_pool().')
    r_server = redis.Redis(connection_pool=POOL)
    if q_type in sql_q.QUERY_STRINGS:
        json_list = r_server.get(q_type)
        return json_list
    else:
        raise ValueError("q_type not in REDIS")


def _set_to_redis(key, value):
    if not POOL:
        raise Exception('POOL not initiated. Call init_pool().')
    print "getting r_server..."
    r_server = redis.Redis(connection_pool=POOL)
    print "setting key value on redis:", key,"=", value
    r_server.set(key, value)
    print "done"


def maint_redis():
    if not POOL:
        raise Exception('POOL not initiated. Call init_pool().')
    for key in sql_q.QUERY_STRINGS.iterkeys():
        # HACK - we don't want to redo 'save_tweet'
        if not key == 'save_tweet':
            print "Redis: Querying Sql and getting results..."
            result = None
            try:
                result = sql_q.get_query_results(key)
            except Exception as x:
                print "Redis: something went wrong getting results for ", key, ": ", x.args
            if result is None:
                raise Exception("REDIS: SQL Query result is None for ", key)
            else:
                print "Redis: Settings query results in redis for ", key
                try:
                    # if not isinstance(result, basestring):
                    #     raise Exception('ERROR: result is not a string')
                    _set_to_redis(key, result)
                except Exception as x:
                    print "Redis: Something went wrong while setting k,v pair on redis: ", x.args
                else:
                    print 'Redis: [SUCCESS] results set for ', key
# def maint_redis():
#     conn = db_connection()
#     cur = conn.cursor()

#     for key, value in interest_list.iteritems():
#         try:
#             cur.execute(value)
#             json_result = cur.fetchall()
#             key_value = ""
#             for item in json_result:
#                 key_value += str(item)
#             _set_to_redis(key, key_value)
#         except Exception as x:
#             print "Redis->SQL: Something went wrong!: ", x.args


# def db_connection():
#     DB_HOST = "rhetoracle-db-instance.c2vrlkt9v1tp.us-west-2.rds.amazonaws.com"
#     DB_NAME = "rhetorical-db"
#     DB_USERNAME = SECRETS['DB_USERNAME']
#     DB_PASSWORD = SECRETS['DB_PASSWORD']

#     connection_string = []
#     connection_string.append("host=" + DB_HOST)
#     connection_string.append("dbname=" + DB_NAME)
#     connection_string.append("user=" + DB_USERNAME)
#     connection_string.append("password=" + DB_PASSWORD)
#     connection_str = " ".join(connection_string)

#     try:
#         print "establishing a new connection..."
#         conn = psycopg2.connect(connection_str)
#     except Exception as x:
#         print "Error connecting to DB: ", x.args
#     print "Connection established and stored..."
#     return conn

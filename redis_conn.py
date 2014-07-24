import redis
import os
import sql_queries as sql_q

POOL = None


def init_pool():
    global POOL # HACK, fix later
    r_config = os.environ.get('R_CONFIG')
    if r_config == 'Prod':
        #logger.info("REDIS: Using Prod Redis Service")
        POOL = redis.ConnectionPool(host=os.environ.get('R_REDIS_ENDPOINT'), port=6379, db=0)
    elif r_config == 'Test':
        #logger.info("REDIS: Using Test Redis Service")
        POOL = redis.ConnectionPool(host=os.environ.get('R_TEST_REDIS_ENDPOINT'), port=6379, db=0)
    elif r_config == 'Local':
        print "REDIS: Using Local Redis Service"
        POOL = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0)
    else:
        #logger.error('R_CONFIG not set properly', exc_info=True)
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
    print "setting key value on redis:", key, "=", value
    r_server.set(key, value)
    print "done"


def maint_redis():
    if not POOL:
        raise Exception('POOL not initiated. Call init_pool().')
    for key in sql_q.QUERY_STRINGS.iterkeys():
        if key[:5] != 'fetch' :
            continue
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
                _set_to_redis(key, result)
            except Exception as x:
                print "Redis: Something went wrong while setting k,v pair on redis: ", x.args
            else:
                print 'Redis: [SUCCESS] results set for ', key




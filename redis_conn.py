#!/usr/bin/python

import redis
import os
import sql_queries as sql_q
from logger import make_logger
import inspect


logger = make_logger(inspect.stack()[0][1], 'retoracle.log')
POOL = None


def init_pool():
    global POOL  # HACK, fix later
    r_config = os.environ.get('R_CONFIG')
    if r_config == 'Prod':
        logger.info("REDIS: Using Prod Redis Service")
        POOL = redis.ConnectionPool(host=os.environ.get('R_REDIS_ENDPOINT'), port=6379, db=0)
    elif r_config == 'Test':
        logger.info("REDIS: Using Test Redis Service")
        POOL = redis.ConnectionPool(host=os.environ.get('R_TEST_REDIS_ENDPOINT'), port=6379, db=0)
    elif r_config == 'Local':
        print "REDIS: Using Local Redis Service"
        POOL = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0)
    else:
        logger.error('R_CONFIG not set properly', exc_info=True)
        raise Exception('R_CONFIG not set.')
        logger.error('R_CONFIG not set properly')


def get_redis_query(q_type):
    if not POOL:
        raise Exception('POOL not initiated. Call init_pool().')
    r_server = redis.Redis(connection_pool=POOL)
    if q_type in sql_q.QUERY_STRINGS:
        json_list = r_server.get(q_type)
        return json_list
    else:
        logger.error('Requested query not in REDIS', exc_info=True)
        raise ValueError("q_type not in REDIS")


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

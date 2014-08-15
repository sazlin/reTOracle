#!/usr/bin/python

import redis
import os
import sql_queries as sql_q
from logger import make_logger
import inspect


logger = make_logger(inspect.stack()[0][1], 'retoracle.log')
POOL = None
TTL = 5  # How long to cache SQL results for before expiring them


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


def get_redis_query(query):
    global POOL
    global TTL

    # make sure this is a valid query for reTOracle...
    if query not in sql_q.QUERY_STRINGS:
        logger.error('REDIS: query not in sql_q.QUERY_STRINGS')
        return

    # make sure we can work against redis
    if not POOL:
        raise Exception('POOL not initiated. Call init_pool().')
    r_server = redis.Redis(connection_pool=POOL)

    # return the cached value if it exists. If it doesn't then
    # query SQL and cache the result
    logger.debug("REDIS: Getting values from redis for %s", query)
    cached_results = r_server.get(query)
    pttl = r_server.pttl(query)
    if cached_results and pttl > 0:
        logger.debug("REDIS: Got cached value for %s", query)
        return cached_results
    else:
        # result not cached (or no TTL set), so hit sql and cache the result w/ TTL
        try:
            result = sql_q.get_query_results(query)
        except Exception as x:
            logger.error("REDIS: something went wrong getting sql results for %s: %s", query, x.args, exc_info=True)
        if result is None:
            logger.error("REDIS: SQL query result is none for %s", query, exc_info=True)
            return
        logger.info("REDIS: Settings query results in redis for %s", query)
        try:
            if(isinstance(result, basestring)):
                r_server.set(query, result)
            else:
                r_server.set(query, result[0])
            r_server.expire(query, TTL)
            logger.info('Redis: [SUCCESS] results set for %s ', query)
            logger.debug('-->Results are: %s', result)
        except Exception as x:
            logger.error("Redis: Something went wrong while setting k,v pair on redis: %s ", x.args, exc_info=True)
        return result

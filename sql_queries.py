import os
import psycopg2
import json
import time
from filters_json import filter_list as FilterMap

QUERY_STRINGS = {}
DB_CONFIG = {}


def init():
    _init_db_config()
    _build_query_strings()


def _build_connection_string():
    connection_string = []
    connection_string.append("host=" + DB_CONFIG['DB_HOST'])
    connection_string.append("dbname=" + DB_CONFIG['DB_NAME'])
    connection_string.append("user=" + DB_CONFIG['DB_USERNAME'])
    connection_string.append("password=" + DB_CONFIG['DB_PASSWORD'])
    return " ".join(connection_string)


def _init_db_config():
    r_config = os.environ.get('R_CONFIG')
    if r_config == 'Prod':
        DB_CONFIG['DB_HOST'] = os.environ.get('R_DB_HOST')
        DB_CONFIG['DB_NAME'] = os.environ.get('R_DB_NAME')
        DB_CONFIG['DB_USERNAME'] = os.environ.get('R_DB_USERNAME')
        DB_CONFIG['DB_PASSWORD'] = os.environ.get('R_DB_PASSWORD')
    elif r_config == 'Test' or r_config == 'Local':
        DB_CONFIG['DB_HOST'] = os.environ.get('R_TEST_DB_HOST')
        DB_CONFIG['DB_NAME'] = os.environ.get('R_TEST_DB_NAME')
        DB_CONFIG['DB_USERNAME'] = os.environ.get('R_TEST_DB_USERNAME')
        DB_CONFIG['DB_PASSWORD'] = os.environ.get('R_TEST_DB_PASSWORD')
    else:
        raise Exception("R_CONFIG not set.")

    DB_CONFIG['DB_CONNECTION_STRING'] = _build_connection_string()


def _build_query_strings():
    QUERY_STRINGS['ticker1'] = _build_q3_query()
    QUERY_STRINGS['geomap1'] = _build_q4_query()

    QUERY_STRINGS['save_tweets']= _save_tweets()
    QUERY_STRINGS['save_filters'] = _save_filters()
    QUERY_STRINGS['save_users'] = _save_users()
    QUERY_STRINGS['save_user_filter_join'] = save_user_filter_join()
    QUERY_STRINGS['find_user'] = _find_user()
    QUERY_STRINGS['find_filter'] = _find_filter()
    QUERY_STRINGS['find_join'] = _find_join()
    QUERY_STRINGS['update_user_tw_count'] = _update_user_tweet_count()
    QUERY_STRINGS['update_filter_tw_count'] = _update_filter_tweet_count()
    QUERY_STRINGS['update_join_tw_count'] = _update_join_tweet_count()
    QUERY_STRINGS['update_user_timestamp'] = _update_user_timestamp()
    QUERY_STRINGS['update_filter_timestamp'] = _update_filter_timestamp()
    QUERY_STRINGS['update_join_timestamp'] = _update_join_timestamp()
    QUERY_STRINGS['fetch_filter_tw_counts'] = _query_filter_tweets_counts()
    QUERY_STRINGS['fetch_popular_users'] = _query_popular_users()


def _connect_db():
    try:
        print "establishing a new connection..."
        conn = psycopg2.connect(DB_CONFIG['DB_CONNECTION_STRING'])
    except Exception as x:
        raise Exception("Error connecting to DB: " + str(x.args))
    print "Connection established and stored..."
    DB_CONFIG['DB_CONNECTION'] = conn
    return conn


def _get_connection():
    """get the current connection if it exists, else connect."""
    conn = DB_CONFIG.get('DB_CONNECTION')
    if conn is not None:
        print "connection exists, so reusing it..."
        return conn
    else:
        print "no connection found..."
        return _connect_db()


def _create_cursor():
    """create a new cursor and store it"""
    conn = _get_connection()
    print "creating new cursor..."
    DB_CONFIG['DB_CURSOR'] = conn.cursor()
    print "got new cursor."
    return DB_CONFIG['DB_CURSOR']


def _get_cursor():
    """get the current cursor if it exist, else create a new cursor"""
    cur = DB_CONFIG.get('DB_CURSOR')
    if cur is not None:
        print "cursor exists, using that..."
        return cur
    else:
        print "no cursor found, so creating one..."
        return _create_cursor()


def _execute_query(sql, args=None, need_fetch=True):
    """execute the passed in SQL using the current cursor.
    If the query string takes any args pass those to the cursor as well."""
    try:
        print "getting cursor..."
        cur = _get_cursor()
        print "executing the following on cursor:"
        print "SQL STRING: {}".format(sql)
        print "SQL ARGS: {}".format(args)
        cur.execute(sql, args)
        if need_fetch:
            print "Getting results..."
            results = cur.fetchall()
            print results
            print "Got results..."
            try:
                json_results = json.dumps(results)
            except Exception as x:
                print "Error dumping json for: ", results, " Args: ", x.args
            else:
                return json_results
    except psycopg2.Error as x:
        # this will catch any errors generated by the database
        print "*" * 40
        print "Error execuring query against DB: ", x.args
        print "Attempting to reconnect to the DB..."
        DB_CONFIG['DB_CONNECTION'].close()
        DB_CONFIG['DB_CONNECTION'] = None
        DB_CONFIG['DB_CURSOR'] = None
        time.sleep(5)
        conn = _get_connection()
        while conn is None:
            conn = _get_connection()
            time.sleep(5)
    else:
        DB_CONFIG['DB_CONNECTION'].commit()
    return None


def _build_q3_query():
    sql = """
    SELECT screen_name, text FROM massive
    ORDER BY tweet_id DESC
    LIMIT 1;
    """
    return (sql, None)


def _build_q4_query():
    sql = []
    sql.append("""SELECT tweet_id, text, screen_name, location FROM massive""")
    sql.append("""WHERE json_array_length(location) <> 0""")
    sql.append("""ORDER BY tweet_id DESC LIMIT 1""")
    return (" ".join(sql), None)



# New db structure queries
def _find_user():
    sql = ("""SELECT screen_name, tweet_count FROM users WHERE screen_name = %s """)
    return sql

def _find_filter():
    sql = ("""SELECT filter_name, tweet_count FROM filters WHERE filter_name = %s """)
    return sql

def _find_join():
    sql = []
    sql.append("""SELECT tweet_count FROM user_filter_join""")
    sql.append("""WHERE screen_name = %s AND filter_name = %s""")
    return " ".join(sql)


def _update_user_tweet_count():
    sql = ("""UPDATE users SET tweet_count = %s WHERE screen_name = %s;""")
    return sql

def _update_user_timestamp():
    sql = ("""UPDATE users SET last_tweet_timestamp = %s WHERE screen_name = %s;""")
    return sql

def _update_filter_tweet_count():
    sql = ("""UPDATE filters SET tweet_count = %s WHERE filter_name = %s;""")
    return sql

def _update_filter_timestamp():
    sql = ("""UPDATE filters SET last_tweet_timestamp = %s WHERE filter_name = %s;""")
    return sql

def _update_join_tweet_count():
    sql = []
    sql .append("""UPDATE user_filter_join SET tweet_count = %s """)
    sql.append("""WHERE screen_name = %s AND filter_name = %s""")
    return " ".join(sql)

def _update_join_timestamp():
    sql = []
    sql.append("""UPDATE user_filter_join SET last_tweet_timestamp = %s""")
    sql.append("""WHERE screen_name = %s AND filter_name = %s""")
    return " ".join(sql)


def _query_filter_tweets_counts():
    sql = ("""SELECT filter_name, tweet_count FROM filters ORDER BY tweet_count DESC;""")
    return sql

def _query_popular_users():
    final_result = []
    sql1_result = _execute_query("""SELECT filter_name FROM filters ORDER BY tweet_count DESC""")
    sql1_result = json.loads(sql1_result)
    for filter_ in sql1_result:
        tmp_sql = []
        tmp_sql.append("""SELECT filter_name, tweet_count, screen_name FROM  user_filter_join""")
        tmp_sql.append("""WHERE filter_name = %s ORDER BY tweet_count DESC LIMIT 1""")
        json_result = _execute_query(" ".join(tmp_sql), [filter_[0]])
        json_result = json.loads(json_result)
        final_result.append(json_result[0])
    return json.dumps(final_result)


def _save_tweets():
    return ("""
            INSERT INTO tweets(
                tweet_id, screen_name, tweet_url, tweet_text, hashtags, location, retweet_count)

            VALUES(
                %s, %s, %s, %s, %s, %s, %s); """)

def _save_users():
    return("""INSERT INTO users (screen_name, account_url,
                                tweet_count, last_tweet_timestamp)
                 VALUES (%s, %s, %s, %s); """)

def _save_filters():
    return ("""INSERT INTO filters( filter_name,
                                                last_tweet_timestamp,
                                                tweet_count)
                   VALUES (%s, %s, %s); """)

def save_user_filter_join():
    return ("""INSERT INTO user_filter_join( screen_name,
                                                filter_name,
                                                tweet_count,
                                                first_tweet_timestamp,
                                                last_tweet_timestamp)
                   VALUES (%s, %s, %s, %s, %s); """)



def get_query_results(chart_string, args=None, need_fetch=True):
    if args is None:
        args = QUERY_STRINGS[chart_string][1]
    if chart_string == 'fetch_popular_users':
        return _query_popular_users()
    return _execute_query(
        QUERY_STRINGS[chart_string],
        args,
        need_fetch)

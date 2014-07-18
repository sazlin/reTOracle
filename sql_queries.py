import os
import psycopg2
import json
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
    DB_CONFIG['DB_HOST'] = os.environ.get('R_DB_HOST')
    DB_CONFIG['DB_NAME'] = os.environ.get('R_DB_NAME')
    DB_CONFIG['DB_USERNAME'] = os.environ.get('R_DB_USERNAME')
    DB_CONFIG['DB_PASSWORD'] = os.environ.get('R_DB_PASSWORD')
    DB_CONFIG['DB_CONNECTION_STRING'] = _build_connection_string()


def _build_query_strings():
    QUERY_STRINGS['chart1'] = _build_q1_query()
    QUERY_STRINGS['chart2'] = _build_q2_query()
    QUERY_STRINGS['ticker1'] = _build_q3_query()
    QUERY_STRINGS['geomap1'] = _build_q4_query()
    QUERY_STRINGS['save_tweet'] = _build_save_tweet_sql()


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


def _execute_query(sql, args=None):
    """execute the passed in SQL using the current cursor.
    If the query string takes any args pass those to the cursor as well."""
    # print "executing query..."
    try:
        cur = _get_cursor()
    except Exception as x:
        print "Error getting cursor: ", x.args
    #print "got cursor..."
    try:
        print "executing the following on cursor:"
        print "SQL STRING: {}".format(sql)
        print "SQL ARGS: {}".format(args)
        cur.execute(sql, args)
        print "Getting results..."
        results = cur.fetchall()
        print "Got results..."
    except Exception as x:
        print "Error executing sql on cursor: ", x.args
    else:
        print "query success!"
    try:
        json_results = json.dumps(results)
        print "json results: ", json_results
    except Exception as x:
        print "Error dumping json: ", json_results
    else:
        return json_results

    return None


def _build_q1_query():
    """build a query string for Q1 using FilterMap"""
    sql = []
    args = []
    sql.append("""SELECT hashtag, COUNT(hashtag) as HashTagCount""")
    sql.append("""FROM (SELECT screen_name, unnest(hashtags) as hashtag FROM massive) as subquery""")
    sql.append("""WHERE""")
    for language in FilterMap:
        search_terms = FilterMap[language]['search_terms']
        for hashtag in search_terms['hashtags']:
            sql.append("""hashtag = '%s' """)
            args.append(hashtag[1:])
            sql.append("""OR""")
    sql.pop()  # discard last OR statement
    sql.append("""GROUP BY hashtag""")
    sql.append("""ORDER BY HashTagCount DESC""")
    return (" \r\n".join(sql), args)


def _build_q2_query():
    """build a query string for Q2 using FilterMap"""
    sql = []
    args = []
    sql.append("""SELECT hashtag, HashTagCount, screen_name""")
    sql.append("""FROM (SELECT hashtag, screen_name, HashTagCount, rank() OVER (PARTITION BY hashtag ORDER BY HashTagCount DESC, screen_name) AS pos""")
    sql.append("""FROM (SELECT hashtag, screen_name, COUNT(hashtag) as HashTagCount""")
    sql.append("""FROM (SELECT screen_name, unnest(hashtags) as hashtag FROM massive) as unwrap""")
    sql.append("""WHERE""")
    for language in FilterMap:
        search_terms = FilterMap[language]['search_terms']
        for hashtag in search_terms['hashtags']:
            sql.append("""hashtag = '%s' """)
            args.append(hashtag[1:])
            sql.append("""OR""")
    sql.pop()  # discard last OR statement
    sql.append("""GROUP BY screen_name, hashtag""")
    sql.append("""ORDER BY hashtag, HashTagCount DESC""")
    sql.append(""") as countedhashtags""")
    sql.append(""") as ss""")
    sql.append("""WHERE pos = 1""")
    sql.append("""ORDER BY hashtag, HashTagCount DESC""")
    return (" \r\n".join(sql), args)


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


def _build_save_tweet_sql():
    return ("""
            INSERT INTO massive(
                tweet_id, text, hashtags, user_mentions,
                created_at, screen_name, urls, location,
                inreplytostatusif, retweetcount)

            VALUES(
                '%s', '%s', '%s', '%s', '%s', '%s', '%s',
                '%s', '%s', %s); """, [])


def save_tweet_to_sql(**tweet_args):
    QUERY_STRINGS['save_tweet'][1].
    return _execute_query(
        QUERY_STRINGS['save_tweet'][0],
        QUERY_STRINGS['save_tweet'][1])
        PUSH_SQL = PUSH_SQL.format(tweet_id, text, hashtags, user_mentions,
                                   created_at, screen_name, urls, location,
                                   in_reply_to_screen_name, retweets)

def get_query_results(chart_string):
    return _execute_query(
        QUERY_STRINGS[chart_string][0],
        QUERY_STRINGS[chart_string][1])

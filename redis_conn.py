import redis
import psycopg2

sql_query = {
    'type1': """
SELECT screen_name, COUNT(screen_name) as TweetCount
FROM massive
WHERE '#Seattle' = ANY (hashtags)
GROUP BY screen_name
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

POOL = redis.ConnectionPool(host='localhost', port=2000, db=0)
interest_list = {}
"""
Who is talking about #q1_what
What is @q2_who talking about
Who is talking about @q3_who
Who is @q4_who talking about
"""
"""
interest _list is a dictionary.
"""


def get_redis_query(key):
    r_server = redis.Redis(connection_pool=POOL)
    return r_server.get(key)


def set_to_redis(key, value):
    r_server = redis.Redis(connection_pool=POOL)
    r_server.set(key, value)


def add_search(key, q_type):
    my_key = str(q_type)+str(key)
    if my_key not in interest_list.keys():
        # it's Sean's turn :)
        return None
    if interest_list.get(my_key):
        return get_redis_query(my_key)
    interest_list[my_key] = []


def parse_key(key):
    return key[:5], key[5:]


def is_key_outdated(conn, my_key):
    q_type, key = parse_key(my_key)
    try:
        cur = conn.cursor()
    except Exception as x:
        print "Error connecting to DB: ", x.args
    try:
        json_result = cur.execute(sql_query.get(q_type))
        return json_result
    except:
        return []


def maint_redis(conn):
    update_interest_list()
    # del list for outdated keys
    for key in interest_list.keys():
        json_result = is_key_outdated(conn, key)
        if json_result:
            del_keys.append(key)
        else:
            interest_list[key] = json_result



    # remove all out-dated keys from dictionary
    # add new keys in tmp_interest_list to dictionary
    # seek for new datas for my keys in interest list
    # check time stamp and add them to the dict
    # call this method in rheTOracle.py main





"""
1 - Her search yapildiginda
A. time_stamp i kontrol et.
    Eger time_stamp  bizim time_stample
A. search yapilan bilgiyi redis-servera ata
2 - Her search yapildiginda get_redis i calistir ve bilgileri getir
3 - her 5 dakikada bir db yi tara ve zaman kisitlamasina gore
        redis_server i guncelle
4 - No3 icin gevent olustur ve arkada redisi calistir

"""




def connect_db():
    try:
        connection_string = []
        connection_string.append("host=rhetoracle-db-instance.c2vrlkt9v1tp.us-west-2.rds.amazonaws.com")
        connection_string.append("dbname=rhetorical-db")
        connection_string.append("user=" + "codefellow")
        connection_string.append("password=" + "teamawesome1!")
        return psycopg2.connect(" ".join(connection_string))
    except Exception as x:
        print "Error connecting to DB: ", x.args


def get_data_from_db(conn, time_stamp):
    # get most recent datas in out interest list
    cur = conn.cursor()
    try:
        cur.execute()
    except:


def get_database_connection():
    db = getattr(g, 'db', None)
    if db is None:
        g.db = db = connect_db()
    return db


if __name__ == '__main__':
    conn = connect_db()



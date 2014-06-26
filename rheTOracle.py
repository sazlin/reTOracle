from flask import Flask
from flask import render_template
import psycopg2
import json
from filters_json import filter_list

#from passlib.hash import pbkdf2_sha256
from SECRETS import SECRETS
app = Flask(__name__)

app.config['DB_HOST'] = "rhetoracle-db-instance.c2vrlkt9v1tp.us-west-2.rds.amazonaws.com"
app.config['DB_NAME'] = "rhetorical-db"
app.config['DB_USERNAME'] = SECRETS['DB_USERNAME']
#app.config['DB_PASSWORD'] = pbkdf2_sha256.encrypt(SECRETS['DB_PASSWORD'])
app.config['DB_PASSWORD'] = SECRETS['DB_PASSWORD']
#app.config['SECRET_KEY'] = SECRETS['FLASK_SECRET_KEY']
app.config['DB_CONNECTION'] = None
app.config['DB_CURSOR'] = None


def build_connection_string():
        connection_string = []
        connection_string.append("host=" + app.config['DB_HOST'])
        connection_string.append("dbname=" + app.config['DB_NAME'])
        connection_string.append("user=" + app.config['DB_USERNAME'])
        connection_string.append("password=" + app.config['DB_PASSWORD'])
        return " ".join(connection_string)


def connect_db():
    """establish a new connection"""
    connection_string = build_connection_string()
    try:
        print "establishing a new connection..."
        conn = psycopg2.connect(connection_string)
    except Exception as x:
        print "Error connecting to DB: ", x.args
    print "Connection established and stored..."
    app.config['DB_CONNECTION'] = conn
    return conn


def get_connection():
    """get the current connection if it exists, else connect."""
    if app.config['DB_CONNECTION'] is not None:
        print "connection exists, so reusing it..."
        return app.config['DB_CONNECTION']
    else:
        print "no connection found..."
        return connect_db()


def create_cursor():
    """create a new cursor and store it"""
    conn = get_connection()
    app.config['DB_CURSOR'] = conn.cursor()
    return app.config['DB_CURSOR']


def get_cursor():
    """get the current cursor if it exist, else create a new cursor"""
    if app.config['DB_CURSOR'] is not None:
        print "cursor exists, using that..."
        return app.config['DB_CURSOR']
    else:
        print "no cursor found, so creating one..."
        return create_cursor()


def execute_query(sql):
    """execute the passed in SQL using the current cursor"""
    print "executing query..."
    try:
        cur = get_cursor()
    except Exception as x:
        print "Something went wrong: ", x.args
    print "got cursor..."
    cur.execute(sql)
    try:
        results = cur.fetchall()
        print "Raw Results: ", results
    except Exception as x:
        print "Error executing sql on cursor: ", x.args
    else:
        print "query success!"
        print "Returning: ", json.dumps(results)
        return json.dumps(results)
    return None


@app.route('/', methods=['GET'])
def home_page():
    return render_template('home.html')


@app.route('/about', methods=['GET'])
def about_page():
    return render_template('about.html')


@app.route('/contact', methods=['GET'])
def contact_page():
    return render_template('contact.html')


@app.route('/test-graph', methods=['GET'])
def test_graph():
    return render_template('test_graphs.html')

def build_q1_querystring():
    """build a query string for Q1 using filter_list"""
    sql = []
    sql.append("""SELECT hashtag, COUNT(hashtag) as HashTagCount""")
    sql.append("""FROM (SELECT screen_name, unnest(hashtags) as hashtag FROM massive) as subquery""")
    sql.append("""WHERE""")
    for language in filter_list:
        search_terms = filter_list[language]['search_terms']
        for hashtag in search_terms['hashtags']:
            sql.append("""hashtag = '""" + hashtag[1:] + """'""")
            sql.append("""OR""")
        # for user in search_terms['users']:
        #     sql.append("""screen_name = '""" + user + """'""")
        #     sql.append(""" OR """)
        # for keyword in search_terms['keywords']:
        #     sql.append("""'"""+ keyword + """' LIKE text""")
        #     sql.append(""" OR """)
    sql.pop()  # discard last OR statement
    sql.append("""GROUP BY hashtag""")
    sql.append("""ORDER BY HashTagCount DESC""")
    return " \r\n".join(sql)


def map_q1_results_to_language(parsed_results):
    """use the filter_list to group and sum the results parsed from Q1's query results
        into a new list of lists that will be returned to the client for rendering"""
    final_result = []
    for language in filter_list:
        language_count = 0
        search_terms = filter_list[language]['search_terms']
        for hashtag in search_terms['hashtags']:
            for result in parsed_results:
                print "***comparing***", hashtag[1:], result[0]
                if hashtag[1:] == result[0]:
                    language_count += result[1]
        final_result.append([language, language_count])
    return json.dumps(final_result)


@app.route('/q1', methods=['GET'])
def q1_query():
    """Which programming language is being talked about the most?"""
    #q1_what = request.args.get('q1_what', None)
    #print "qt_what: ", q1_what
    json_result = None
    #if not q1_what == "":
    sql = """
    SELECT hashtag, COUNT(hashtag) as HashTagCount
    FROM (SELECT screen_name, unnest(hashtags) as hashtag FROM massive) as subquery
    WHERE
    hashtag = 'Java' OR
    hashtag = 'Python' OR
    hashtag = 'JavaScript' OR
    hashtag = 'CPlusPlus' OR
    hashtag = 'Ruby'
    GROUP BY hashtag
    ORDER BY HashTagCount DESC
    """
    query_string = build_q1_querystring()
    #print "QUERY STRING: ",query_string
    json_result = execute_query(query_string)
    parsed_results = json.loads(json_result)
    final_result = map_q1_results_to_language(parsed_results)
    #print "QUERY RESULT: ",query_result
    return final_result


@app.route('/q2', methods=['GET'])
def q2_query():
    """Who is *the* guys to follow for a given language?"""
    json_result = None
    sql = """
    SELECT hashtag, HashTagCount, screen_name
    FROM
    (
        SELECT hashtag, screen_name, HashTagCount, rank() OVER (PARTITION BY hashtag ORDER BY HashTagCount DESC, screen_name) AS pos
        FROM (
            SELECT hashtag, screen_name, COUNT(hashtag) as HashTagCount
            FROM (
                SELECT screen_name, unnest(hashtags) as hashtag
                FROM massive
            ) as unwrap
            WHERE
            hashtag = 'Java' OR
            hashtag = 'Python' OR
            hashtag = 'JavaScript' OR
            hashtag = 'CPlusPlus' OR
            hashtag = 'Java'
            GROUP BY screen_name, hashtag
            ORDER BY hashtag, HashTagCount DESC
        ) as countedhashtags
    ) as ss
    WHERE pos = 1
    ORDER BY hashtag, HashTagCount DESC
    """
    json_result = execute_query(sql)
    print json.loads(json_result)
    return json_result

if __name__ == '__main__':
    app.run()

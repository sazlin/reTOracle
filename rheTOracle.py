from flask import Flask, redirect, url_for, request
from flask import render_template
import psycopg2
import json
#from passlib.hash import pbkdf2_sha256
from secrets import SECRETS
app = Flask(__name__)

app.config['DB_HOST'] = "rhetoracle-db-instance.c2vrlkt9v1tp.us-west-2.rds.amazonaws.com"
app.config['DB_NAME'] = "rhetorical-db"
app.config['DB_USERNAME'] = SECRETS['DB_USERNAME']
#app.config['DB_PASSWORD'] = pbkdf2_sha256.encrypt(SECRETS['DB_PASSWORD'])
app.config['DB_PASSWORD'] = SECRETS['DB_PASSWORD']
app.config['SECRET_KEY'] = SECRETS['FLASK_SECRET_KEY']
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


@app.route('/q1', methods=['GET'])
def q1_query(q1_what="#Seattle"):
    """Who is talking about #q1_what?"""
    q1_what = request.args.get('q1_what', None)
    print "qt_what: ", q1_what
    json_result = None
    if not q1_what == "":
        sql = """
        SELECT screen_name, COUNT(screen_name) as TweetCount
        FROM massive
        WHERE '""" + q1_what + """' = ANY (hashtags)
        GROUP BY screen_name
        """
        json_result = execute_query(sql)
    return json_result


@app.route('/q2', methods=['GET'])
def q2_query(q2_who="@crisewing"):
    """What is @q2_who talking about?"""
    q2_who = request.args.get('q2_who', None)
    print "q2_who: ", q2_who
    json_result = None
    if not q2_who == "":
        sql = """
        SELECT hashtag, COUNT(hashtag) as HashTagCount
        FROM (SELECT screen_name, unnest(hashtags) as hashtag FROM massive WHERE screen_name = '""" + q2_who + """') as subquery
        GROUP BY hashtag
        """
        json_result = execute_query(sql)
    return json_result


@app.route('/q3', methods=['GET'])
def q3_query(q3_who="@CodeFellowsOrg"):
    """Who is talking about @q3_who?"""
    return redirect(url_for('home_page'))


@app.route('/q4', methods=['GET'])
def q4_query(q4_who="#Seattle"):
    """Who is @q4_who talking about?"""
    return redirect(url_for('home_page'))

if __name__ == '__main__':
    app.run()

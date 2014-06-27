import psycopg2
import json
from flask import Flask


# from passlib.hash import pbkdf2_sha256
from SECRETS import SECRETS
app = Flask(__name__)

app.config['DB_HOST'] = "rhetoracle-db-instance.c2vrlkt9v1tp.us-west-2.rds.amazonaws.com"
app.config['DB_NAME'] = "rhetorical-db"
app.config['DB_USERNAME'] = SECRETS['DB_USERNAME']
app.config['DB_PASSWORD'] = SECRETS['DB_PASSWORD']
app.config['DB_CONNECTION'] = None
app.config['DB_CURSOR'] = None
# app.config['SECRET_KEY'] = SECRETS['FLASK_SECRET_KEY']
# app.config['DB_PASSWORD'] = pbkdf2_sha256.encrypt(SECRETS['DB_PASSWORD'])


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
    except Exception as x:
        print "Error executing sql on cursor: ", x.args
    else:
        print "query success!"
        return json.dumps(results)
    return None

"""
@app.route('/q1', methods=['GET'])
def q1_query(q1_what="#Seattle"):
    Who is talking about #q1_what?
    try:
        result_list = red.get_redis_query("type1"+"Java")
        print result_list
        return json.dumps(result_list)
    except:
        return redirect(url_for('home_page'))

@app.route('/q2', methods=['GET'])
def q2_query():
    What is @q2_who talking about?
    red.maint_redis()
    return redirect(url_for('home_page'))
    """
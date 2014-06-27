from flask import Flask, Response
from flask import render_template
import psycopg2
import json
from filters_json import filter_list
import random

#from passlib.hash import pbkdf2_sha256
from SECRETS import SECRETS
app = Flask(__name__)

app.config['DB_HOST'] = "rhetoracle-db-instance.c2vrlkt9v1tp.us-west-2.rds.amazonaws.com"
app.config['DB_NAME'] = "rhetorical-db"
app.config['DB_USERNAME'] = SECRETS['DB_USERNAME']
#app.config['DB_PASSWORD'] = pbkdf2_sha256.encrypt(SECRETS['DB_PASSWORD'])
app.config['DB_PASSWORD'] = SECRETS['DB_PASSWORD']
# app.config['SECRET_KEY'] = SECRETS['FLASK_SECRET_KEY']

app.config['DB_CONNECTION'] = None
app.config['DB_CURSOR'] = None
app.config['LAST_GEO_TWEET_ID'] = -1

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
        #print "Raw Results: ", results
    except Exception as x:
        print "Error executing sql on cursor: ", x.args
    else:
        print "query success!"
        #print "Raw Results: ", results
        #print "Returning: ", json.dumps(results)

    try:
        json_results = json.dumps(results)
    except Exception as x:
        print "***Error dumping json: ", json_results
    else:
        return json_results

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

app.config['Q1_QUERYSTRING'] = build_q1_querystring()


def build_q2_querystring():
    """build a query string for Q2 using filter_list"""
    sql = []
    sql.append("""SELECT hashtag, HashTagCount, screen_name""")
    sql.append("""FROM (SELECT hashtag, screen_name, HashTagCount, rank() OVER (PARTITION BY hashtag ORDER BY HashTagCount DESC, screen_name) AS pos""")
    sql.append("""FROM (SELECT hashtag, screen_name, COUNT(hashtag) as HashTagCount""")
    sql.append("""FROM (SELECT screen_name, unnest(hashtags) as hashtag FROM massive) as unwrap""")
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
    sql.append("""GROUP BY screen_name, hashtag""")
    sql.append("""ORDER BY hashtag, HashTagCount DESC""")
    sql.append(""") as countedhashtags""")
    sql.append(""") as ss""")
    sql.append("""WHERE pos = 1""")
    sql.append("""ORDER BY hashtag, HashTagCount DESC""")
    return " \r\n".join(sql)
    """
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
app.config['Q2_QUERYSTRING'] = build_q2_querystring()


def map_q1_results_to_language(parsed_results):
    """use the filter_list to group and sum the results parsed from Q1's query results
        into a new list of lists that will be returned to the client for rendering"""
    final_result = []
    for language in filter_list:
        language_count = 0
        search_terms = filter_list[language]['search_terms']
        for hashtag in search_terms['hashtags']:
            for result in parsed_results:
                #print "***comparing***", hashtag[1:], result[0]
                if hashtag[1:] == result[0]:
                    language_count += result[1]
        final_result.append([language, language_count])
    return json.dumps(final_result)

def map_q2_results_to_language(parsed_results):
    """use the filter_list to group and sum the results parsed from Q2's query results
        into a new list of lists that will be returned to the client for rendering"""
    #print "***Coming into q2 mapping:\r\n", parsed_results
    final_result = []
    try:
        for language in filter_list:
            userCountForThisLanguage = {}
            search_terms = filter_list[language]['search_terms']
            for hashtag in search_terms['hashtags']:
                for result in parsed_results:
                    #print "***comparing***", hashtag[1:], result[0]
                    if hashtag[1:] == result[0]:
                        if not userCountForThisLanguage.has_key(result[2]):
                            userCountForThisLanguage[result[2]] = result[1]
                        userCountForThisLanguage[result[2]] += result[1]
            top_user_count, top_user = 0, ""
            if len(userCountForThisLanguage.items()) is not 0:
                top_user_count, top_user = max((v,k) for  k,v in userCountForThisLanguage.items())
            #print "For ", language, ": top_user: ",top_user, " top_user_count: ", top_user_count
            final_result.append([language, top_user_count, top_user])
    except Exception as x:
        print "**************Something went wrong:", x.args
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
    query_string = app.config['Q1_QUERYSTRING']
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
    query_string = app.config['Q2_QUERYSTRING']
    #print "QUERY STRING: ",query_string
    json_result = execute_query(query_string)
    parsed_results = json.loads(json_result)
    final_result = map_q2_results_to_language(parsed_results)
    #print "QUERY RESULT: ",query_result
    return final_result

@app.route('/geotweet', methods=['GET'])
def get_latest_geo_tweet():
    sql = []
    sql.append("""SELECT tweet_id, text, screen_name, location FROM massive""")
    sql.append("""WHERE json_array_length(location) <> 0""")
    sql.append("""ORDER BY tweet_id DESC LIMIT 1""")
    try:
        json_result = execute_query(" ".join(sql))
        #print "JSON: ", json_result
        parsed_results = json.loads(json_result)
        #print "PARSED: ", parsed_results
        #if app.config['LAST_GEO_TWEET_ID'] == parsed_results[0][0]:
        #    return "unchanged"
        app.config['LAST_GEO_TWEET_ID'] = parsed_results[0][0]
        latitude = parsed_results[0][3][0]
        longitude = parsed_results[0][3][1]
        #latitude = random.random() * 40 + 40
        #longitude = random.random() * 40 - 70.0
        screen_name = parsed_results[0][2]
        text = parsed_results[0][1]
    except Exception as x:
        print "SOMETHING WENT WRONG: ", x.args
    print "Latest Geo Tweet: ", screen_name, latitude, longitude
    try:
        response = {}
        response['map'] = 'worldLow'
        response['images'] = [{}]
        response['images'][0]['latitude'] = latitude
        response['images'][0]['longitude'] = longitude
        response['images'][0]['svgPath'] = "M26.492,9.493c-0.771,0.343-1.602,0.574-2.473,0.678c0.89-0.533,1.562-1.376,1.893-2.382c-0.832,0.493-1.753,0.852-2.734,1.044c-0.785-0.837-1.902-1.359-3.142-1.359c-2.377,0-4.306,1.928-4.306,4.306c0,0.337,0.039,0.666,0.112,0.979c-3.578-0.18-6.75-1.894-8.874-4.499c-0.371,0.636-0.583,1.375-0.583,2.165c0,1.494,0.76,2.812,1.915,3.583c-0.706-0.022-1.37-0.216-1.95-0.538c0,0.018,0,0.036,0,0.053c0,2.086,1.484,3.829,3.454,4.222c-0.361,0.099-0.741,0.147-1.134,0.147c-0.278,0-0.547-0.023-0.81-0.076c0.548,1.711,2.138,2.955,4.022,2.99c-1.474,1.146-3.33,1.842-5.347,1.842c-0.348,0-0.69-0.021-1.027-0.062c1.905,1.225,4.168,1.938,6.6,1.938c7.919,0,12.248-6.562,12.248-12.25c0-0.187-0.002-0.372-0.01-0.557C25.186,11.115,25.915,10.356,26.492,9.493"
        response['images'][0]['color'] = '#00F'
        response['images'][0]['scale'] = 0.5
        response['images'][0]['labelShiftX'] = 0
        response['images'][0]['labelShiftY'] = 0
        #response['images'][0]['zoomLevel'] = 3
        response['images'][0]['title'] = screen_name
        response['images'][0]['label'] = screen_name
        response['images'][0]['description'] = text
        # response.append("""longitude:""" + str(longitude) + """,""")
        # response.append("""svgPath:icon, """)
        # response.append("""color:"#00F",""")
        # response.append("""scale:0.5,""")
        # response.append("""labelShiftY:2,""")
        # response.append("""zoomLevel:5,""")
        # response.append('title:"' + screen_name + '",')
        # response.append('label:"' + screen_name + '",')
        # response.append('description:"' + text + '"}]')
        # response.append("""}""")
        response_json = json.dumps(response)
    except Exception as x:
        print x.args
    print "geomap response: ",response_json
    resp = Response(response=response_json,
                            status=200,
                            mimetype="application/json")
    return resp

    """
    {map: "worldLow",
     images:[{
     latitude:40.3951,
     longitude:-73.5619,
     svgPath:icon,
     color:"#CC0000",
     scale:0.5,
     label:"New York",
     labelShiftY:2,
     zoomLevel:5,
     title:"New York",
     description:"New York is the most populous city in the United States and the center of the New York Metropolitan Area, one of the most populous metropolitan areas in the world."
     }]
    };
    """

if __name__ == '__main__':
    app.run()

from flask import Flask, Response, render_template
from filters_json import filter_list
import json
import sql_queries as sql_q
import redis_conn as re
#from SECRETS import SECRETS
from time import time
import os
import sys
# from passlib.hash import pbkdf2_sha256

app = Flask(__name__)

# app.config['LAST_GEO_TWEET_ID'] = -1
# app.config['DB_PASSWORD'] = pbkdf2_sha256.encrypt(SECRETS['DB_PASSWORD'])
# app.config['SECRET_KEY'] = SECRETS['FLASK_SECRET_KEY']


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


def map_q1_results_to_language(parsed_results):
    """use the filter_list to group and sum the results parsed from Q1's query results
        into a new list of lists that will be returned to the client for rendering"""
    final_result = []
    for item in parsed_results:
        final_result.append([item[0], item[1]])
    for lang in filter_list:
        _found = False
        for item in parsed_results:
            if lang.lower() == item[0]:
                _found = True
        if not _found:
            final_result.append([lang, 0])

    return json.dumps(final_result)




def map_q2_results_to_language(parsed_results):
    """use the filter_list to group and sum the results parsed from Q2's query results
        into a new list of lists that will be returned to the client for rendering"""
    final_result = []
    for item in parsed_results:
        final_result.append([item[0], item[1], item[2]])

    for lang in filter_list:
        _found = False
        for item in parsed_results:
            if lang.lower() == item[0]:
                _found = True
        if not _found:
            final_result.append([lang, 0, 'God knows you lonely souls'])
    return json.dumps(final_result)


def update_redis():
    new_time = time()
    if (new_time - app.config['LAST_REDIS_UPDATE']) > app.config['REDIS_UPDATE_INTERVAL']:
        #re.maint_redis()
        app.config['LAST_REDIS_UPDATE'] = new_time


@app.route('/q1', methods=['GET'])
def q1_query():
    """Which programming language is being talked about the most?"""
    update_redis()
    try:
        print "*****Q1********: Getting vals from redis..."
        json_result = re.get_redis_query('chart1')
    except:
        print "...ERROR. Trying SQL instead..."
        #json_result = sql_q.get_query_results('fetch_chart1')
        json_result = sql_q.get_query_results('fetch_filter_tw_counts')
    parsed_results = json.loads(json_result)
    print "Got results: ", parsed_results
    final_result = map_q1_results_to_language(parsed_results)
    print "Formatted Results: ",final_result
    return final_result


@app.route('/q2', methods=['GET'])
def q2_query():
    """Who is *the* person to follow for a given language?"""
    update_redis()
    try:
        json_result = re.get_redis_query('chart2')
    except:
        #json_result = sql_q.get_query_results('fetch_chart2')
        json_result = sql_q.get_query_results('fetch_popular_users')
    #parsed_results = json.loads(json_result)
    parsed_results = json_result
    final_result = map_q2_results_to_language(parsed_results)
    return final_result




@app.route('/geotweet', methods=['GET'])
def get_latest_geo_tweet():
    update_redis()

    try:
        print "Geo: getting query results..."
        json_result = sql_q.get_query_results('geomap1')
        print "Geo: parsing json..."
        parsed_results = json.loads(json_result)
        print "Geo: breaking out needed vals..."
        latitude = parsed_results[0][3][0]
        longitude = parsed_results[0][3][1]
        screen_name = parsed_results[0][2]
        text = parsed_results[0][1]
        print "Geo: success"
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
        response['images'][0]['color'] = '#F22'
        response['images'][0]['scale'] = 2
        response['images'][0]['labelShiftX'] = 15
        response['images'][0]['labelShiftY'] = 20
        response['images'][0]['zoomLevel'] = 10
        response['images'][0]['zoomLatitude'] = latitude
        response['images'][0]['zoomLongitude'] = longitude
        response['images'][0]['title'] = screen_name
        response['images'][0]['label'] = screen_name
        response['images'][0]['description'] = text
        response_json = json.dumps(response)
    except Exception as x:
        print x.args
    print "geomap response: ",response_json
    resp = Response(response=response_json,
                            status=200,
                            mimetype="application/json")
    return resp


@app.route('/ticker', methods=['GET'])
def ticker_fetch():
    """Return JSON for recent tweet"""
    json_result = sql_q.get_query_results('ticker1')

    resp = Response(response=json_result,
                    status=200,
                    mimetype="application/json")
    return resp


if __name__ == '__main__':

    if sys.argv[1] == 'Prod':
        app.config['DB_HOST'] = os.environ.get('R_DB_HOST')
        app.config['DB_NAME'] = os.environ.get('R_DB_NAME')
        app.config['DB_USERNAME'] = os.environ.get('R_DB_USERNAME')
        app.config['DB_PASSWORD'] = os.environ.get('R_DB_PASSWORD')
    elif sys.argv[1] == 'Test':
        app.config['DB_HOST'] = os.environ.get('R_TEST_DB_HOST')
        app.config['DB_NAME'] = os.environ.get('R_TEST_DB_NAME')
        app.config['DB_USERNAME'] = os.environ.get('R_TEST_DB_USERNAME')
        app.config['DB_PASSWORD'] = os.environ.get('R_TEST_DB_PASSWORD')

    app.config['DB_CONNECTION'] = None
    app.config['DB_CURSOR'] = None
    app.config['REDIS_UPDATE_INTERVAL'] = 3


    sql_q.init()
    re.init_pool()
    #re.maint_redis()
    app.config['LAST_REDIS_UPDATE'] = time()
    app.run()

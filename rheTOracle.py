#!/usr/bin/python

from flask import Flask, Response, render_template
from flask import Markup
import markdown
from filters_json import filter_list
import json
import sql_queries as sql_q
import redis_conn as re
from time import time
import os
from logger import make_logger
import argparse
import inspect
import itertools


logger = make_logger(inspect.stack()[0][1], 'retoracle.log')


app = Flask(__name__)


@app.route('/', methods=['GET'])
def home_page():
    return render_template('home.html')


@app.route('/about', methods=['GET'])
def about_page():
    try:
        with open('./static/markdown/about.md', 'rb') as f:
            content = Markup(markdown.markdown(f.read()))
    except Exception as e:
        print "Markdown fail: ", e.args
        print os.getcwd()
    return render_template('about.html', **locals())


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
            final_result.append([lang, 0, ' '])
    return json.dumps(final_result)


def update_redis():
    new_time = time()
    if (new_time - app.config['LAST_REDIS_UPDATE']) > app.config['REDIS_UPDATE_INTERVAL']:
        re.maint_redis()
        app.config['LAST_REDIS_UPDATE'] = new_time


# @app.route('/q1', methods=['GET'])
# def q1_query():
#     """Which programming language is being talked about the most?"""
#     update_redis()
#     try:
#         logger.debug("Q1: Getting values from redis")

#         json_result = re.get_redis_query('chart1')
#     except:
#         logger.error("Q1: redis failed. Trying SQL instead")
#         json_result = sql_q.get_query_results('chart1')
#     parsed_results = json.loads(json_result)
#     final_result = map_q1_results_to_language(parsed_results)
#     return final_result


@app.route('/q2', methods=['GET'])
def q2_query():
    """Who is *the* person to follow for a given language?"""
    update_redis()
    try:
        logger.debug("Q2: Getting values from redis...")
        json_result = re.get_redis_query('fetch_popular_users')
        logger.debug("Q2: Succes! From Redis: %s", json_result)
    except Exception as x:
        logger.error("Q2: Redis Query Failed! %s", x.args)
        try:
            logger.debug("Q2: Trying SQL instead...")
            json_result = sql_q.get_query_results('fetch_popular_users')
            logger.debug("Q2: Success! From SQL: %s", json_result)
        except Exception as x:
            logger.critical("Q2: SQL Query also Failed! %s", x.args)
            raise x
    logger.debug("Q2: loading json_result...")

    ###GET SENTIMENT VALUES#####
    user_count = []
    logger.error("These are jsonresults Q2 %s", json_result)
    json_result = json.loads(json_result)
    index = 0
    for result in json_result:
        logger.info("This is result, %s", result)
        logger.info("This is the hashtag %s", result[0])
        logger.info("This is the user %s", result[2])
        user_count.append([result[0]] + [0, 0, 0])
        counts = sql_q.get_query_results('popular_tweet_sent', [result[2], result[0]])
        # logger.info("Here is final list of tweets: %s", tweet_ids)
        counts = json.loads(counts)
        logger.info("These are the counts %s", counts)
        for count in counts:
            if count[0] == 1:
                user_count[index][1] += 1
            elif count[0] == -1:
                user_count[index][2] += 1
            elif count[0] == 0:
                user_count[index][3] += 1
            else:
                raise Exception("Q2: unexpected agg_sent")
        index += 1
    logger.info("Q2 TIHS IS THE OUTPUT LIST %s", user_count)
    output_json = json.dumps(user_count)
    resp = Response(response=output_json,
                    status=200,
                    mimetype="text/plain")

    return resp

@app.route('/geotweet', methods=['GET'])
def get_latest_geo_tweet():
    # update_redis()

    try:
        json_result = sql_q.get_query_results('geomap1')
        parsed_results = json.loads(json_result)
        latitude = parsed_results[0][3][0]
        longitude = parsed_results[0][3][1]
        screen_name = parsed_results[0][2]
        text = parsed_results[0][1]
    except Exception as x:
        logger.error("Geotweet: Error loading and parsing json: %s", x.args, exc_info=True)
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
        logger.error("Geotweet response error: %s", x.args, exc_info=True)

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


@app.route('/q1', methods=['GET'])
def q1_query():
    build_count_table = {}
    logger.info("Q1: Assembling response...")
    try:
        logger.debug("Q1: Getting values from redis")
        filter_sent_counts = re.get_redis_query('fetch_filter_sent_counts')
        filter_sent_counts = json.loads(filter_sent_counts)
    except:
        logger.debug("Q1: redis failed. Trying SQL instead")
        filter_sent_counts = json.loads(sql_q.get_query_results('fetch_filter_sent_counts'))

    for language in filter_list:
        logger.debug("Q1: Current language %s", language)
        build_count_table[language] = [0,0,0]

    for record in filter_sent_counts:
        if record[1] == 1:
            build_count_table[record[0]][0] = record[2]
        elif record[1] == 0:
            build_count_table[record[0]][2] = record[2]
        elif record[1] == -1:
            build_count_table[record[0]][1] = record[2]
        else:
            raise Exception("Unexpected agg_sent in sql response.")
    output_list = []
    for key in build_count_table:
        output_list.append([key] + build_count_table[key])
    try:
        logger.debug("Q1: Dumping output_list into JSON...")
        output_json = json.dumps(output_list)
    except Exception as x:
        logger.debug("Q1: Error converting output_json to a json string:", x.args)
        raise x
    else:
        logger.debug("Q1: This is final output %s", output_json)
        resp = Response(response=output_json,
                        status=200,
                        mimetype="text/plain")
        return resp


parser = argparse.ArgumentParser()
parser.add_argument('setting')
parser.add_argument('-v', '--verbosity', type=int)
ARGS = parser.parse_args()


if __name__ == '__main__':

    if ARGS.setting == 'Prod':
        app.config['DB_HOST'] = os.environ.get('R_DB_HOST')
        app.config['DB_NAME'] = os.environ.get('R_DB_NAME')
        app.config['DB_USERNAME'] = os.environ.get('R_DB_USERNAME')
        app.config['DB_PASSWORD'] = os.environ.get('R_DB_PASSWORD')
    elif ARGS.setting == 'Test':
        app.config['DB_HOST'] = os.environ.get('R_TEST_DB_HOST')
        app.config['DB_NAME'] = os.environ.get('R_TEST_DB_NAME')
        app.config['DB_USERNAME'] = os.environ.get('R_TEST_DB_USERNAME')
        app.config['DB_PASSWORD'] = os.environ.get('R_TEST_DB_PASSWORD')

    app.config['DB_CONNECTION'] = None
    app.config['DB_CURSOR'] = None
    app.config['REDIS_UPDATE_INTERVAL'] = 3

    sql_q.init()
    re.init_pool()
    re.maint_redis()
    app.config['LAST_REDIS_UPDATE'] = time()
    app.run()

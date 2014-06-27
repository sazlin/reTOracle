
from flask import Flask
from flask import render_template
from filters_json import filter_list
import json
import connection as con
import sql_queries as sql_q
app = Flask(__name__)


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


app.config['Q1_QUERYSTRING'] = sql_q.build_q1_querystring()


app.config['Q2_QUERYSTRING'] = sql_q.build_q2_querystring()


def map_q1_results_to_language(parsed_results):
    """use the filter_list to group and sum the results parsed from Q1's
    query results into a new list of lists that will be returned to the client
    for rendering"""
    final_result = []
    for language in filter_list:
        language_count = 0
        search_terms = filter_list[language]['search_terms']
        for hashtag in search_terms['hashtags']:
            for result in parsed_results:
                if hashtag[1:] == result[0]:
                    language_count += result[1]
        final_result.append([language, language_count])
    return json.dumps(final_result)


def map_q2_results_to_language(parsed_results):
    """use the filter_list to group and sum the results parsed from Q2's
    query results into a new list of lists that will be returned to the client
    for rendering"""
    final_result = []
    try:
        for language in filter_list:
            userCountForThisLanguage = {}
            search_terms = filter_list[language]['search_terms']
            for hashtag in search_terms['hashtags']:
                for result in parsed_results:
                    if hashtag[1:] == result[0]:
                        if not userCountForThisLanguage.has_key(result[2]):
                            userCountForThisLanguage[result[2]] = result[1]
                        userCountForThisLanguage[result[2]] += result[1]
            top_user_count, top_user = 0, ""
            if len(userCountForThisLanguage.items()) is not 0:
                top_user_count, top_user = max((v, k) for k, v in userCountForThisLanguage.items())
            final_result.append([language, top_user_count, top_user])
    except Exception as x:
        print "**************Something went wrong:", x.args
    return json.dumps(final_result)


@app.route('/q1', methods=['GET'])
def q1_query():
    """Which programming language is being talked about the most?"""
    json_result = None
    # if not q1_what == "":
    query_string = app.config['Q1_QUERYSTRING']
    json_result = con.execute_query(query_string)
    parsed_results = json.loads(json_result)
    final_result = map_q1_results_to_language(parsed_results)
    return final_result


@app.route('/q2', methods=['GET'])
def q2_query():
    """Who is *the* guys to follow for a given language?"""
    json_result = None
    query_string = app.config['Q2_QUERYSTRING']
    json_result = con.execute_query(query_string)
    parsed_results = json.loads(json_result)
    final_result = map_q2_results_to_language(parsed_results)
    return final_result

if __name__ == '__main__':
    app.run()

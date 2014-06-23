from flask import Flask, redirect, url_for
from flask import render_template
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


@app.route('/q1', methods=['GET'])
def q1_query(q1_what="#Seattle"):
    """Who is talking about #q1_what?"""
    return redirect(url_for('home_page'))


@app.route('/q2', methods=['GET'])
def q2_query(q2_who="@crisewing"):
    """What is @q2_who talking about?"""
    return redirect(url_for('home_page'))


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

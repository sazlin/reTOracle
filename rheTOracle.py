from flask import Flask
app = Flask(__name__)


@app.route('/')
def hello_world():
    return say_hello()




def say_hello():
    return u'RheTOracly speaking, how awesome are we?'

if __name__ == '__main__':
    app.run()

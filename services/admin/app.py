# create an hello world endpoint
from flask import Flask, make_response

app = Flask(__name__)

# BASE_URL = '/users/admin'

@app.route('/')
def hello_world():
    return make_response('Hello, World!\n', 200)

@app.route('/prova')
def prova():
    return make_response('Prova\n', 200)  

if __name__ == '__main__':
    app.run()
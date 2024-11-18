from flask import Flask, request, make_response, jsonify
import random, time, os, threading, requests


app = Flask(__name__)
SECRET_KEY = os.environ.get('SECRET_KEY') or 'this is a secret'
print(SECRET_KEY)
app.config['SECRET_KEY'] = SECRET_KEY

@app.route('/')
def index():
    return make_response('Hello, World!\n', 200)

if __name__ == '__main__':
    app.run(debug=True)
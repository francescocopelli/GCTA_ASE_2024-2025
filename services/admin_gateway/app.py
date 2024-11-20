from flask import Flask, request, make_response, jsonify
import random, time, os, threading, requests
from shared.auth_middleware import *

app = Flask(__name__)

print(SECRET_KEY)
app.config['SECRET_KEY'] = SECRET_KEY

@app.route('/')
def index():
    return make_response('Hello, World!\n', 200)

if __name__ == '__main__':
    app.run(debug=True)
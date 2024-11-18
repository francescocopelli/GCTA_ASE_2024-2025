from flask import Flask, request, make_response, jsonify
import random, time, os, threading, requests


app = Flask(__name__)

# Make a function that takes JSON data and returns a response
def send_response(message, status_code):
    return jsonify(message), status_code

@app.route('/')
def index():
    return make_response('Hello, World!\n', 200)

if __name__ == '__main__':
    app.run(debug=True)
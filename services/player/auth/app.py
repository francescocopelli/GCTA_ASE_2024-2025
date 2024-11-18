import os

import requests
from flask import Flask, jsonify, request

from shared.auth_middleware import token_required


app = Flask(__name__)
SECRET_KEY = os.environ.get('SECRET_KEY') or 'this is a secret'
print(SECRET_KEY)
app.config['SECRET_KEY'] = SECRET_KEY

dbm_url = "http://db-manager:5000"

# Make a function that takes JSON data and returns a response
def send_response(message, status_code):
    return jsonify(message), status_code


@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']
    url = f"{dbm_url}/login/PLAYER"
    data = {
        "username": username,
        "password": password
    }
    response = requests.post(url, json=data)
    return send_response(response.json(), response.status_code)

@app.route('/register', methods=['POST'])
def register():
    username = request.json['username']
    password = request.json['password']
    email = request.json['email']
    url = f"{dbm_url}/register/PLAYER"
    data = {
        "username": username,
        "password": password,
        "email": email
    }
    response = requests.post(url, json=data)
    return send_response(response.json(), response.status_code)

@token_required
@app.route('/logout', methods=['POST'])
def logout():
    session_token = request.json['session_token']
    url = f"{dbm_url}/logout/PLAYER"
    data = {
        "session_token": session_token
    }
    response = requests.post(url, json=data)
    return send_response(response.json(), response.status_code)

# delete my account
@app.route('/delete', methods=['DELETE'])
def delete():
    session_token = request.json['session_token']
    url = f"{dbm_url}/delete/PLAYER"
    data = {
        "session_token": session_token
    }
    response = requests.post(url, json=data)
    return send_response(response.json(), response.status_code)

@token_required
#update my account pw, email, username
@app.route('/update', methods=['PUT'])
def update():
    session_token = request.json['session_token']
    username = request.json['username']
    password = request.json['password']
    email = request.json['email']
    url = f"{dbm_url}/update/PLAYER"
    data = {
        "session_token": session_token,
        "username": username,
        "password": password,
        "email": email
    }
    response = requests.post(url, json=data)
    return send_response(response.json(), response.status_code)


# Esempio di utilizzo
if __name__ == '__main__': 
    app.run()

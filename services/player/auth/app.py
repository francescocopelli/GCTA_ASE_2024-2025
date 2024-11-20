import base64
import os

import requests
from flask import Flask, jsonify, request

from shared.auth_middleware import *

app = Flask(__name__)
SECRET_KEY = os.environ.get('SECRET_KEY') or 'this is a secret'
print(SECRET_KEY)
app.config['SECRET_KEY'] = SECRET_KEY

dbm_url = "http://db-manager:5000"

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
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    image = request.files.get('image')
    if image:
        image = image.read()
    url = f"{dbm_url}/register/PLAYER"
    data = {
        "username": username,
        "password": password,
        "email": email,
        "image": base64.b64encode(image).decode('utf-8') if image else None
    }
    response = requests.post(url, data=data)
    return send_response(response.json(), response.status_code)

@app.route('/logout', methods=['POST'])
@token_required_ret
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

#update my account pw, email, username
@app.route('/update', methods=['PUT'])
@token_required_void
def update():
    data = request.form
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    image = request.files.get('image')
    if image:
        image = image.read()

    url = f"{dbm_url}/update/PLAYER"
    data = {
        "username": str(username),
        "password": str(password),
        "email": str(email),
        # "image": base64.b64encode(image).decode('utf-8') if image else None
    }
    response, status_code = requests.post(url, json=data, headers=generate_session_token_system())
    return send_response(response, status_code)


# Esempio di utilizzo
if __name__ == '__main__': 
    app.run()

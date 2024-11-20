import os

import requests
from flask import Flask, jsonify

from shared.auth_middleware import *

app = Flask(__name__)

print(SECRET_KEY)
app.config['SECRET_KEY'] = SECRET_KEY
logging.basicConfig(level=logging.DEBUG)

@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']
    url = f"http://db-manager:5000/login/ADMIN"
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
    url = f"http://db-manager:5000/register/ADMIN"
    data = {
        "username": username,
        "password": password,
        "email": email
    }
    response = requests.post(url, json=data)
    return send_response(response.json(), response.status_code)

@app.route('/logout', methods=['POST'])
def logout():
    username = request.json['username']
    url = f"http://db-manager:5000/logout/ADMIN"
    data = {
        "username": username
    }
    response = requests.post(url, json=data)
    return send_response(response.json(), response.status_code)

@app.route('/reset_pwd', methods=['POST'])
def reset_password():
    email = request.json['email']
    new_password = request.json['new_password']
    url = f"http://db-manager:5000/reset_pwd/ADMIN"
    data = {
        "email": email,
        "new_password": new_password
    }
    response = requests.post(url, json=data)
    return send_response(response.json(), response.status_code)

@app.get('/get_all/<user_type>')
@admin_required
def get_all(user_type):
    logging.info(f"Get all users {user_type}")
    url = f"http://db-manager:5000/get_all/{user_type}"
    response = requests.get(url, headers=request.headers)
    return send_response(response.json(), response.status_code)

# Esempio di utilizzo
if __name__ == '__main__':
    app.run()

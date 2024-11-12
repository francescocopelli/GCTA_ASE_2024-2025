import requests
from flask import Flask, request

app = Flask(__name__)


@app.route('/logout', methods=['POST'])
def logout():
    session_token = request.json['session_token']
    url = f"http://db-manager:5000/logout/ADMIN"
    data = {
        "session_token": session_token
    }
    response = requests.post(url, json=data)
    return response.json()

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
    return response.json()

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
    return response.json()

# Esempio di utilizzo
if __name__ == '__main__':
    app.run()

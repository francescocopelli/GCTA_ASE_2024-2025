import requests
from flask import Flask, request

app = Flask(__name__)

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
    print(response.json())
    return response.json()

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
    return response.json()

@app.route('/logout', methods=['POST'])
def logout():
    session_token = request.json['session_token']
    url = f"{dbm_url}/logout/PLAYER"
    data = {
        "session_token": session_token
    }
    response = requests.post(url, json=data)
    return response.json()

# delete my account
@app.route('/delete', methods=['DELETE'])
def delete():
    session_token = request.json['session_token']
    url = f"{dbm_url}/delete/PLAYER"
    data = {
        "session_token": session_token
    }
    response = requests.post(url, json=data)
    return response.json()

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
    return response.json()


# Esempio di utilizzo
if __name__ == '__main__':
    app.run()
    
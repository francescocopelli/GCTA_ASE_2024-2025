import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

dbm_url = "http://db-manager:5000"
auction_url = "http://auction:5000"
gacha_url = "http://gacha:5000"

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
    #call to dbm for delete account infos
    session_token = request.json['session_token']
    url = f"{dbm_url}/delete/PLAYER/{session_token}"
    response = requests.delete(url)
    if response.status_code == 200:
        #call to auction for delete all my auctions
        url = f"{auction_url}/delete"
        data = {
            "user_id": response.json()['user_id']
        }
        response2 = requests.put(url, json=data)
        
        #call to auction for delete the inventory
        url = f"{gacha_url}/delete"
        data = {
            "user_id": response.json()['user_id']
        }
        response3 = requests.put(url, json=data)
        
        return send_response(response3.json(), response3.status_code)

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

#TODO implementare parte in DBM

@app.route('/users/auth/reset_pwd', methods=['POST'])
def reset_password():
    email = request.json['email']
    url = f"{dbm_url}/reset_pwd/PLAYER"
    data = {
        "email": email
    }
    response = requests.post(url, json=data)
    return send_response(response.json(), response.status_code)

# Esempio di utilizzo
if __name__ == '__main__': 
    app.run()

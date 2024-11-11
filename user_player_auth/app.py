import requests
from flask import Flask

app = Flask(__name__)

@app.route('/user/player_auth/login', methods=['POST'])
def login(username, password, user_type):
    url = f"http://db-manager:5000/login/PLAYER"
    data = {
        "username": username,
        "password": password
    }
    response = requests.post(url, json=data)
    return response.json()

@app.route('/user/player_auth/register', methods=['POST'])
def register(username, password, email, user_type):
    url = f"http://db-manager:5000/register/PLAYER"
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
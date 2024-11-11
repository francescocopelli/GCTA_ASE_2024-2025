import requests
from flask import Flask

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login(username, password):
    url = f"http://db-manager:5000/login/ADMIN"
    data = {
        "username": username,
        "password": password
    }
    response = requests.post(url, json=data)
    return response.json()

@app.route('/register', methods=['POST'])
def register(username, password, email):
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

# create an hello world endpoint
import requests
from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run()

@app.get("/get_user/<user_id>")
def get_user(user_id):
    url = f"http://db-manager:5000/get_user/" + user_id
    response = requests.get(url)
    return response.json()
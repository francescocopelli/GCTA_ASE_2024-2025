# from services.player.auth.test_app import AuthUser
from threading import Lock
from locust import events

from services.player.test_app import UserPlayer

# from services.gacha.test_app import GachaTest

session_token = []
user_id = []
session_token_lock = Lock()

user_auth = "/users/auth"
user_player = "/users/player"
gacha_url = "/gacha"

def create_header(token):
    return {"Authorization": f"Bearer {token}"}


def login(self):
    global session_token
    global user_id
    with session_token_lock:
        if len(session_token) == 0:
            for a in range(0,3):
                response = self.client.post(f'{user_auth}/login', json={
                    "username": "test_"+ str(a+1),
                    "password": "prova"
                })
                print(f"login response: {response.json()}")
                session_token.append(response.json()["session_token"])
                user_id.append(response.json()["user_id"])
                print(f"session_token: {session_token}")


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, context, **kwargs):
    # print the response time in seconds
    response_time = response_time / 1000
    print(f"Request Type: {request_type}, Name: {name}, Response Time: {response_time}, Response Length: {response_length}, Context: {context}")
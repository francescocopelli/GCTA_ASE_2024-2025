
from threading import Lock

from locust import events
import random
import string

from test_locust.gacha_test import GachaBehavior
from test_locust.auction_test import GetAllAuctionsBehavior
from test_locust.player_test import UserBehavior




#PLAYERS LOGIN
session_token = []
user_id = []
session_token_lock = Lock()
all_auctions = []


user_auth = "/users/auth"
user_player = "/users/player"
gacha_url = "/gacha"
auction_url = "/auction"

def create_header(token):
    return {"Authorization": f"Bearer {token}"}


def generate_random_username(length=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def register_and_login(self):
    random_username = generate_random_username()
    # Register a user with a random username and password
    with self.client.post(f'{user_auth}/register', verify=False, data={
        "username": random_username,
        "password": "prova",
        "email": f"{random_username}@example.com"
    } , catch_response=True) as response:
        print(f"register response: {response.json()}")
        if response.status_code > 201:
            response.failure("Failed to register user")
    with self.client.post(f'{user_auth}/login', verify=False, json={
        "username": random_username,
        "password": "prova"
    }, catch_response=True) as response:
        print(f"login response: {response.json()}")
        self.session_token_user = response.json().get("session_token")
        self.user_id = response.json().get("user_id")
    

def delete_user(self):
    with self.client.delete(f'{user_player}/delete', verify=False, headers=create_header(self.session_token_user)) as response:
        print(f"delete response: {response.json()}")
        if response.status_code > 201:
            response.failure("Failed to delete user")

#ADMIN LOGIN
admin_session_token = []
admin_user_id = []
admin_session_token_lock = Lock()

admin_base = "https://localhost:8081"
admin_auth = admin_base + "/users/admin_auth"

def create_admin_header(token):
    return {"Authorization": f"Bearer {token}"}

def register_and_login_admin(self):
    random_username = generate_random_username()
    # Register a user with a random username and password
    with self.client.post(f'{admin_auth}/register', verify=False, data={
        "username": "admin_"+random_username,
        "password": "prova",
        "email": f"{random_username}@example.com"
    }, catch_response=True) as response:
        print(f"register response: {response.json()}")
        if response.status_code > 200:
            response.failure("Failed to register admin")
    with self.client.post(f'{admin_auth}/login', verify=False, json={
        "username": "admin_"+random_username,
        "password": "prova"
    }, catch_response=True) as response:
        print(f"login response: {response.json()}")
        self.admin_session_token = response.json().get("session_token")
        self.admin_id = response.json().get("user_id")
            
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, context, **kwargs):
    # print the response time in seconds
    response_time = response_time / 1000
    print(f"Request Type: {request_type}, Name: {name}, Response Time: {response_time}, Response Length: {response_length}, Context: {context}")
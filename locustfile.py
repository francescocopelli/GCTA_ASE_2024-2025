
from threading import Lock
from locust import events

from test_locust.auction_test import GetAllAuctionsTest
# from test_locust.auth_player_test import AuthUser
from test_locust.dbm_test import WebsiteUser
from test_locust.gacha_test import GachaTest
from test_locust.player_test import UserPlayer
from test_locust.transaction_test import GetTransactionTest



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


def login(self):
    global session_token
    global user_id
    with session_token_lock:
        if len(session_token) == 0:
            for a in range(0,3):
                response = self.client.post(f'{user_auth}/login', verify=False, json={
                    "username": "test_"+ str(a+1),
                    "password": "prova"
                })
                print(f"login response: {response.json()}")
                session_token.append(response.json()["session_token"])
                user_id.append(response.json()["user_id"])
                print(f"session_token: {session_token}")


#ADMIN LOGIN
admin_session_token = []
admin_user_id = []
admin_session_token_lock = Lock()

admin_base = "https://localhost:8081"
admin_auth = admin_base + "/users/admin_auth"

def create_admin_header(token):
    return {"Authorization": f"Bearer {token}"}

def admin_login(self):
    global admin_session_token
    global admin_user_id
    with admin_session_token_lock:
        if len(admin_session_token) == 0:
            for a in range(0, 3):
                response = self.client.post(f'{admin_auth}/login', verify=False, json={
                    "username": "admin_test_" + str(a + 1),
                    "password": "prova"
                })
                print(f"admin login response: {response.json()}")
                admin_session_token.append(response.json()["session_token"])
                admin_user_id.append(response.json()["user_id"])
                print(f"admin_session_token: {admin_session_token}")


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, context, **kwargs):
    # print the response time in seconds
    response_time = response_time / 1000
    print(f"Request Type: {request_type}, Name: {name}, Response Time: {response_time}, Response Length: {response_length}, Context: {context}")
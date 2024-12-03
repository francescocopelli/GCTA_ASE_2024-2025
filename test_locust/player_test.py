import random

from locust import HttpUser, TaskSet, task, between
from locustfile import *
import locustfile

def create_header(token):
    return {"Authorization": f"Bearer {token}"}


class UserBehavior(TaskSet):

    @task
    def my_gacha_list_logged(self):
        
        locustfile.login(self)
        response = self.client.get(f"{locustfile.user_player}/my_gacha_list", verify=False, headers=create_header(locustfile.session_token[random.choice(range(0,3))]))
        # if response.status_code != 200:
        #     print(f'my_gacha_list_logged response: {response}')
        #     exit(1)
        # # print(f'my_gacha_list_logged response: {response.json()}')
        # else:
        assert response.status_code == 200
        assert isinstance(response.json(), dict)

    @task
    def gacha_info_logged(self):
        
        locustfile.login(self)
        gacha_id = 25
        usr=random.choice(range(0,3))
        response = self.client.get(f"{locustfile.user_player}/gacha/{locustfile.user_id[usr]}/{gacha_id}", verify=False, headers=create_header(locustfile.session_token[usr]))

        assert response.status_code == 200

    @task
    def real_money_transaction_logged(self):
        
        locustfile.login(self)
        usr = random.choice(range(0,3))
        response = self.client.post(f"{locustfile.user_player}/real_money_transaction", json={
            "user_id": locustfile.session_token[usr],
            "amount": 100.0
        }, verify=False, headers=create_header(locustfile.session_token[usr]))
        assert response.status_code == 200
        assert response.json()["message"] == "Account topped up successfully"
    @task
    def get_user_balance(self):
        locustfile.login(self)
        response = self.client.get(f"{locustfile.user_player}/get_user_balance", verify=False, headers=create_header(locustfile.session_token[random.choice(range(0,3))]))
        assert response.status_code == 200
        assert "currency_balance" in response.json()

    @task
    def get_user(self):
        
        locustfile.login(self)
        response = self.client.get(f"{locustfile.user_player}/get_user", verify=False, headers=create_header(locustfile.session_token[random.choice(range(0,3))]))
        assert response.status_code == 200
        assert "user_id" in response.json()

    @task
    def update_user(self):
        locustfile.login(self)
        usr=random.choice(range(0,3))
        response = self.client.put(f"{locustfile.user_player}/update", data={
            "email": f"temp_{''.join(random.choices('abcdefghijklmnopqrstuvwxyz' + '0123456789', k=10))}@email.com",
            "password":"prova"
        }, verify=False, headers=create_header(locustfile.session_token[usr]))
        assert response.status_code == 200
        assert response.json()["message"] == "Profile updated successfully"

class UserPlayer(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1,5)
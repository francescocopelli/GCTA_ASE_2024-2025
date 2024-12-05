import random

from locust import HttpUser, TaskSet, task, between

import locustfile


class UserBehavior(HttpUser):

    wait_time = between(1, 5)
    session_token_user = None
    user_id = None
    admin_session_token = None
    admin_id = None
    
    def on_start(self):
        locustfile.register_and_login(self)
    
    def on_stop(self):
        locustfile.delete_user(self)
        
    @task
    def my_gacha_list_logged(self):
        response = self.client.get(f"{locustfile.user_player}/my_gacha_list", verify=False, headers=locustfile.create_header(self.session_token_user))
        assert response.status_code == 200
        assert isinstance(response.json(), dict)

    @task
    def gacha_info_logged(self):
        gacha_id = 25
        response = self.client.get(f"{locustfile.user_player}/gacha/{self.user_id}/{gacha_id}", verify=False, headers=locustfile.create_header(self.session_token_user))
        assert response.status_code == 200

    @task
    def real_money_transaction_logged(self):
        response = self.client.post(f"{locustfile.user_player}/real_money_transaction", json={
            "user_id": self.user_id,
            "amount": 100.0
        }, verify=False, headers=locustfile.create_header(self.session_token_user))
        assert response.status_code == 200
        assert response.json()["message"] == "Account topped up successfully"
    @task
    def get_user_balance(self):
        response = self.client.get(f"{locustfile.user_player}/get_user_balance", verify=False, headers=locustfile.create_header(self.session_token_user))
        assert response.status_code == 200
        assert "currency_balance" in response.json()

    @task
    def get_user(self):
        response = self.client.get(f"{locustfile.user_player}/get_user", verify=False, headers=locustfile.create_header(self.session_token_user))
        assert response.status_code == 200
        assert "user_id" in response.json()

    @task
    def update_user(self):
        response = self.client.put(f"{locustfile.user_player}/update", data={
            "email": f"temp_{''.join(random.choices('abcdefghijklmnopqrstuvwxyz' + '0123456789', k=10))}@email.com",
            "password":"prova"
        }, verify=False, headers=locustfile.create_header(self.session_token_user))
        assert response.status_code == 200
        assert response.json()["message"] == "Profile updated successfully"
from locust import HttpUser, TaskSet, task, between

def create_header(token):
    return {"Authorization": f"Bearer {token}"}
    
class UserBehavior(TaskSet):
    @task
    def my_gacha_list(self):
        response = self.client.get("/my_gacha_list/1")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @task
    def gacha_info(self):
        response = self.client.get("/gacha/1/1")
        assert response.status_code == 200
        assert "gacha_id" in response.json()

    @task
    def real_money_transaction(self):
        response = self.client.post("/real_money_transaction", json={
            "user_id": "1",
            "amount": 100.0
        }, header=create_header("valid_session_token"))
        
        assert response.status_code == 200
        assert response.json()["message"] == "Transaction added successfully"

    @task
    def get_user_balance(self):
        response = self.client.get("/get_user_balance/1")
        assert response.status_code == 200
        assert "currency_balance" in response.json()

    @task
    def get_user(self):
        response = self.client.get("/get_user/1")
        assert response.status_code == 200
        assert "user_id" in response.json()

    @task
    def update_balance(self):
        response = self.client.put("/update_balance/PLAYER", json={
            "user_id": "1",
            "amount": 50.0,
            "type": "credit"
        }, header=create_header("valid_session_token"))
        assert response.status_code == 200
        assert response.json()["message"] == "Balance updated successfully"

class UserPlayer(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)
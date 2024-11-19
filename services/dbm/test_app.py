from locust import HttpUser, TaskSet, task, between

class UserBehavior(TaskSet):
    @task
    def test_register(self):
        self.client.post("/register/PLAYER", json={
            "username": "testuser",
            "password": "testpass",
            "email": "testuser@example.com"
        })

    @task
    def test_login(self):
        self.client.post("/login/PLAYER", json={
            "username": "testuser",
            "password": "testpass"
        })

    @task
    def test_logout(self):
        self.client.post("/logout/PLAYER", json={
            "session_token": "some_session_token"
        })

    @task
    def test_get_balance(self):
        self.client.get("/balance/PLAYER", params={"user_id": "1"})

    @task
    def test_delete(self):
        self.client.delete("/delete/PLAYER", json={
            "session_token": "some_session_token"
        })

    @task
    def test_update(self):
        self.client.put("/update/PLAYER", json={
            "session_token": "some_session_token",
            "username": "newusername",
            "password": "newpassword",
            "email": "newemail@example.com"
        })

    @task
    def test_update_balance_user(self):
        self.client.put("/update_balance/PLAYER", json={
            "user_id": "1",
            "amount": 100,
            "type": "credit"
        })

    @task
    def test_get_user(self):
        self.client.get("/get_user/PLAYER/1")

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)
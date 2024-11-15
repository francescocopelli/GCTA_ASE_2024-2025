from locust import HttpUser, TaskSet, task, between

class UserBehavior(TaskSet):
    @task
    def login_success(self):
        response = self.client.post('/users/auth/login', json={
            "username": "provando",
            "password": "prova"
        })
        #assert response.status_code == 200
        assert response.json()["message"] == "Login successful"

    @task
    def login_failure(self):
        response = self.client.post('/users/auth/login', json={
            "username": "wronguser",
            "password": "wrongpassword"
        })
        #assert response.status_code == 401
        assert response.json()["error"] == "Invalid credentials"

class AuthUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)
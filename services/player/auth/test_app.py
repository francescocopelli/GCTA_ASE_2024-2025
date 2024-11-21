from locust import HttpUser, TaskSet, task, between


class UserBehavior(TaskSet):
    @task
    def login_success(self):
        response = self.client.post('/login', json={
            "username": "provando",
            "password": "prova"
        })
        assert response.status_code == 200
        assert response.json()["message"] == "Login successful"

    @task
    def login_failure(self):
        response = self.client.post('/login', json={
            "username": "wronguser",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        assert response.json()["error"] == "Invalid credentials"

    @task
    def register(self):
        response = self.client.post('/register', json={
            "username": "new_player123",
            "password": "securepassword",
            "email": "new_player@example.com"
        })
        assert response.status_code == 200
        assert response.json()["message"] == "PLAYER registered successfully"

    @task
    def logout(self):
        response = self.client.post('/logout', json={
            "session_token": "valid_session_token"
        })
        assert response.status_code == 200
        assert response.json()["message"] == "Logout successful"

    @task
    def delete_account(self):
        response = self.client.delete('/delete', json={
            "session_token": "valid_session_token"
        })
        assert response.status_code == 200
        assert response.json()["message"] == "Account deleted successfully"

    @task
    def update_account(self):
        response = self.client.put('/update', json={
            "session_token": "valid_session_token",
            "username": "updated_username",
            "password": "updated_password",
            "email": "updated_email@example.com"
        })
        assert response.status_code == 200
        assert response.json()["message"] == "Account updated successfully"


class AuthUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)

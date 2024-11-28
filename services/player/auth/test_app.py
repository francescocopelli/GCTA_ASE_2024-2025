from locust import HttpUser, TaskSet, task, between
import random,string
import locustfile


def create_header(token):
    return {"Authorization": f"Bearer {token}"}

from shared.auth_middleware import *
def gen():
    alph=string.ascii_letters+string.digits
    return ''.join(random.choice(alph) for i in range(random.randint(5,32)))

class UserAuthBehavior(TaskSet):
    is_logged_in=None
    valid_session_token=None
    @task
    def login_success(self):
        response = self.client.post(f'{locustfile.user_auth}/login', json={
            "username": "provando",
            "password": "prova"
        })
        
        assert int(response.status_code) == 200
        assert response.json()["message"] == "Login successful"
        self.valid_session_token = response.json()["session_token"]
        self.is_logged_in = True
        
    @task
    def login_failure(self):
        with self.client.post(f'{locustfile.user_auth}/login', json={
            "username": "wronguser",
            "password": "wrongpassword"
        },catch_response=True) as response:
            if response.status_code == 401:
                assert response.json()["error"] == "Invalid credentials"
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")
    #generate test for register a random user with random password and email. Login with it and then logout. Check all return codes
    @task(100)
    def register_login_logout(self):
        random_username=gen()
        random_password=gen()
        print(f'username: {random_username} password: {random_password}')
        random_email=random_username+f"@{random_username[:4]}.com"
        print(f'email: {random_email}')
        response = self.client.post(f'{locustfile.user_auth}/register', data={

            "username": random_username,
            "password": random_password,
            "email": random_email
        })
        print(response.json())
        print(response.status_code)
        assert response.status_code == 200
        assert response.json()["message"] == "PLAYER registered successfully"
        response = self.client.post(f'{locustfile.user_auth}/login', json={
            "username": random_username,
            "password": random_password
        })
        assert response.status_code == 200
        assert response.json()["message"] == "Login successful"
        response = self.client.delete(f'{locustfile.user_auth}/logout', headers=create_header(response.json()["session_token"]))
        assert response.status_code == 200

    '''
    
    
    @task(1000)
    def logout(self):
        if not self.is_logged_in: self.login_success()
        response = self.client.delete('/logout', headers=create_header(self.valid_session_token))
        assert response.status_code == 200
        self.is_logged_in = False
    
    @task
    def register(self):
        response = self.client.post('/register', json={
            "username": "new_player123",
            "password": "securepassword",
            "email": "new_player@example.com"
        })
        assert int(response.status_code) == 200
        assert response.json()["message"] == "PLAYER registered successfully"

    @task
    def delete_account(self):
        response = self.client.post('/login', json={
            "username": "new_player123",
            "password": "securepassword"
        })
        assert int(response.status_code) == 200
        assert response.json()["message"] == "Login successful"
        self.valid_session_token = response.json()["session_token"]
        print(self.valid_session_token)
        response = self.client.delete('/delete', json={
            "session_token": self.valid_session_token
        }, headers=create_header("valid_session_token"))
        assert int(response.status_code) == 200
        assert response.json()["message"] == "Account deleted successfully"
        self.valid_session_token = None

    @task
    def update_account(self):
        response = self.client.post('/register', json={
            "username": "new_player123",
            "password": "securepassword",
            "email": "new_player@example.com"
        })
        assert response.status_code == 200
        assert response.json()["message"] == "PLAYER registered successfully"
        response = self.client.put('/update', json={
            
            "session_token": self.valid_session_token,
            "username": "new_player13",
            "password": "securepassword",
            "email": "updated_email@example.com"
        }, headers=create_header("valid_session_token"))
        assert int(response.status_code) == 200
        assert response.json()["message"] == "Account updated successfully"
        self.valid_session_token = None
'''
class AuthUser(HttpUser):
    tasks = [UserAuthBehavior]
    wait_time = between(1, 5)

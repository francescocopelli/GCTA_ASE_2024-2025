from locust import HttpUser, TaskSet, task, between

from services.player.test_app import user_auth
from locustfile import *
import locustfile

def create_header(token):
    return {"Authorization": f"Bearer {token}"}

class GachaBehavior(TaskSet):

    @task
    def add_gacha(self):

        locustfile.login(self)
        response = self.client.post(f"{gacha_url}/add", json={
            "gacha_name": "gacha_test",
            "gacha_type": "test",
            "gacha_cost": 10.0
        }, headers=create_header(locustfile.session_token[random.choice(range(0,3))]))


class GachaTest(HttpUser):
    tasks = [GachaBehavior]
    wait_time = between(1, 5)

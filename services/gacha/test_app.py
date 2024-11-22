from locust import HttpUser, TaskSet, task, between


class UserBehavior(TaskSet):
    @task
    def add_item(self):
        self.client.post("/gacha/add", data={
            "name": "Test Item",
            "rarity": "Common",
            "status": "available",
            "description": "A test item"
        }, header=create_header("valid_session_token"))

    @task
    def roll_gacha(self):
        self.client.post("/gacha/roll", json={
            "user_id": 1,
            "roll_cost": 5
        }, header=create_header("valid_session_token"))

    @task
    def get_user_inventory(self):
        self.client.get("/gacha/inventory/1")

    @task
    def add_to_inventory(self):
        self.client.post("/gacha/inventory/add", json={
            "user_id": 1,
            "gacha_id": 1
        }, header=create_header("valid_session_token"))

    @task
    def get_all(self):
        self.client.get("/gacha/all")

    @task
    def update_gacha_item(self):
        self.client.put("/gacha/update", data={
            "gacha_id": 1,
            "name": "Updated Item",
            "rarity": "Rare",
            "status": "available",
            "description": "An updated test item"
        }, header=create_header("valid_session_token"))

    @task
    def get_gacha_item(self):
        self.client.get("/gacha/get/1")

    @task
    def get_user_gacha_item(self):
        self.client.get("/gacha/get/1/1")

    @task
    def is_gacha_unlocked(self):
        self.client.get("/gacha/is_gacha_unlocked/1/1")

    @task
    def update_gacha_status(self):
        self.client.put("/gacha/update_gacha_status", json={
            "user_id": 1,
            "gacha_id": 1,
            "status": "unlocked"
        }, header=create_header("valid_session_token"))

    @task
    def update_gacha_owner(self):
        self.client.put("/gacha/update_gacha_owner", json={
            "buyer_id": 2,
            "seller_id": 1,
            "gacha_id": 1,
            "status": "unlocked"
        }, header=create_header("valid_session_token"))


class GachaTest(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)

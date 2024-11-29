import random
from locust import HttpUser, TaskSet, task, between

from locustfile import *
import locustfile

def create_header(token):
    return {"Authorization": f"Bearer {token}"}


class GachaBehavior(TaskSet):
    
    @task()
    def add_gacha_item(self):
        locustfile.admin_login(self)
        token = locustfile.admin_session_token[random.choice(range(0, 3))]
        headers = create_header(token)
        
        # Prepare data for adding a gacha item
        data = {
            "name": f"gacha_test_{random.randint(1, 1000)*random.randint(1, 1000)}",
            "rarity": "common",
            "status": "available",
            "description": "Test gacha item",
        }
        
        # Perform the add gacha item action
        response = self.client.post(f"{locustfile.admin_base}{locustfile.gacha_url}/add", data=data, headers=headers)
        
        # Check for possible errors
        if response.status_code == 201:
            print(f"Gacha item added successfully: {response.json()}")
            return response.json()["gacha_id"]
        elif response.status_code == 400:
            print(f"Error: Missing data to add gacha item")
        elif response.status_code == 401:
            print(f"Error: Admin authorization required")
        elif response.status_code == 500:
            print(f"Error: Internal server error")
        else:
            print(f"Unexpected status code {response.status_code}")

    @task
    def update_gacha_item(self):
        locustfile.admin_login(self)
        gacha_id = self.add_gacha_item() or random.randint(1, 100)
            
        token = locustfile.admin_session_token[random.choice(range(0, 3))]
        headers = create_header(token)
        
        # Prepare data for updating a gacha item
        data = {
            "gacha_id": gacha_id,  # Assuming gacha_id ranges from 1 to 100
            "name": f"updated_gacha_test_{random.randint(1, 1000)*random.randint(1, 1000)}",
            "rarity": "rare",
            "status": "available",
            "description": "Updated test gacha item",
        }
        
        # Perform the update gacha item action
        response = self.client.put(f"{locustfile.admin_base}{locustfile.gacha_url}/update", data=data, headers=headers)
        
        # Check for possible errors
        if response.status_code == 200:
            print(f"Gacha item updated successfully: {response.json()}")
        elif response.status_code == 400:
            print(f"Error: Missing data to update gacha item")
        elif response.status_code == 404:
            print(f"Error: Gacha item not found")
        elif response.status_code == 500:
            print(f"Error: Internal server error")
        else:
            print(f"Unexpected status code {response.status_code}")

    @task
    def get_gacha_item(self):
        locustfile.login(self)
        token = locustfile.session_token[random.choice(range(0, 3))]
        headers = create_header(token)
        gacha_id = random.randint(1, 300)  # Assuming gacha_id ranges from 1 to 100
        
        # Perform the get gacha item action
        response = self.client.get(f"{locustfile.gacha_url}/get/{gacha_id}", headers=headers)
        
        # Check for possible errors
        if response.status_code == 200:
            try:
                gacha_item = response.json()
                assert "gacha_id" in gacha_item
                assert "name" in gacha_item
                assert "rarity" in gacha_item
                assert "status" in gacha_item
                assert "description" in gacha_item
                print(f"Gacha item retrieved successfully: {gacha_item}")
            except ValueError:
                print(f"Error: Response is not valid JSON for gacha_id={gacha_id}")
        elif response.status_code == 404:
            print(f"Error: Gacha item not found for gacha_id={gacha_id}")
        elif response.status_code == 500:
            print(f"Error: Internal server error for gacha_id={gacha_id}")
        else:
            print(f"Unexpected status code {response.status_code} for gacha_id={gacha_id}")

    @task
    def get_user_gacha_item(self):
        locustfile.login(self)
        usr = random.choice(range(0, 3))
        token = locustfile.session_token[usr]
        headers = create_header(token)
        gacha_id = random.randint(1, 300)  # Assuming gacha_id ranges from 1 to 100
        
        # Perform the get user gacha item action
        with self.client.get(f"{locustfile.gacha_url}/get/{locustfile.user_id[usr]}/{gacha_id}", headers=headers, catch_response=True) as response:
        
            # Check for possible errors
            if response.status_code == 200:
                try:
                    gacha_item = response.json()
                    if "not found" in gacha_item.get("error", {}):
                        response.success()
                        return
                    else:
                        assert "description" in gacha_item
                        assert "gacha_id" in gacha_item
                        assert "name" in gacha_item
                        assert "rarity" in gacha_item
                        assert "status" in gacha_item
                        response.success()
                except ValueError:
                    response.failure(f"Error: Response is not valid JSON for user_id={locustfile.user_id}, gacha_id={gacha_id}")
            elif response.status_code == 403:
                response.failure(f"Error: You are not authorized to view this page for user_id={locustfile.user_id}")
            elif response.status_code == 404:
                response.success(f"Error: Gacha item not found in user inventory for user_id={locustfile.user_id}, gacha_id={gacha_id}")
            elif response.status_code == 500:
                response.failure(f"Error: Internal server error for user_id={locustfile.user_id}, gacha_id={gacha_id}")
            else:
                response.failure(f"Unexpected status code {response.status_code} for user_id={locustfile.user_id}, gacha_id={gacha_id}")

    @task
    def is_gacha_unlocked(self):
        locustfile.admin_login(self)
        token = locustfile.admin_session_token[random.choice(range(0, 3))]
        headers = create_header(token)
        user_id = random.choice(locustfile.user_id)
        gacha_id = random.randint(1, 100)  # Assuming gacha_id ranges from 1 to 100
        
        # Perform the is gacha unlocked action
        with self.client.get(f"{locustfile.admin_base}{locustfile.gacha_url}/is_gacha_unlocked/{user_id}/{gacha_id}", headers=headers, catch_response=True) as response:
            # Check for possible errors
            if response.status_code == 200 or response.status_code == 403:
                response.success()
            elif response.status_code == 400:
                response.failure(f"Error: Missing data to check gacha item for user_id={user_id}, gacha_id={gacha_id}")
            elif response.status_code == 403:
                response.failure(f"Gacha item is locked for user_id={user_id}, gacha_id={gacha_id}")
            elif response.status_code == 500:
                response.failure(f"Error: Internal server error for user_id={user_id}, gacha_id={gacha_id}")
            else:
                response.failure(f"Unexpected status code {response.status_code} for user_id={user_id}, gacha_id={gacha_id}")


    @task
    def delete_gacha_item(self):
        locustfile.admin_login(self)
        gacha_id = self.add_gacha_item() or random.randint(396, 430)
        token = locustfile.admin_session_token[random.choice(range(0, 3))]
        headers = create_header(token)
        
        # Perform the delete gacha item action
        with self.client.delete(f"{locustfile.admin_base}{locustfile.gacha_url}/delete/{gacha_id}", headers=headers, catch_response=True) as response:
        
            # Check for possible errors
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                response.success()
            elif response.status_code == 500:
                error_message = response.json().get('error', '')
                if error_message == 'Failed to get highest bid':
                    response.failure(f"Error: Failed to get highest bid for gacha_id={gacha_id}")
                elif error_message == 'Failed to update balance':
                    response.failure(f"Error: Failed to update balance for gacha_id={gacha_id}")
                elif error_message == 'Failed to delete auction':
                    response.failure(f"Error: Failed to delete auction for gacha_id={gacha_id}")
                elif error_message == 'Failed to delete gacha item':
                    response.failure(f"Error: Failed to delete gacha item: gacha_id={gacha_id}")
                else:
                    response.failure(f"Error: Internal server error for gacha_id={gacha_id}")
            else:
                response.failure(f"Unexpected status code {response.status_code} for gacha_id={gacha_id}")

    @task
    def get_all_gacha_items(self):
        token = locustfile.session_token[random.choice(range(0, 3))]
        headers = create_header(token)
        offset = random.randint(0, 100)  # Random offset for testing
        
        # Perform the get all gacha items action
        response = self.client.get(f"{locustfile.gacha_url}/all?offset={offset}", headers=headers)
        
        # Check for possible errors
        if response.status_code == 200:
            try:
                items = response.json().get('message', None)
                if items is None:
                    print(f"Error: Items not found in response")
                else:
                    assert isinstance(items, list)
                    print(f"Gacha items retrieved successfully with offset={offset}")
            except ValueError:
                print(f"Error: Response is not valid JSON with offset={offset}")
        elif response.status_code == 404:
            print(f"Error: No gacha items found with offset={offset}")
        elif response.status_code == 500:
            print(f"Error: Internal server error with offset={offset}")
        else:
            print(f"Unexpected status code {response.status_code} with offset={offset}")


class GachaInventoryBehavior(TaskSet):

    @task
    def get_user_inventory(self):
        locustfile.login(self)
        usr = random.choice(range(0, 3))
        response = self.client.get(f"{locustfile.gacha_url}/inventory/{locustfile.user_id[usr]}", headers=create_header(locustfile.session_token[usr]))
        
        # Check for possible errors
        if response.status_code == 200:
            try:
                inventory = response.json().get('inventory', None)
                if inventory is None:
                    print(f"Error: Inventory not found in response for user_id={locustfile.user_id[usr]}")
                else:
                    assert isinstance(inventory, list)
                    print(f"Inventory retrieved successfully for user_id={locustfile.user_id[usr]}")
            except ValueError:
                print(f"Error: Response is not valid JSON for user_id={locustfile.user_id[usr]}")
        elif response.status_code == 404:
            print(f"Error: No gacha items found for user_id={locustfile.user_id[usr]}")
        else:
            print(f"Unexpected status code {response.status_code} for user_id={locustfile.user_id[usr]}")

    @task
    def add_to_inventory(self):
        locustfile.admin_login(self)
        user_id = random.choice(locustfile.admin_user_id)
        gacha_id = random.randint(1, 100)  # Assuming gacha_id ranges from 1 to 100
        token = locustfile.admin_session_token[random.choice(range(0, 3))]
        headers = create_header(token)
        
        # Perform the add to inventory action
        with self.client.post(f"{locustfile.admin_base}{locustfile.gacha_url}/inventory/add", json={
            "user_id": user_id,
            "gacha_id": gacha_id
        }, headers=headers, catch_response=True) as response:
        
            # Check for possible errors
            if response.status_code == 201:
                response.success()
            elif response.status_code == 400:
                print(f"Error: Missing data to add gacha to inventory for user_id={user_id}, gacha_id={gacha_id}")
            elif response.status_code == 404:
                error_message = response.json().get('error', '')
                if error_message == 'User not found':
                    print(f"Error: User not found for user_id={user_id}")
                elif error_message == 'Gacha item not found or not available':
                    print(f"Error: Gacha item not found or not available for gacha_id={gacha_id}")
                else:
                    print(f"Error: Not found for user_id={user_id}, gacha_id={gacha_id}")
            elif response.status_code == 500:
                print(f"Error: Internal server error for user_id={user_id}, gacha_id={gacha_id}")
            else:
                print(f"Unexpected status code {response.status_code} for user_id={user_id}, gacha_id={gacha_id}")

class GachaRollBehavior(TaskSet):

    @task
    def roll_gacha(self):
        locustfile.login(self)
        user_id = random.choice(locustfile.user_id)
        token = locustfile.session_token[random.choice(range(0, 3))]
        headers = create_header(token)
        
        # Perform the gacha roll
        response = self.client.post(f"{locustfile.gacha_url}/roll", json={}, headers=headers)
        
        # Check for possible errors
        if response.status_code == 200:
            try:
                result = response.json()
                assert "gacha_id" in result
                assert "name" in result
                assert "rarity" in result
                print(f"Gacha roll successful for user_id={user_id}")
            except ValueError:
                print(f"Error: Response is not valid JSON for user_id={user_id}")
        elif response.status_code == 400:
            print(f"Error: Missing data for gacha roll for user_id={user_id}")
        elif response.status_code == 403:
            error_message = response.json().get('error', '')
            if error_message == 'Admins cannot roll gacha':
                print(f"Error: Admins cannot roll gacha for user_id={user_id}")
            elif error_message == 'Insufficient funds for gacha roll':
                print(f"Error: Insufficient funds for gacha roll for user_id={user_id}")
            else:
                print(f"Error: Forbidden action for user_id={user_id}")
        elif response.status_code == 500:
            error_message = response.json().get('error', '')
            if error_message == 'Failed to update user balance':
                print(f"Error: Failed to update user balance for user_id={user_id}")
            elif error_message == 'Failed to add transaction':
                print(f"Error: Failed to add transaction for user_id={user_id}")
            elif error_message == 'Failed to perform gacha roll':
                print(f"Error: Failed to perform gacha roll for user_id={user_id}")
            elif error_message == 'Failed to add gacha item to inventory':
                print(f"Error: Failed to add gacha item to inventory for user_id={user_id}")
            else:
                print(f"Error: Internal server error for user_id={user_id}")
        else:
            print(f"Unexpected status code {response.status_code} for user_id={user_id}")

class GachaTest(HttpUser):
    tasks = [GachaBehavior, GachaInventoryBehavior, GachaRollBehavior]
    wait_time = between(1, 5)
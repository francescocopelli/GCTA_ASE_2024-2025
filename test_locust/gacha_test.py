import random

from locust import HttpUser, task, between

import locustfile


class GachaBehavior(HttpUser):
    wait_time = between(1, 5)
    session_token_user = None
    user_id = None
    admin_session_token = None
    admin_id = None
    
    def on_start(self):
        locustfile.register_and_login(self)
        locustfile.register_and_login_admin(self)
    
    def on_stop(self):
        locustfile.delete_user(self)
    
    @task
    def add_gacha_item(self):
        headers = locustfile.create_header(self.admin_session_token)
        
        # Prepare data for adding a gacha item
        data = {
            "name": f"gacha_test_{random.randint(1, 1000)*random.randint(1, 1000)}",
            "rarity": "common",
            "status": "available",
            "description": "Test gacha item",
        }
        
        # Perform the add gacha item action
        with self.client.post(f"{locustfile.admin_base}{locustfile.gacha_url}/add", data=data, verify=False, headers=headers, catch_response=True) as response:
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
        gacha_id = self.add_gacha_item() or random.randint(1, 100)
        headers = locustfile.create_header(self.admin_session_token)
        
        # Prepare data for updating a gacha item
        data = {
            "gacha_id": gacha_id,  # Assuming gacha_id ranges from 1 to 100
            "name": f"updated_gacha_test_{random.randint(1, 1000)*random.randint(1, 1000)}",
            "rarity": "rare",
            "status": "available",
            "description": "Updated test gacha item",
        }
        
        # Perform the update gacha item action
        with self.client.put(f"{locustfile.admin_base}{locustfile.gacha_url}/update", data=data, verify=False, headers=headers, catch_response=True) as response:
            
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
        headers = locustfile.create_header(self.session_token_user)
        gacha_id = random.randint(1, 300)  # Assuming gacha_id ranges from 1 to 100
        
        # Perform the get gacha item action
        with self.client.get(f"{locustfile.gacha_url}/get/{gacha_id}", verify=False, headers=headers, catch_response=True) as response:
            
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
        headers = locustfile.create_header(self.session_token_user)
        gacha_id = random.randint(1, 300)  # Assuming gacha_id ranges from 1 to 100
        
        # Perform the get user gacha item action
        with self.client.get(f"{locustfile.gacha_url}/get/{self.user_id}/{gacha_id}", verify=False, headers=headers, catch_response=True) as response:
        
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
                    response.failure(f"Error: Response is not valid JSON for user_id={self.user_id}, gacha_id={gacha_id}")
            elif response.status_code == 403:
                response.failure(f"Error: You are not authorized to view this page for user_id={self.user_id}")
            elif response.status_code == 404:
                response.success(f"Error: Gacha item not found in user inventory for user_id={self.user_id}, gacha_id={gacha_id}")
            elif response.status_code == 500:
                response.failure(f"Error: Internal server error for user_id={self.user_id}, gacha_id={gacha_id}")
            else:
                response.failure(f"Unexpected status code {response.status_code} for user_id={self.user_id}, gacha_id={gacha_id}")

    @task
    def is_gacha_unlocked(self):
        headers = locustfile.create_header(self.admin_session_token)
        gacha_id = random.randint(1, 100)  # Assuming gacha_id ranges from 1 to 100
        
        # Perform the is gacha unlocked action
        with self.client.get(f"{locustfile.admin_base}{locustfile.gacha_url}/is_gacha_unlocked/{self.user_id}/{gacha_id}", verify=False, headers=headers, catch_response=True) as response:
            # Check for possible errors
            if response.status_code == 200 or response.status_code == 403:
                response.success()
            elif response.status_code == 400:
                response.failure(f"Error: Missing data to check gacha item for user_id={self.user_id}, gacha_id={gacha_id}")
            elif response.status_code == 403:
                response.failure(f"Gacha item is locked for user_id={self.user_id}, gacha_id={gacha_id}")
            elif response.status_code == 500:
                response.failure(f"Error: Internal server error for user_id={self.user_id}, gacha_id={gacha_id}")
            else:
                response.failure(f"Unexpected status code {response.status_code} for user_id={self.user_id}, gacha_id={gacha_id}")


    @task
    def delete_gacha_item(self):   
        gacha_id = self.add_gacha_item() or random.randint(396, 430)
        headers = locustfile.create_header(self.admin_session_token)
        
        # Perform the delete gacha item action
        with self.client.delete(f"{locustfile.admin_base}{locustfile.gacha_url}/delete/{gacha_id}", verify=False, headers=headers, catch_response=True) as response:
        
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
        headers = locustfile.create_header(self.session_token_user)
        # Perform the get all gacha items action
        response = self.client.get(f"{locustfile.gacha_url}/all", verify=False, headers=headers)
        
        # Check for possible errors
        if response.status_code == 200:
            try:
                items = response.json().get('message', None)
                if items is None:
                    print(f"Error: Items not found in response")
                else:
                    assert isinstance(items, list)
                    print(f"Gacha items retrieved successfully")
            except ValueError:
                print(f"Error: Response is not valid JSON")
        elif response.status_code == 404:
            print(f"Error: No gacha items found")
        elif response.status_code == 500:
            print(f"Error: Internal server error")
        else:
            print(f"Unexpected status code {response.status_code}")

    @task
    def get_user_inventory(self):
        response = self.client.get(f"{locustfile.gacha_url}/inventory/{self.user_id}", verify=False, headers=locustfile.create_header(self.session_token_user))
        
        # Check for possible errors
        if response.status_code == 200:
            try:
                inventory = response.json().get('inventory', None)
                if inventory is None:
                    print(f"Error: Inventory not found in response for user_id={self.user_id}")
                else:
                    assert isinstance(inventory, list)
                    print(f"Inventory retrieved successfully for user_id={self.user_id}")
            except ValueError:
                print(f"Error: Response is not valid JSON for user_id={self.user_id}")
        elif response.status_code == 404:
            print(f"Error: No gacha items found for user_id={self.user_id}")
        else:
            print(f"Unexpected status code {response.status_code} for user_id={self.user_id}")

    @task
    def add_to_inventory(self):
        gacha_id = random.randint(1, 100)  # Assuming gacha_id ranges from 1 to 100
        headers = locustfile.create_header(self.admin_session_token)
        
        # Perform the add to inventory action
        with self.client.post(f"{locustfile.admin_base}{locustfile.gacha_url}/inventory/add", json={
            "user_id": self.user_id,
            "gacha_id": gacha_id
        }, verify=False, headers=headers, catch_response=True) as response:
        
            # Check for possible errors
            if response.status_code == 201:
                response.success()
            elif response.status_code == 400:
                print(f"Error: Missing data to add gacha to inventory for user_id={self.user_id}, gacha_id={gacha_id}")
            elif response.status_code == 404:
                error_message = response.json().get('error', '')
                if error_message == 'User not found':
                    print(f"Error: User not found for user_id={self.user_id}")
                elif error_message == 'Gacha item not found or not available':
                    print(f"Error: Gacha item not found or not available for gacha_id={gacha_id}")
                else:
                    print(f"Error: Not found for user_id={self.user_id}, gacha_id={gacha_id}")
            elif response.status_code == 500:
                print(f"Error: Internal server error for user_id={self.user_id}, gacha_id={gacha_id}")
            else:
                print(f"Unexpected status code {response.status_code} for user_id={self.user_id}, gacha_id={gacha_id}")
                
    @task
    def roll_gacha(self):
        headers = locustfile.create_header(self.session_token_user)
        
        # Perform the gacha roll
        with self.client.post(f"{locustfile.gacha_url}/roll", verify=False, headers=headers, catch_response=True) as response:
        
            # Check for possible errors
            if response.status_code == 200:
                try:
                    result = response.json()
                    assert "gacha_id" in result
                    assert "name" in result
                    assert "rarity" in result
                    print(f"Gacha roll successful for user_id={self.user_id}")
                except ValueError:
                    print(f"Error: Response is not valid JSON for user_id={self.user_id}")
            elif response.status_code == 400:
                print(f"Error: Missing data for gacha roll for user_id={self.user_id}")
            elif response.status_code == 403:
                error_message = response.json().get('error', '')
                if error_message == 'Admins cannot roll gacha':
                    print(f"Error: Admins cannot roll gacha for user_id={self.user_id}")
                elif error_message == 'Insufficient funds for gacha roll':
                    print(f"Error: Insufficient funds for gacha roll for user_id={self.user_id}")
                else:
                    print(f"Error: Forbidden action for user_id={self.user_id}")
            elif response.status_code == 500:
                error_message = response.json().get('error', '')
                if error_message == 'Failed to update user balance':
                    print(f"Error: Failed to update user balance for user_id={self.user_id}")
                elif error_message == 'Failed to add transaction':
                    print(f"Error: Failed to add transaction for user_id={self.user_id}")
                elif error_message == 'Failed to perform gacha roll':
                    print(f"Error: Failed to perform gacha roll for user_id={self.user_id}")
                elif error_message == 'Failed to add gacha item to inventory':
                    print(f"Error: Failed to add gacha item to inventory for user_id={self.user_id}")
                else:
                    print(f"Error: Internal server error for user_id={self.user_id}")
            else:
                print(f"Unexpected status code {response.status_code} for user_id={self.user_id}")
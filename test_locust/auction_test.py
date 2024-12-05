import datetime
import random
from threading import Lock

from locust import HttpUser, task, between

import locustfile


class GetAllAuctionsBehavior(HttpUser):

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
    def all_auctions(self):
        headers = locustfile.create_admin_header(self.admin_session_token)
        status = random.choice(["all", "active", "expired", "completed"])  # Random status for testing

        # Perform the get all auctions action
        with self.client.get(f"{locustfile.admin_base}{locustfile.auction_url}/all?status={status}", verify=False, headers=headers,
                             catch_response=True) as response:

            # Check for possible errors
            if response.status_code == 200:
                try:
                    auctions = response.json().get("auctions", None)
                    if auctions is None:
                        response.failure(f"Error: Auctions not found in response")
                    else:
                        print(f"Auctions retrieved successfully with status={status}: {auctions}")
                except ValueError:
                    print(f"Error: Response is not valid JSON with status={status}")
            elif response.status_code == 404:
                response.success()
            elif response.status_code == 500:
                print(f"Error: Internal server error with status={status}")
            else:
                print(f"Unexpected status code {response.status_code} with status={status}")

    @task
    def get_all_active_auctions(self):
        headers = locustfile.create_admin_header(self.admin_session_token)
        # Perform the get all active auctions action
        response = self.client.get(f"{locustfile.admin_base}{locustfile.auction_url}/all_active", verify=False, headers=headers)

        # Check for possible errors
        if response.status_code == 200:
            try:
                auctions = response.json().get("auctions", None)
                if auctions is None:
                    print(f"Error: Auctions not found in response")
                else:
                    assert isinstance(auctions, list)
                    print(f"Active auctions retrieved successfully: {auctions}")
            except ValueError:
                print(f"Error: Response is not valid JSON")
        elif response.status_code == 404:
            print(f"Error: No active auctions found")
        elif response.status_code == 500:
            print(f"Error: Internal server error")
        else:
            print(f"Unexpected status code {response.status_code}")

    @task(1)
    def add_auction(self):
        headers = locustfile.create_header(self.session_token_user)
        with self.client.post(f"{locustfile.gacha_url}/roll", verify=False, headers=headers, catch_response=True) as response:
            if response.json().get("error") == "Insufficient funds for gacha roll":
                print("Insufficient funds for gacha roll")
                response.success()
            # Prepare data for adding a new auction
            data = {
                "gacha_id": response.json()["gacha_id"],
                "base_price": random.choice(range(1, 3))  # Random base price for testing
            }

            # Perform the add auction action
            response = self.client.post(f"{locustfile.auction_url}/add", json=data, verify=False, headers=headers)

            # Check for possible errors
            if response.status_code == 201:
                print(f"Auction locustfile.created successfully: {response.json()}")
            elif response.status_code == 400:
                print(f"Error: Missing data for new auction or failed to lock gacha")
            elif response.status_code == 403:
                error_message = response.json().get('error', '')
                if error_message == 'Only players can locustfile.create auctions':
                    print(f"Error: Only players can locustfile.create auctions")
                elif error_message == 'Unauthorized access':
                    print(f"Error: Unauthorized access")
                else:
                    print(f"Error: Forbidden action")
            elif response.status_code == 404:
                print(f"Error: Gacha is locked or does not exist")
            elif response.status_code == 500:
                print(f"Error: Internal server error")
            else:
                print(f"Unexpected status code {response.status_code}")

    @task
    def get_gacha_auctions(self):
        headers = locustfile.create_header(self.session_token_user)
        gacha_id = random.randint(1, 300)  # Assuming gacha_id ranges from 1 to 100

        # Perform the get gacha auctions action
        with self.client.get(f"{locustfile.auction_url}/get_gacha_auctions?gacha_id={gacha_id}", verify=False, headers=headers,
                             catch_response=True) as response:

            # Check for possible errors
            if response.status_code == 200:
                response.success()
            elif response.status_code == 400:
                print(f"Error: Missing gacha_id parameter")
            elif response.status_code == 404:
                response.success()
            elif response.status_code == 500:
                print(f"Error: Internal server error for gacha_id={gacha_id}")
            else:
                print(f"Unexpected status code {response.status_code} for gacha_id={gacha_id}")

    @task
    def all_my_auctions(self):
        headers = locustfile.create_header(self.session_token_user)

        # Perform the get all my auctions action
        response = self.client.get(f"{locustfile.auction_url}/my", verify=False, headers=headers)

        # Check for possible errors
        if response.status_code == 200:
            try:
                auctions = response.json()
                print(f"My auctions retrieved successfully: {auctions}")
            except ValueError:
                print(f"Error: Response is not valid JSON")
        elif response.status_code == 403:
            print(f"Error: Admins don't have auctions")
        elif response.status_code == 500:
            print(f"Error: Internal server error")
        else:
            print(f"Unexpected status code {response.status_code}")

    @task
    def get_auction(self):
        headers = locustfile.create_admin_header(self.admin_session_token)
        # Randomly choose to test with auction_id or user_id
        if random.choice([True, False]):

            with Lock():
                # if len(locustfile.all_auctions) == 0:
                response = self.client.get(f"{locustfile.admin_base}{locustfile.auction_url}/all?status=active",
                                           verify=False, headers=headers)

                locustfile.all_auctions = [id.get("auction_id") for id in response.json().get("auctions", [])]

                auction_id = locustfile.all_auctions[random.choice(range(0, len(locustfile.all_auctions)))]
                url = f"{locustfile.admin_base}{locustfile.auction_url}/get_auction?auction_id={auction_id}"
        else:
            url = f"{locustfile.admin_base}{locustfile.auction_url}/get_auction?user_id={self.user_id}"

        # Perform the get auction action
        with self.client.get(url, verify=False, headers=headers, catch_response=True) as response:

            # Check for possible errors
            if response.status_code == 200:
                try:
                    auction = response.json()
                    if "auctions" in auction:
                        assert isinstance(auction["auctions"], list)
                        print(f"Auctions retrieved successfully: {auction['auctions']}")
                    else:
                        assert "auction_id" in auction
                        print(f"Auction retrieved successfully: {auction}")
                except ValueError:
                    print(f"Error: Response is not valid JSON")
            elif response.status_code == 400:
                error_message = response.json().get('error', '')
                if error_message == "Both auction_id and user_id cannot be provided":
                    print(f"Error: Both auction_id and user_id cannot be provided")
                elif error_message == "Missing auction_id or user_id parameter":
                    print(f"Error: Missing auction_id or user_id parameter")
                else:
                    print(f"Error: Bad request")
            elif response.status_code == 404:
                response.success()
            elif response.status_code == 500:
                print(f"Error: Internal server error")
            else:
                print(f"Unexpected status code {response.status_code}")

    @task
    def update_auction(self):
        header = locustfile.create_admin_header(self.admin_session_token)
            # if len(locustfile.all_auctions) == 0:
        with self.client.get(f"{locustfile.admin_base}{locustfile.auction_url}/all?status=active",
                                   verify=False, headers=header, catch_response=True) as response:
            auction_id = [id.get("auction_id") for id in response.json().get("auctions", [])]
            if len(auction_id) == 0:
                print("No auction found for user")
                response.success()
            data = {
                "base_price": random.choice(range(3, 5)),  # Random base price for testing
            }
            # Perform the update auction action
            with self.client.put(f"{locustfile.admin_base}{locustfile.auction_url}/update?auction_id={random.choice(auction_id)}", json=data,
                                       verify=False, headers=header, catch_response=True) as response:

                # Check for possible errors
                if response.status_code == 200:
                    print(f"Auction updated successfully: {response.json()}")
                elif response.status_code == 400:
                    error_message = response.json().get('error', '')
                    if error_message == "Missing auction_id parameter":
                        print(f"Error: Missing auction_id parameter")
                    elif error_message == "Auction has finished":
                        print(f"Error: Auction has finished")
                    else:
                        print(f"Error: Failed to update auction")
                elif response.status_code == 403:
                    print(f"Error: You are not the seller of this auction")
                elif response.status_code == 404:
                    print(f"Error: Auction not found")
                elif response.status_code == 500:
                    print(f"Error: Internal server error")
                else:
                    print(f"Unexpected status code {response.status_code}")

    @task
    def place_bid(self):
        headers = locustfile.create_header(self.session_token_user)
        with Lock():
            # if len(locustfile.all_auctions) == 0:
            response = self.client.get(f"{locustfile.admin_base}{locustfile.auction_url}/all?status=active",
                                       verify=False, headers=locustfile.create_admin_header(self.admin_session_token))
            locustfile.all_auctions = [id.get("auction_id") for id in response.json().get("auctions", [])]
            data = {
                "auction_id": locustfile.all_auctions[random.choice(range(0, len(locustfile.all_auctions)))],
                # Random auction_id for testing
                "bid_amount": random.choice(range(3, 6))  # Random bid amount for testing
            }

        # Perform the place bid action
        with self.client.post(f"{locustfile.auction_url}/bid", json=data, verify=False, headers=headers,
                              catch_response=True) as response:

            # Check for possible errors
            if response.status_code == 200:
                response.success()
            elif response.status_code == 400:
                response.success()
            elif response.status_code == 403:
                error_message = response.json().get('error', '')
                if error_message == 'You cannot place a bid as an admin':
                    print(f"Error: You cannot place a bid as an admin")
                elif error_message == 'Insufficient funds':
                    print(f"Error: Insufficient funds")
                else:
                    print(f"Error: Forbidden action")
            elif response.status_code == 408:
                print(f"Error: Auction not found or already ended")
            elif response.status_code == 409:
                print(f"Error: Failed to place bid")
            elif response.status_code == 500:
                print(f"Error: Internal server error")
            else:
                print(f"Unexpected status code {response.status_code}")

    @task
    def get_bids(self):
        headers = locustfile.create_header(self.session_token_user)

        with Lock():
            response = self.client.get(f"{locustfile.admin_base}{locustfile.auction_url}/all?status=active",
                                       verify=False, headers=locustfile.create_admin_header(self.admin_session_token))
            locustfile.all_auctions = [id.get("auction_id") for id in response.json().get("auctions", [])]
        auction_id = locustfile.all_auctions[random.choice(range(0, len(locustfile.all_auctions)))]
        if len(locustfile.all_auctions) == 0:
            print("No auction found")
            response.success()
        # Perform the get bids action
        response = self.client.get(f"{locustfile.auction_url}/bids?auction_id={auction_id}", verify=False, headers=headers)

        # Check for possible errors
        if response.status_code == 200:
            try:
                bids = response.json().get("bids", None)
                if bids is None:
                    print(f"Error: Bids not found in response")
                else:
                    assert isinstance(bids, list)
                    print(f"Bids retrieved successfully for auction_id={auction_id}: {bids}")
            except ValueError:
                print(f"Error: Response is not valid JSON for auction_id={auction_id}")
        elif response.status_code == 400:
            print(f"Error: Missing auction_id parameter")
        elif response.status_code == 500:
            print(f"Error: Internal server error for auction_id={auction_id}")
        else:
            print(f"Unexpected status code {response.status_code} for auction_id={auction_id}")
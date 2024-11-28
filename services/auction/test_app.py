import datetime
import random
from locust import HttpUser, TaskSet, task, between
from locustfile import *
import locustfile

class GetAllAuctionsBehavior(TaskSet):

    @task
    def all_auctions(self):
        locustfile.admin_login(self)
        token = locustfile.admin_session_token[random.choice(range(0, 3))]
        headers = locustfile.create_header(token)
        status = random.choice(["all", "active", "expired", "completed"])  # Random status for testing
        
        # Perform the get all auctions action
        with self.client.get(f"{locustfile.admin_base}{locustfile.auction_url}/all?status={status}", headers=headers, catch_response=True) as response:

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
        locustfile.admin_login(self)
        token = locustfile.admin_session_token[random.choice(range(0, 3))]
        headers = locustfile.create_header(token)
        
        # Perform the get all active auctions action
        response = self.client.get(f"{locustfile.admin_base}{locustfile.auction_url}/all_active", headers=headers)
        
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

    #@task(2)
    def add_auction(self):
        #locustfile.login(self)
        token = locustfile.session_token[random.choice(range(0, 3))]
        headers = locustfile.create_header(token)
        response = self.client.post(f"{locustfile.gacha_url}/roll", headers = headers)
        # Prepare data for adding a new auction
        data = {
            "gacha_id": response.json()["gacha_id"],  # Assuming gacha_id ranges from 1 to 100
            "base_price": random.uniform(1, 2)  # Random base price for testing
        }
        
        # Perform the add auction action
        response = self.client.post(f"{locustfile.auction_url}/add", json=data, headers=headers)
        
        # Check for possible errors
        if response.status_code == 201:
            print(f"Auction created successfully: {response.json()}")
        elif response.status_code == 400:
            print(f"Error: Missing data for new auction or failed to lock gacha")
        elif response.status_code == 403:
            error_message = response.json().get('error', '')
            if error_message == 'Only players can create auctions':
                print(f"Error: Only players can create auctions")
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
        locustfile.login(self)
        token = locustfile.session_token[random.choice(range(0, 3))]
        headers = locustfile.create_header(token)
        gacha_id = random.randint(1, 300)  # Assuming gacha_id ranges from 1 to 100
        
        # Perform the get gacha auctions action
        with self.client.get(f"{locustfile.auction_url}/get_gacha_auctions?gacha_id={gacha_id}", headers=headers, catch_response=True) as response:
        
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
        locustfile.login(self)
        token = locustfile.session_token[random.choice(range(0, 3))]
        headers = locustfile.create_header(token)
        
        # Perform the get all my auctions action
        response = self.client.get(f"{locustfile.auction_url}/my", headers=headers)
        
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
        locustfile.admin_login(self)
        token = locustfile.admin_session_token[random.choice(range(0, 3))]
        headers = locustfile.create_header(token)
        # Randomly choose to test with auction_id or user_id
        if random.choice([True, False]) or True:
            
            with Lock():
                #if len(locustfile.all_auctions) == 0:
                locustfile.admin_login(self)
                response = self.client.get(f"{locustfile.admin_base}{locustfile.auction_url}/all?status=active", headers=headers)
                print("Buccio1: ", response.json())
                locustfile.all_auctions = [id.get("auction_id") for id in response.json().get("auctions", [])]
                print("Buccio: ", locustfile.all_auctions)
                auction_id = locustfile.all_auctions[random.choice(range(0, len(locustfile.all_auctions)))]
                url = f"{locustfile.admin_base}{locustfile.auction_url}/get_auction?auction_id={auction_id}"
        else:
            usr_id = random.choice(locustfile.user_id)
            url = f"{locustfile.admin_base}{locustfile.auction_url}/get_auction?user_id={usr_id}"
        
        # Perform the get auction action
        with self.client.get(url, headers=headers, catch_response=True) as response:
        
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
    ##@task
    def update_auction(self):
        locustfile.login(self)
        token = locustfile.session_token[random.choice(range(0, 3))]
        headers = locustfile.create_header(token)
        
        # Prepare data for updating an auction
        auction_id = random.randint(1, 100)  # Assuming auction_id ranges from 1 to 100
        data = {
            "base_price": random.uniform(10, 1000),  # Random base price for testing
            "end_time": (datetime.now() + datetime.timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')  # New end time
        }
        
        # Perform the update auction action
        response = self.client.put(f"{locustfile.auction_url}/update?auction_id={auction_id}", json=data, headers=headers)
        
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

    ##@task
    def delete_auction(self):
        locustfile.admin_login(self)
        token = locustfile.admin_session_token[random.choice(range(0, 3))]
        headers = locustfile.create_header(token)
        
        # Prepare data for deleting an auction
        gacha_id = random.randint(1, 100)  # Assuming gacha_id ranges from 1 to 100
        
        # Perform the delete auction action
        response = self.client.delete(f"{locustfile.auction_url}/delete?gacha_id={gacha_id}", headers=headers)
        
        # Check for possible errors
        if response.status_code == 200:
            print(f"Auction deleted successfully: {response.json()}")
        elif response.status_code == 400:
            print(f"Error: Missing gacha_id parameter or failed to delete auction")
        elif response.status_code == 404:
            print(f"Error: Auction not found for gacha_id={gacha_id}")
        elif response.status_code == 500:
            print(f"Error: Internal server error for gacha_id={gacha_id}")
        else:
            print(f"Unexpected status code {response.status_code} for gacha_id={gacha_id}")

class PlaceBidBehavior(TaskSet):

    @task
    def place_bid(self):
        locustfile.login(self)
        token = locustfile.session_token[random.choice(range(0, 3))]
        headers = locustfile.create_header(token)
        with Lock():
            
            # if len(locustfile.all_auctions) == 0:
            locustfile.admin_login(self)
            response = self.client.get(f"{locustfile.admin_base}{locustfile.auction_url}/all?status=active", headers=locustfile.create_admin_header(locustfile.admin_session_token[random.choice(range(0, 3))]))
            locustfile.all_auctions = [id.get("auction_id") for id in response.json().get("auctions", [])]
            print("AAAAA: ", locustfile.all_auctions)
            data = {
                "auction_id": locustfile.all_auctions[random.choice(range(0, len(locustfile.all_auctions)))],  # Random auction_id for testing
                "bid_amount": random.uniform(3, 4)  # Random bid amount for testing
            }
        
        # Perform the place bid action
        response = self.client.post(f"{locustfile.auction_url}/bid", json=data, headers=headers)
        
        # Check for possible errors
        if response.status_code == 200:
            print(f"Bid placed successfully: {response.json()}")
        elif response.status_code == 400:
            print(f"Error: Missing data for bid or bid amount must be higher than current highest bid")
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

    ##@task
    def get_bids(self):
        locustfile.login(self)
        token = locustfile.session_token[random.choice(range(0, 3))]
        headers = locustfile.create_header(token)
        auction_id = random.randint(1, 100)  # Assuming auction_id ranges from 1 to 100
        
        # Perform the get bids action
        response = self.client.get(f"{locustfile.auction_url}/bids?auction_id={auction_id}", headers=headers)
        
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

    ##@task
    def get_highest_bid(self):
        locustfile.admin_login(self)
        token = locustfile.admin_session_token[random.choice(range(0, 3))]
        headers = locustfile.create_header(token)
        gacha_id = random.randint(1, 100)  # Assuming gacha_id ranges from 1 to 100
        
        # Perform the get highest bid action
        response = self.client.get(f"{locustfile.auction_url}/highest_bid?gacha_id={gacha_id}", headers=headers)
        
        # Check for possible errors
        if response.status_code == 200:
            try:
                highest_bid = response.json()
                assert "auction" in highest_bid
                assert "highest_bid" in highest_bid
                assert "buyer_id" in highest_bid
                print(f"Highest bid retrieved successfully for gacha_id={gacha_id}: {highest_bid}")
            except ValueError:
                print(f"Error: Response is not valid JSON for gacha_id={gacha_id}")
        elif response.status_code == 400:
            print(f"Error: Missing gacha_id parameter")
        elif response.status_code == 404:
            print(f"Error: Auction not found for gacha_id={gacha_id}")
        elif response.status_code == 500:
            print(f"Error: Internal server error for gacha_id={gacha_id}")
        else:
            print(f"Unexpected status code {response.status_code} for gacha_id={gacha_id}")

class GetAllAuctionsTest(HttpUser):
    tasks = [GetAllAuctionsBehavior, PlaceBidBehavior]
    wait_time = between(1, 5)
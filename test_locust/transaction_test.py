import random

from locust import HttpUser, TaskSet, task, between

import locustfile


class GetTransactionBehavior(TaskSet):

    @task
    def get_transaction(self):
        locustfile.login(self)
        token = locustfile.session_token[random.choice(range(0, 3))]
        headers = locustfile.create_header(token)
        transaction_id = random.randint(1, 10)  # Assuming transaction_id ranges from 1 to 100
        
        # Perform the get transaction action
        response = self.client.get(f"{locustfile.user_player}/get_transaction?transaction_id={transaction_id}", verify=False, headers=headers)
        
        # Check for possible errors
        if response.status_code == 200:
            try:
                transaction = response.json()
                assert "transaction_id" in transaction
                print(f"Transaction retrieved successfully: {transaction}")
            except ValueError:
                print(f"Error: Response is not valid JSON for transaction_id={transaction_id}")
        elif response.status_code == 400:
            print(f"Error: Missing transaction_id parameter")
        elif response.status_code == 404:
            print(f"Error: Transaction not found for transaction_id={transaction_id}")
        elif response.status_code == 500:
            print(f"Error: Internal server error for transaction_id={transaction_id}")
        else:
            print(f"Unexpected status code {response.status_code} for transaction_id={transaction_id}")

    @task
    def get_user_transactions(self):
        locustfile.login(self)
        token = locustfile.session_token[random.choice(range(0, 3))]
        headers = locustfile.create_header(token)
        
        # Perform the get user transactions action
        response = self.client.get(f"{locustfile.user_player}/get_user_transactions", verify=False, headers=headers)
        
        # Check for possible errors
        if response.status_code == 200:
            try:
                transactions = response.json()
                assert isinstance(transactions, list)
                print(f"User transactions retrieved successfully: {transactions}")
            except ValueError:
                print(f"Error: Response is not valid JSON")
        elif response.status_code == 403:
            print(f"Error: You don't have a transaction history (as an ADMIN)")
        elif response.status_code == 500:
            print(f"Error: Internal server error")
        else:
            print(f"Unexpected status code {response.status_code}")

    @task
    def get_all_transactions(self):
        locustfile.login(self)
        token = locustfile.session_token[random.choice(range(0, 3))]
        headers = locustfile.create_header(token)
        
        # Perform the get all transactions action
        response = self.client.get(f"{locustfile.user_player}/all", verify=False, headers=headers)
        
        # Check for possible errors
        if response.status_code == 200:
            try:
                transactions = response.json()
                assert isinstance(transactions, list)
                print(f"All transactions retrieved successfully: {transactions}")
            except ValueError:
                print(f"Error: Response is not valid JSON")
        elif response.status_code == 404:
            print(f"Error: No transactions found")
        elif response.status_code == 500:
            print(f"Error: Internal server error")
        else:
            print(f"Unexpected status code {response.status_code}")

class GetTransactionTest(HttpUser):
    tasks = [GetTransactionBehavior]
    wait_time = between(1, 5)
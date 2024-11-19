# create an hello world endpoint

import logging
from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

gacha_url = "http://gacha:5000"
user_url = "http://user_player:5000"
dbm_url = "http://db-manager:5000"
transaction_url = "http://transaction:5000"

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# make a function that take json data and return a response
def send_response(message, status_code):
    return jsonify(message), status_code

# A function that adds a transaction to the transaction service
def create_transaction(user_id, amount, transaction_type):
    try:
        response = requests.post(f"{transaction_url}/add_transaction",
                                 json={"user_id": user_id, "amount": amount, "type": transaction_type})
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Error creating transaction: {e}")
        return None
    return response

# make a function that ask to the service gacha the list of all my gacha inside the db of gacha user inventory
@app.route("/my_gacha_list/<user_id>")
def my_gacha_list(user_id):
    try:
        response = requests.get(f"{gacha_url}/inventory", params={"user_id": user_id})
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Error retrieving gacha list for user {user_id}: {e}")
        return send_response({"error": "Failed to retrieve gacha list"}, 500)
    return send_response(response.json(), 200)

# function to ask for the information of a specific gacha for that user
@app.route("/gacha/<user_id>/<gacha_id>")
def gacha_info(user_id, gacha_id):
    try:
        response = requests.get(
            f"{gacha_url}/my_gacha", params={"user_id": user_id, "gacha_id": gacha_id}
        )
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Error retrieving gacha info for user {user_id} and gacha {gacha_id}: {e}")
        return send_response({"error": "Failed to retrieve gacha info"}, 500)
    return send_response(response.json(), 200)

def update_user_balance(user_id, amount, type):
    try:
        response = requests.put(
            f"{dbm_url}/update_balance/PLAYER",
            json={"user_id": user_id, "amount": amount, "type": type},
        )
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Error updating user balance for user {user_id}: {e}")
        return None
    return response

@app.route("/real_money_transaction", methods=["POST"])
def real_money_transaction():
    data = request.get_json()
    user_id = data.get("user_id")
    amount = data.get("amount")

    if not user_id or amount is None:
        logging.error("Missing user_id or amount in request")
        return send_response({"error": "Missing user_id or amount in request"}, 400)

    if amount < 0:
        logging.error("Negative amount in request")
        return send_response({"error": "Amount cannot be negative"}, 400)

    # Update the user's balance
    if update_user_balance(user_id, amount, "credit") is None:
        return send_response({"error": "Failed to update user balance"}, 500)

    if create_transaction(user_id, amount, "top_up") is None:
        return send_response({"error": "Failed to create transaction"}, 500)

    return send_response({"message": "Transaction added successfully"}, 200)

# function to get the user balance information
@app.route("/get_user_balance/<user_id>")
def get_user_balance(user_id):
    try:
        response = requests.get(f"{dbm_url}/balance/PLAYER", params={"user_id": user_id})
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Error retrieving user balance for user {user_id}: {e}")
        return send_response({"error": "Failed to retrieve user balance"}, 500)
    return send_response(response.json(), 200)

@app.route("/get_user/<user_id>")
def get_user(user_id):
    url = f"{dbm_url}/get_user/" + user_id
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Error retrieving user info for user {user_id}: {e}")
        return send_response({"error": "Failed to retrieve user info"}, 500)
    return send_response(response.json(), response.status_code)

@app.route("/update_balance/<user_type>", methods=['PUT'])
def update_balance(user_type):
    user_id = request.json['user_id']
    amount = request.json['amount']
    type = request.json['type']

    url = f"{dbm_url}/update_balance/" + user_type
    data = {
        "user_id": user_id,
        "amount": amount,
        "type": type
    }
    logging.debug("Sending data: %s", data)
    try:
        response = requests.put(url, json=data)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Error updating balance for user {user_id}: {e}")
        return send_response({"error": "Failed to update balance"}, 500)
    return send_response(response.json(), response.status_code)

if __name__ == "__main__":
    app.run()

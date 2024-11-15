# create an hello world endpoint

import logging
from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

gacha_url = "http://gacha:5000"
user_url = "http://user_player:5000"
dbm_url = "http://db-manager:5000"
transaction_url = "http://transaction:5000"


# A function that adds a transaction to the transaction service
def create_transaction(user_id, amount, transaction_type):
    response = requests.post(f"{transaction_url}/add_transaction/",
                             json={"user_id": user_id, "amount": amount, "type": transaction_type})
    return response


# make a function that ask to the service gacha the list of all my gacha inside the db of gacha user invetory
@app.route("/my_gacha_list/<user_id>")
def my_gacha_list(user_id):
    response = requests.get(f"{gacha_url}/inventory", params={"user_id": user_id})
    if response.status_code == 200:
        return response.json()
    else:
        return "Failed to retrieve gacha list", response.status_code


# DA CONTROLLARE
# function to ask for the information of a specific gacha for that user
@app.route("/gacha/<user_id>/<gacha_id>")
def gacha_info(user_id, gacha_id):
    response = requests.get(
        f"{gacha_url}/my_gacha", params={"user_id": user_id, "gacha_id": gacha_id}
    )
    if response.status_code == 200:
        return response.json()
    else:
        return "Failed to retrieve gacha list", response.status_code


def update_user_balance(user_id, amount, type):
    response = requests.put(
        f"{dbm_url}/update_balance/PLAYER",
        json={"user_id": user_id, "amount": amount, "type": type},
    )
    return response


@app.route("/real_money_transaction", methods=["POST"])
def real_money_transaction():
    """
    Handle real money transactions.
    This endpoint processes a real money transaction by updating the user's balance
    and recording the transaction in the database.
    Request JSON format:
    {
        "user_id": str,
        "amount": float
    }
    Returns:
        Response: A JSON response indicating success or failure of the transaction.
        - 200: Transaction added successfully.
        - 400: Failed to update user balance.
    """
    data = request.get_json()
    user_id = data.get("user_id")
    amount = data.get("amount")

    if not user_id or amount is None:
        return jsonify({"error": "Missing user_id or amount in request"}), 400

    # Update the user's balance
    if update_user_balance(user_id, amount, "auction_credit").status_code != 200:
        return jsonify({"error": "Failed to update user balance"}), 400

    if create_transaction(user_id, amount, "real_money").status_code != 200:
        return jsonify({"error": "Failed to create transaction"}), 400

    return jsonify({"message": "Transaction added successfully"}), 200


# function to get the user balance information
@app.route("/get_user_balance/<user_id>")
def get_user_balance(user_id):
    response = requests.get(f"{dbm_url}/balance/PLAYER", params={"user_id": user_id})
    if response.status_code == 200:
        return response.json()
    else:
        return jsonify({"error": "Failed to retrieve user balance"}), response.status_code


if __name__ == "__main__":
    app.run()


@app.get("/get_user/<user_id>")
def get_user(user_id):
    url = f"{dbm_url}/get_user/" + user_id
    response = requests.get(url)
    return response.json()


@app.route("/update_balance/<user_type>", methods=['PUT'])
def update_balance(user_type):
    """
    Update the balance of a user.

    This endpoint updates the balance of a user by sending a PUT request to the db-manager service.

    Request JSON format:
    {
        "user_id": str,
        "new_balance": float
    }

    Returns:
        Response: A JSON response from the db-manager service indicating the result of the update.
    """
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
    response = requests.put(url, json=data)
    return response.json()

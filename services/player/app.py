# create an hello world endpoint

import logging
from flask import Flask, jsonify, request
import requests


app = Flask(__name__)

gacha_url = "http://gacha:5000"
user_url = "http://user_player:5000"


# make a function that ask to the service gacha the list of all my gacha inside the db of gacha user invetory
@app.route("/my_gacha_list/<user_id>")
def gacha(user_id):
    response = requests.get(f"{gacha_url}/my_gacha_list", params={"user_id": user_id})
    if response.status_code == 200:
        return response.json()
    else:
        return "Failed to retrieve gacha list", response.status_code


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
    """
    Updates the balance of a user by sending a PUT request to the user service.

    Args:
        user_id (int): The ID of the user whose balance is to be updated.
        amount (float): The amount to update the user's balance by.
        type (str): The type of transaction (e.g., 'credit' or 'debit').

    Returns:
        Response: The response object from the PUT request.
    """
    response = requests.put(
        f"{user_url}/users/", json={"user_id": user_id, "amount": amount, "type": type}
    )
    return response


def update_user_balance(user_id, amount, type):
    """
    Updates the balance of a user by sending a PUT request to the user service.

    Args:
        user_id (int): The ID of the user whose balance is to be updated.
        amount (float): The amount to update the user's balance by.
        type (str): The type of transaction (e.g., 'credit' or 'debit').

    Returns:
        Response: The response object from the PUT request.
    """
    response = requests.put(
        f"{user_url}/update_balance/PLAYER/",
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
    if update_user_balance(user_id, amount, "credit").status_code != 200:
        return jsonify({"error": "Failed to update user balance"}), 400

    return jsonify({"message": "Transaction added successfully"}), 200


if __name__ == "__main__":
    app.run()


@app.get("/get_user/<user_id>")
def get_user(user_id):
    url = f"http://db-manager:5000/get_user/" + user_id
    response = requests.get(url)
    return response.json()


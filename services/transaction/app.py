import logging
from flask import Flask, request, jsonify
import sqlite3
import hashlib
import uuid

import requests

# Configura il logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

DATABASE = "./transactions.db/transactions.db"
user_url = "http://user_player:5000"


# Helper function to connect to the database
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/add_transaction", methods=["POST"])
def add_transaction():
    """
    Add a new transaction to the database.
    This endpoint handles POST requests to add a new transaction. The transaction type is derived based on the service 
    path in the request URL. The transaction details are then inserted into the TRANSACTIONS table in the database.
    Returns:
        JSON response with a success message and HTTP status code 200.
    Request Body (JSON):
        user_id (str): The ID of the user making the transaction.
        type (str): The type of the transaction (only used if the path contains "auction").
        amount (float): The amount of the transaction.
    Example:
        POST /add_transaction
        {
            "user_id": "12345",
            "type": "bid",
            "amount": 100.0
        }
    Response:
        {
            "message": "Transaction added successfully"
        }
    """
    data = request.get_json()
    logging.debug(data)
    conn = get_db_connection()
    cursor = conn.cursor()
    transaction_id = str(uuid.uuid4())
    # Derive transaction type based on the service
    if "auction" in request.path:
        transaction_type = "auction" + data["type"]
    elif "gacha" in request.path:
        transaction_type = "roll"
    elif "user" in request.path:
        transaction_type = "real_money"
    else:
        transaction_type = "unknown"

    

    cursor.execute(
        "INSERT INTO TRANSACTIONS (transaction_id, user_id, transaction_type, amount) VALUES (?, ?, ?, ?)",
        (transaction_id, data["user_id"], transaction_type, data["amount"]),
    )

    # Log the derived transaction type
    logging.debug(f"Derived transaction type: {transaction_type}")
    conn.commit()
    conn.close()
    return jsonify({"message": "Transaction added successfully"}), 200


@app.route("/get_transaction", methods=["GET"])
def get_transaction():
    """
    Retrieve a transaction by its ID.
    This endpoint expects a GET request with a 'transaction_id' parameter.
    It queries the database for a transaction with the given ID and returns
    the transaction details in JSON format if found.
    Returns:
        Response: A JSON response containing the transaction details with a 200 status code
                if the transaction is found.
                A JSON response with an error message and a 400 status code if the
                'transaction_id' parameter is missing.
                A JSON response with an error message and a 404 status code if the
                transaction is not found.
    """
    transaction_id = request.args.get("transaction_id")
    if not transaction_id:
        return jsonify({"error": "Missing transaction_id parameter"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM TRANSACTIONS WHERE transaction_id = ?", (transaction_id,)
    )
    transaction = cursor.fetchone()
    conn.close()

    if transaction:
        return jsonify(dict(transaction)), 200
    else:
        return jsonify({"error": "Transaction not found"}), 404


# Endpoint to retrieve all transactions for a specific user
@app.route("/get_user_transactions", methods=["GET"])
def get_user_transactions():
    """
    Endpoint to retrieve transactions for a specific user.
    This endpoint handles GET requests to fetch all transactions associated with a given user ID.
    The user ID must be provided as a query parameter.
    Returns:
        JSON response containing a list of transactions if found, or an error message if no transactions are found or if the user_id parameter is missing.
    Query Parameters:
        user_id (str): The ID of the user whose transactions are to be retrieved.
    Responses:
        200: A JSON array of transactions for the specified user.
        400: A JSON error message indicating that the user_id parameter is missing.
        404: A JSON error message indicating that no transactions were found for the specified user.
    """
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id parameter"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM TRANSACTIONS WHERE user_id = ?", (user_id,))
    transactions = cursor.fetchall()
    conn.close()

    if transactions:
        return jsonify([dict(transaction) for transaction in transactions]), 200
    else:
        return jsonify({"error": "No transactions found for the user"}), 404

# Run the Flask app on the specified port
if __name__ == "__main__":
    app.run()

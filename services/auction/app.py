import logging
from time import strftime

from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime, timedelta
import uuid

import requests

app = Flask(__name__)
DATABASE = "./auction.db/auction.db"
gacha_url = "http://gacha:5000"
user_url = "http://user_player:5000"
transaction_url = "http://transaction:5000"

logging.basicConfig(level=logging.DEBUG)


# Helper function to connect to the database
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# write a function that sends user id and gacha id to the gacha service to check if the gacha is locked using GET request
def is_gacha_unlocked(user_id, gacha_id):
    response = requests.get(f"{gacha_url}/is_gacha_unlocked/{user_id}/{gacha_id}")
    if response.status_code == 200:
        return True
    return False


# write a function fos sand an update request to the gacha service to lock or unlock gatcha
def update_gacha_status(user_id, gacha_id, status):
    response = requests.put(f"{gacha_url}/update_gacha_status",
                            json={"user_id": user_id, "gacha_id": gacha_id, "status": status})
    return response


def update_gacha_owner(buyer_id, gacha_id, seller_id, status):
    response = requests.put(f"{gacha_url}/update_gacha_owner",
                            json={"buyer_id": buyer_id, "seller_id": seller_id, "gacha_id": gacha_id, "status": status})
    return response


def create_transaction(user_id, amount, transaction_type):
    response = requests.post(f"{transaction_url}/add_transaction",
                             json={"user_id": user_id, "amount": amount, "type": transaction_type})
    return response


def update_user_balance(user_id, amount, type):
    response = requests.put(f"{user_url}/update_balance/PLAYER",
                            json={"user_id": user_id, "amount": amount, "type": type})
    return response


# write a function that sends a get request to user service to get the user's balance if the user exists
def get_user_balance(user_id):
    response = requests.get(f"{user_url}/get_user_balance/{user_id}")
    a = response
    logging.debug(a)
    if response.status_code == 200:
        return a.json().get("currency_balance")
    else:
        return jsonify({"error": "User not found"}), 408


# Endpoint to add a new auction
@app.route("/add", methods=["POST"])
def add_auction():
    # Extract auction details from the request JSON
    data = request.get_json()
    gacha_id = data.get("gacha_id")
    seller_id = data.get("seller_id")
    base_price = data.get("base_price")

    # Check if all required fields are provided
    if not all([gacha_id, base_price, seller_id]):
        return jsonify({"error": "Missing data for new auction"}), 400

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # VERIFY IF THE GACHA EXIST AND IF ITS NOT LOCKED
    # Make a GET request to the Gacha service to verify the gacha
    if is_gacha_unlocked(seller_id, gacha_id):
        # Insert the new auction record
        auction_id = str(uuid.uuid4())
        end_time = (datetime.now() + timedelta(hours=6)).timestamp()

        if update_gacha_status(seller_id, gacha_id, "locked").status_code == 200:

            cursor.execute(
                "INSERT INTO Auctions (auction_id, gacha_id, seller_id, base_price, highest_bid, buyer_id, status, end_time) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (auction_id, gacha_id, seller_id, base_price, 0, None, "active", end_time),
            )

            # UPDATE GACHA INVENTORY WITH BLOCKED GACHA

            conn.commit()
            conn.close()

            return (
                jsonify({"message": "Auction created successfully", "auction_id": auction_id}),
                201,
            )
        else:
            return jsonify({"error": "Failed to lock gacha"}), 400
    else:
        return jsonify({"error": "Gacha is locked"}), 400


# End the auction if the end time has passed and update the status to completed if user id not equal to None
# or expired if user id is None

# write a function that checks if the auction has ended and if it has, update the status to expired
def check_auction_status():
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    logging.debug("Inside check auction status. Before query")
    # Retrieve all active auctions that have ended

    cursor.execute(
        "SELECT * FROM Auctions WHERE status = 'active'"
    )

    # stampa la query che è stata eseguita
    # logging.debug("SELECT * FROM Auctions WHERE status = 'active')
    auctions = cursor.fetchall()

    today = datetime.now().timestamp()
    # Update the status of each expired auction
    logging.debug("Current datetime is: %s", datetime.now().timestamp())
    for auction in auctions:
        # from timestamp to datetime
        end_time = auction["end_time"]
        logging.debug("End time is: %s", end_time)

        # Confronta end_time con l'ora attuale
        if not (today > end_time):
            continue

        logging.debug(f"Inside check auction status. Auction ({auction['auction_id']}) ended")
        if auction["highest_bid"] > 0:
            cursor.execute(
                "UPDATE Auctions SET status = 'completed' WHERE auction_id = ?",
                (auction["auction_id"],),
            )
            # UPDATE THE owner of the gacha
            if update_gacha_owner(auction['buyer_id'], auction['gacha_id'], auction['seller_id'],
                                  "unlocked").status_code != 200:
                return jsonify({"error": "Failed to unlock gacha"}), 400

            logging.debug("Inside check auction status. Owner updated")

            # UPDATE THE SELLER'S BALANCE WITH POST TO USER SERVICE
            if update_user_balance(auction['seller_id'], auction['highest_bid'], "auction_credit").status_code != 200:
                return jsonify({"error": "Failed to update seller's balance"}), 400
            # MAKE POST REQUEST TO TRANSACTION

            logging.debug("Inside check auction status. Seller balance updated")

            if create_transaction(auction['seller_id'], auction['highest_bid'], "auction_credit").status_code != 200:
                return jsonify({"error": "Failed to create transaction"}), 400

            logging.debug("Inside check auction status. Transaction created")

            if create_transaction(auction['buyer_id'], auction['highest_bid'], "auction_debit").status_code != 200:
                return jsonify({"error": "Failed to create transaction"}), 400

            logging.debug("Inside check auction status. Transaction created")

        else:
            cursor.execute(
                "UPDATE Auctions SET status = 'expired' WHERE auction_id = ?",
                (auction["auction_id"],),
            )
            if update_gacha_status(auction['seller_id'], auction['gacha_id'], "unlocked").status_code != 200:
                return jsonify({"error": "Failed to unlock gacha"}), 400

    conn.commit()
    conn.close()

    return jsonify({"message": "Auction status updated successfully"}), 200


# Endpoint to retrieve all active or expired auctions
@app.route("/all", methods=["GET"])
def get_all_auctions():
    """
    Retrieve all auctions or filter by auction status.
    This endpoint retrieves all auctions from the database. Optionally, it can filter
    the auctions based on their status (active or expired) using a query parameter.
    Query Parameters:
        status (str, optional): The status of the auctions to filter by. Can be "active" or "expired".
    Returns:
        Response: A JSON response containing a list of auctions. Each auction is represented
        as a dictionary. The response status code is 200.
    Example:
        GET /all
        GET /all?status=active
        GET /all?status=expired
    """
    # Optional query parameter to filter by auction status (active or expired)
    status = request.args.get("status")

    conn = get_db_connection()
    cursor = conn.cursor()

    # If status filter is provided, retrieve only the matching auctions
    if status == "active":
        cursor.execute(
            "SELECT * FROM Auctions WHERE status = 'active'",
        )
    elif status == "expired":
        cursor.execute(
            "SELECT * FROM Auctions WHERE status = 'expired'"
        )
    else:
        # If no status filter is provided, return all auctions
        cursor.execute("SELECT * FROM Auctions")

    auctions = cursor.fetchall()
    conn.close()

    # Format the auctions for JSON response
    result = [dict(auction) for auction in auctions]
    return jsonify({"auctions": result}), 200


# Endpoint to retrieve all auctions for a specific gacha
@app.route('/get_gacha_auctions', methods=['GET'])
def get_gacha_auctions():
    """
    Endpoint to retrieve gacha auctions based on gacha_id.
    This endpoint handles GET requests to fetch auctions associated with a specific gacha_id.
    If the gacha_id parameter is missing, it returns a 400 error with a message indicating the missing parameter.
    If auctions are found for the given gacha_id, it returns a JSON list of auctions with a 200 status code.
    If no auctions are found, it returns a 404 error with a message indicating no auctions were found.
    Returns:
        Response: JSON response containing the list of auctions or an error message with the appropriate HTTP status code.
    """
    gacha_id = request.args.get('gacha_id')
    if not gacha_id:
        return jsonify({'error': 'Missing gacha_id parameter'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM AUCTIONS WHERE gacha_id = ?", (gacha_id,))
    auctions = cursor.fetchall()
    conn.close()

    if auctions:
        return jsonify([dict(auction) for auction in auctions]), 200
    else:
        return jsonify({'error': 'No auctions found for the gacha'}), 408


# Fuctions for Bidding
# Endpoint to place a bid on an auction
@app.route("/bid", methods=["POST"])
def place_bid():
    check_auction_status()
    """
    Place a bid on an auction.
    Endpoint: /bid
    Method: POST
    Request JSON:
    {
        "auction_id": str,  # ID of the auction
        "user_id": str,     # ID of the user placing the bid
        "bid_amount": float # Amount of the bid
    }
    Responses:
    - 200 OK: Bid placed successfully.
    {
        "message": "Bid placed successfully"
    }
    - 400 Bad Request: Missing data for bid or bid amount is not higher than current highest bid.
    {
        "error": "Missing data for bid"
    }
    or
    {
        "error": "Bid amount must be higher than current highest bid"
    }
    - 403 Forbidden: Insufficient funds.
    {
        "error": "Insufficient funds"
    }
    - 404 Not Found: Auction not found or already ended.
    {
        "error": "Auction not found or already ended"
    }
    Functionality:
    - Extracts bid details from the request JSON.
    - Validates that all required fields are provided.
    - Connects to the database and checks if the auction exists and is active.
    - Validates that the bid amount is higher than the current highest bid.
    - Checks if the user has enough funds for the bid.
    - Updates the auction with the new highest bid.
    - Updates the user balances accordingly.
    - Inserts the bid into the Bids database.
    - Returns a JSON response indicating the result of the bid placement.
    """
    # Extract bid details from the request JSON
    data = request.get_json()
    auction_id = data.get("auction_id")
    user_id = data.get("user_id")
    bid_amount = data.get("bid_amount")

    # Check if all required fields are provided
    if not all([auction_id, user_id, bid_amount]):
        return jsonify({"error": "Missing data for bid"}), 400

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the auction exists and is active
    cursor.execute(
        "SELECT * FROM Auctions WHERE auction_id = ? AND status = 'active'",
        (auction_id,),
    )
    auction = cursor.fetchone()

    if not auction:
        conn.close()
        return jsonify({"error": "Auction not found or already ended"}), 408

    # Check if the bid amount is higher than the current highest bid
    if int(bid_amount) < (auction["highest_bid"]):
        conn.close()
        return (
            jsonify({"error": "Bid amount must be higher than current highest bid"}),
            400,
        )

    # Check if the user has enough funds for the bid
    user_balance = (get_user_balance(user_id))
    if int(user_balance) < int(bid_amount):
        conn.close()
        return jsonify({"error": "Insufficient funds"}), 403

    # Update the auction with the new highest bid

    # sand back money to previous buyer
    update_user_balance(auction['buyer_id'], auction['highest_bid'], "auction_credit")
    # block money from new buyer
    update_user_balance(user_id, bid_amount, "auction_debit")
    # update auction
    cursor.execute(
        "UPDATE Auctions SET highest_bid = ?, buyer_id = ? WHERE auction_id = ?",
        (int(bid_amount), user_id, auction_id),
    )

    # insert in bids db the bid
    bid_id = str(uuid.uuid4())
    bid_time = datetime.now()
    cursor.execute(
        "INSERT INTO Bids (bid_id, auction_id, user_id, bid_amount, bid_time) VALUES (?, ?, ?, ?, ?)",
        (bid_id, auction_id, user_id, bid_amount, bid_time),
    )
    conn.commit()
    conn.close()
    if not cursor.rowcount:
        return jsonify({"error": "Failed to place bid"}), 500
    return jsonify({"message": "Bid placed successfully"}), 200


# Endpoint to retrieve all bids for a specific auction
@app.route("/bids", methods=["GET"])
def get_bids():
    """
    Endpoint to retrieve bids for a specific auction.
    This endpoint handles GET requests to the /bids route. It expects an 
    auction_id parameter to be provided in the query string. If the 
    auction_id parameter is missing, it returns a 400 error with a 
    message indicating the missing parameter. 
    The function connects to the database, retrieves all bids associated 
    with the given auction_id, and returns them in JSON format.
    Returns:
        Response: A JSON response containing the list of bids for the 
        specified auction_id, or an error message if the auction_id 
        parameter is missing.
    """
    auction_id = request.args.get("auction_id")
    if not auction_id:
        return jsonify({"error": "Missing auction_id parameter"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Bids WHERE auction_id = ?", (auction_id,))
    bids = cursor.fetchall()
    conn.close()

    result = [dict(bid) for bid in bids]
    return jsonify({"bids": result}), 200


# Run the Flask app on the specified port
if __name__ == "__main__":
    app.run()

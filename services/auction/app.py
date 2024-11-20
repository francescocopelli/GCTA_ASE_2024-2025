import logging
import os
from time import strftime
from flask import Flask, request, jsonify
import sqlite3
import uuid
from datetime import datetime, timedelta

import requests
from flask import Flask, request, jsonify

from shared.auth_middleware import *

app = Flask(__name__)

print(SECRET_KEY)
app.config['SECRET_KEY'] = SECRET_KEY
DATABASE = "./auction.db/auction.db"
gacha_url = "http://gacha:5000"
user_url = "http://user_player:5000"
transaction_url = "http://transaction:5000"

logging.basicConfig(level=logging.DEBUG)

    
# Helper function to connect to the database
def get_db_connection():
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        logging.debug("Database connection established")
        return conn
    except sqlite3.Error as e:
        logging.error(f"Database connection error: {e}")
        return None


# Function to check if the gacha is unlocked
def is_gacha_unlocked(user_id, gacha_id):
    try:
        response = requests.get(f"{gacha_url}/is_gacha_unlocked/{user_id}/{gacha_id}", headers=generate_session_token_system())
        response.raise_for_status()
        logging.debug(f"Response from gacha service: {response.json()}")
        return True
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        return False
    except Exception as err:
        logging.error(f"Other error occurred: {err}")
        return False

# Function to update gacha status
def update_gacha_status(user_id, gacha_id, status):
    try:
        response = requests.put(f"{gacha_url}/update_gacha_status",
                                json={"user_id": user_id, "gacha_id": gacha_id, "status": status}, headers=generate_session_token_system())
        response.raise_for_status()
        logging.debug(f"Response from gacha service: {response.json()}")
        return send_response(response.json(),200)
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        return send_response({"error": "Failed to update gacha status"}, 408)
    except Exception as err:
        logging.error(f"Other error occurred: {err}")
        return send_response({"error": "An error occurred"}, 500)


# Function to update gacha owner
def update_gacha_owner(buyer_id, gacha_id, seller_id, status):
    try:
        response = requests.put(f"{gacha_url}/update_gacha_owner",
                                json={"buyer_id": buyer_id, "seller_id": seller_id, "gacha_id": gacha_id, "status": status}, headers=generate_session_token_system())
        response.raise_for_status()
        logging.debug(f"Response from gacha service: {response.json()}")
        return send_response(response.json(),200)
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        return send_response({"error": "Failed to update gacha owner"}, 408)
    except Exception as err:
        logging.error(f"Other error occurred: {err}")
        return send_response({"error": "An error occurred"}, 500)
# Function to create a transaction
def create_transaction(user_id, amount, transaction_type):
    try:
        response = requests.post(f"{transaction_url}/add_transaction",
                                    json={"user_id": user_id, "amount": amount, "type": transaction_type}, headers=generate_session_token_system())
        response.raise_for_status()
        logging.debug(f"Response from transaction service: {response.json()}")
        return send_response(response.json(),200)
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        return send_response({"error": "Failed to create transaction"}, 408)
    except Exception as err:
        logging.error(f"Other error occurred: {err}")
        return send_response({"error": "An error occurred"}, 500)


def update_user_balance(user_id, amount, type):
    try:
        response = requests.put(f"{user_url}/update_balance/PLAYER", headers=generate_session_token_system(),
                                json={"user_id": user_id, "amount": amount, "type": type})
        response.raise_for_status()
        logging.debug(f"Response from user service: {response.json()}")
        return send_response(response.json(),200)
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        return send_response({"error": "Failed to update user balance"}, 408)
    except Exception as err:
        logging.error(f"Other error occurred: {err}")
        return send_response({"error": "An error occurred"}, 500)


# write a function that sends a get request to user service to get the user's balance if the user exists
def get_user_balance(user_id):
    try:
        response = requests.get(f"{user_url}/get_user_balance/{user_id}", headers=generate_session_token_system())
        response.raise_for_status()
        logging.debug(f"Response from user service: {response.json()}")
        return send_response(response.json().get("currency_balance"),200)
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        return send_response({"error": "User not found"}, 408)
    except Exception as err:
        logging.error(f"Other error occurred: {err}")
        return send_response({"error": "An error occurred"}, 500)


# Endpoint to add a new auction
@app.route("/add", methods=["POST"])
def add_auction():
    conn = get_db_connection()
    try:
        # Extract auction details from the request JSON
        data = request.get_json()
        gacha_id = data.get("gacha_id")
        seller_id = data.get("seller_id")
        base_price = data.get("base_price")

        # Check if all required fields are provided
        if not all([gacha_id, base_price, seller_id]):
            logging.error("Missing data for new auction")
            return send_response({"error": "Missing data for new auction"}, 400)

        # Connect to the database
        cursor = conn.cursor()

        # VERIFY IF THE GACHA EXIST AND IF ITS NOT LOCKED
        # Make a GET request to the Gacha service to verify the gacha
        if is_gacha_unlocked(seller_id, gacha_id):
            # Insert the new auction record
            auction_id = str(uuid.uuid4())
            end_time = (datetime.now() + timedelta(hours=6)).timestamp()

            response, status_code = update_gacha_status(seller_id, gacha_id, "locked")
            if status_code == 200:
                cursor.execute(
                    "INSERT INTO Auctions (auction_id, gacha_id, seller_id, base_price, highest_bid, buyer_id, status, end_time) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (auction_id, gacha_id, seller_id, base_price, 0, None, "active", end_time),
                )

                # UPDATE GACHA INVENTORY WITH BLOCKED GACHA
                conn.commit()
                logging.debug("Auction created successfully")
                return send_response({"message": "Auction created successfully", "auction_id": auction_id}, 201)
            else:
                logging.error("Failed to lock gacha")
                return send_response({"error": "Failed to lock gacha"}, 400)
        else:
            logging.error("Gacha is locked or does not exist")
            return send_response({"error": "Gacha is locked or does not exist"}, 400)
    except Exception as e:
        logging.error(f"Error occurred while adding auction: {e}")
        return send_response({"error": "An error occurred while adding auction"}, 500)
    finally:
        if conn:
            conn.close()


# write a function that checks if the auction has ended and if it has, update the status to expired
def check_auction_status():
    conn = get_db_connection()
    try:
        # Connect to the database
        cursor = conn.cursor()

        logging.debug("Inside check auction status. Before query")
        # Retrieve all active auctions that have ended
        cursor.execute("SELECT * FROM Auctions WHERE status = 'active'")
        auctions = cursor.fetchall()

        today = datetime.now().timestamp()
        # Update the status of each expired auction
        logging.debug("Current datetime is: %s", today)
        for auction in auctions:
            end_time = auction["end_time"]
            logging.debug("End time is: %s", end_time)

            if today <= end_time:
                continue

            logging.debug(f"Inside check auction status. Auction ({auction['auction_id']}) ended")
            if auction["highest_bid"] > 0:
                cursor.execute(
                    "UPDATE Auctions SET status = 'completed' WHERE auction_id = ?",
                    (auction["auction_id"],),
                )
                # Update the owner of the gacha
                if update_gacha_owner(auction['buyer_id'], auction['gacha_id'], auction['seller_id'], "unlocked")[1] != 200:
                    logging.error("Failed to unlock gacha")
                    continue

                logging.debug("Owner updated")

                # Update the seller's balance
                if update_user_balance(auction['seller_id'], auction['highest_bid'], "auction_credit")[1] != 200:
                    logging.error("Failed to update seller's balance")
                    continue

                logging.debug("Seller balance updated")

                # Create transaction for seller
                if create_transaction(auction['seller_id'], auction['highest_bid'], "auction_credit")[1] != 200:
                    logging.error("Failed to create transaction for seller")
                    continue

                logging.debug("Transaction for seller created")

                # Create transaction for buyer
                if create_transaction(auction['buyer_id'], auction['highest_bid'], "auction_debit")[1] != 200:
                    logging.error("Failed to create transaction for buyer")
                    continue

                logging.debug("Transaction for buyer created")

            else:
                cursor.execute(
                    "UPDATE Auctions SET status = 'expired' WHERE auction_id = ?",
                    (auction["auction_id"],),
                )
                if update_gacha_status(auction['seller_id'], auction['gacha_id'], "unlocked")[1] != 200:
                    logging.error("Failed to unlock gacha")
                    continue

        conn.commit()
        logging.debug("Auction status updated successfully")
        return send_response({"message": "Auction status updated successfully"}, 200)

    except Exception as e:
        logging.error(f"Error occurred while checking auction status: {e}")
        return send_response({"error": "An error occurred while checking auction status"}, 500)

    finally:
        if conn:
            conn.close()
            
# Endpoint to retrieve all auction
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

    try:
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
        return send_response({"auctions": result}, 200)

    except sqlite3.Error as e:
        logging.error(f"Database error occurred: {e}")
        return send_response({"error": "Database error occurred"}, 500)

    except Exception as e:
        logging.error(f"Error occurred: {e}")
        return send_response({"error": "An error occurred"}, 500)

    finally:
        if conn:
            conn.close()


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
        logging.error("Missing gacha_id parameter")
        return send_response({'error': 'Missing gacha_id parameter'}, 400)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Auctions WHERE gacha_id = ?", (gacha_id,))
        auctions = cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Database error occurred: {e}")
        return send_response({'error': 'Database error occurred'}, 500)
    finally:
        if conn:
            conn.close()

    if auctions:
        logging.debug(f"Found {len(auctions)} auctions for gacha_id {gacha_id}")
        return send_response([dict(auction) for auction in auctions], 200)
    else:
        logging.debug(f"No auctions found for gacha_id {gacha_id}")
        return send_response({'error': 'No auctions found for the gacha'}, 404)


# Functions for Bidding
# Endpoint to place a bid on an auction
@app.route("/bid", methods=["POST"])
def place_bid():
    check_auction_status()
    # Extract bid details from the request JSON
    data = request.get_json()
    auction_id = data.get("auction_id")
    user_id = data.get("user_id")
    bid_amount = data.get("bid_amount")

    # Check if all required fields are provided
    if not all([auction_id, user_id, bid_amount]):
        return send_response({"error": "Missing data for bid"}, 400)

    conn = None
    try:
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
            return send_response({"error": "Auction not found or already ended"}, 408)

        # Check if the bid amount is higher than the current highest bid
        if int(bid_amount) <= auction["highest_bid"]:
            return send_response({"error": "Bid amount must be higher than current highest bid"}, 400)

        # Check if the user has enough funds for the bid
        user_balance = get_user_balance(user_id)
        if int(user_balance) < int(bid_amount):
            return send_response({"error": "Insufficient funds"}, 403)

        # Update the auction with the new highest bid
        # Send back money to previous buyer
        if auction['buyer_id']:
            update_user_balance(auction['buyer_id'], auction['highest_bid'], "auction_credit")
        # Block money from new buyer
        update_user_balance(user_id, bid_amount, "auction_debit")
        # Update auction
        cursor.execute(
            "UPDATE Auctions SET highest_bid = ?, buyer_id = ? WHERE auction_id = ?",
            (int(bid_amount), user_id, auction_id),
        )

        # Insert in bids db the bid
        bid_id = str(uuid.uuid4())
        bid_time = datetime.now()
        cursor.execute(
            "INSERT INTO Bids (bid_id, auction_id, user_id, bid_amount, bid_time) VALUES (?, ?, ?, ?, ?)",
            (bid_id, auction_id, user_id, bid_amount, bid_time),
        )
        conn.commit()

        if cursor.rowcount == 0:
            return send_response({"error": "Failed to place bid"}, 500)

        return send_response({"message": "Bid placed successfully"}, 200)

    except sqlite3.Error as e:
        logging.error(f"Database error occurred: {e}")
        return send_response({"error": "Database error occurred"}, 500)

    except Exception as e:
        logging.error(f"Error occurred: {e}")
        return send_response({"error": "An error occurred"}, 500)

    finally:
        if conn:
            conn.close()


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
        logging.error("Missing auction_id parameter")
        return send_response({"error": "Missing auction_id parameter"}, 400)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Bids WHERE auction_id = ?", (auction_id,))
        bids = cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Database error occurred: {e}")
        return send_response({"error": "Database error occurred"}, 500)
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        return send_response({"error": "An error occurred"}, 500)
    finally:
        if conn:
            conn.close()

    result = [dict(bid) for bid in bids]
    logging.debug(f"Retrieved {len(result)} bids for auction_id {auction_id}")
    return send_response({"bids": result}, 200)

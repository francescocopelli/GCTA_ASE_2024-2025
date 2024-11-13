from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime, timedelta
import uuid

import requests

app = Flask(__name__)
DATABASE = "AUCTIONS.db"
gacha_url = "http://gacha:5000"
user_url = "http://users:5000"
transaction_url = "http://transactions:5000"

# Helper function to connect to the database
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# write a function that sends user id and gacha id to the gacha service to check if the gacha is locked using GET request
def is_gacha_unlocked(user_id, gacha_id):
    response = requests.get(f"{gacha_url}/gacha/?user_id={user_id}&gacha_id={gacha_id}")
    if response.status_code == 200:
        return True
    return False

#write a function fos sand an update request to the gacha service to lock or unlock gatcha
def update_gacha_status(user_id, gacha_id, status):
    response = requests.put(f"{gacha_url}/gacha/", json={"user_id": user_id, "gacha_id": gacha_id, "status": status})
    return response

def update_gacha_owner(buyer_id, gacha_id, seller_id, status):
    response = requests.put(f"{gacha_url}/gacha/", json={"buyer_id":buyer_id , "seller_id": seller_id, "gacha_id": gacha_id, "status": status})
    return response

def create_transaction(user_id, amount,transaction_type):
    response = requests.post(f"{transaction_url}/transactions/", json={"user_id": user_id, "amount": amount, "type": transaction_type})
    return response

def update_user_balance(user_id, amount, type):
    response = requests.put(f"{user_url}/users/", json={"user_id": user_id, "amount": amount, "type": type})
    return response

#write a function that sends a get request to user service to get the user's balance if the user exists
def get_user_balance(user_id):
    response = requests.get(f"{user_url}/users/?user_id={user_id}")
    if response.status_code == 200:
        return response.json().get("balance")
    else:
        return jsonify({"error": "User not found"}), 404

# Endpoint to add a new auction
@app.route("/add", methods=["POST"])
def add_auction():
    # Extract auction details from the request JSON
    data = request.get_json()
    gacha_id = data.get("gacha_id")
    seller_id = data.get("seller_id")
    base_price = data.get("base_price")

    # Check if all required fields are provided
    if not all([gacha_id, base_price, end_time]):
        return jsonify({"error": "Missing data for new auction"}), 400

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # VERIFY IF THE GACHA EXIST AND IF ITS NOT LOCKED
    # Make a GET request to the Gacha service to verify the gacha
    if is_gacha_unlocked(seller_id, gacha_id):
        # Insert the new auction record
        auction_id = str(uuid.uuid4())
        end_time = datetime.now() + timedelta(hours=6)
        
        if update_gacha_status(seller_id, gacha_id, "locked")== 200:
        
            cursor.execute(
                "INSERT INTO Auctions (auction_id, gacha_id, seller_id, base_price, highest_bid, buyer_id, status, end_time) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (auction_id, gacha_id, seller_id, base_price, 0, None, "active", end_time),
                
            )

            # UPDATE GACHA INVENTORY WITH BLOCKED GACHA

            auction_id = cursor.lastrowid
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

    # Retrieve all active auctions that have ended
    cursor.execute(
        "SELECT * FROM Auctions WHERE status = 'active' AND end_time <= ?",
        (datetime.now(),),
    )
    auctions = cursor.fetchall()

    # Update the status of each expired auction
    for auction in auctions:
        if auction["highest_bid"] > 0:
            cursor.execute(
                "UPDATE Auctions SET status = 'completed' WHERE auction_id = ?",
                (auction["auction_id"],),
            )
            # UPDATE THE owner of the gacha
            if update_gacha_owner(auction['buyer_id'],auction['gacha_id'], auction['seller_id'], "unlocked")!= 200:
                return jsonify({"error": "Failed to unlock gacha"}), 400
            
            # UPDATE THE SELLER'S BALANCE WITH POST TO USER SERVICE
            if update_user_balance(auction['seller_id'], auction['highest_bid'], "credit")!= 200:
                return jsonify({"error": "Failed to update seller's balance"}), 400
            # MAKE POST REQUEST TO TRANSACTION

            if create_transaction(auction['seller_id'], auction['highest_bid'], "selling")!= 200:
                return jsonify({"error": "Failed to create transaction"}), 400
            
            if create_transaction(auction['buyer_id'], auction['highest_bid'], "buying")!= 200:
                return jsonify({"error": "Failed to create transaction"}), 400
            
        else:
            cursor.execute(
                "UPDATE Auctions SET status = 'expired' WHERE auction_id = ?",
                (auction["auction_id"],),
            )
            if update_gacha_status(auction['seller_id'],auction['gacha_id'], "unlocked")!= 200:
                return jsonify({"error": "Failed to unlock gacha"}), 400

    conn.commit()
    conn.close()

    return jsonify({"message": "Auction status updated successfully"}), 200

# Endpoint to retrieve all active or expired auctions
@app.route("/all", methods=["GET"])
def get_all_auctions():
    # Optional query parameter to filter by auction status (active or expired)
    status = request.args.get("status")

    conn = get_db_connection()
    cursor = conn.cursor()

    # If status filter is provided, retrieve only the matching auctions
    if status == "active":
        cursor.execute(
            "SELECT * FROM Auctions WHERE status = 'active' AND end_time > ?",
            (datetime.now(),),
        )
    elif status == "expired":
        cursor.execute(
            "SELECT * FROM Auctions WHERE status = 'expired' OR end_time <= ?",
            (datetime.now(),),
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
        return jsonify({'error': 'No auctions found for the gacha'}), 404
    

# Fuctions for Bidding
# Endpoint to place a bid on an auction
@app.route("/bid", methods=["POST"])
def place_bid():
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
        (auction_id),
    )
    auction = cursor.fetchone()

    if not auction:
        conn.close()
        return jsonify({"error": "Auction not found or already ended"}), 404

    # Check if the bid amount is higher than the current highest bid
    if bid_amount < auction["highest_bid"]:
        conn.close()
        return (
            jsonify({"error": "Bid amount must be higher than current highest bid"}),
            400,
        )

    # Check if the user has enough funds for the bid
    user_balance = get_user_balance(user_id)
    if user_balance < bid_amount:
        conn.close()
        return jsonify({"error": "Insufficient funds"}), 403
    
    # Update the auction with the new highest bid
    
    #sand back money to previous buyer
    update_user_balance(auction['buyer_id'], auction['highest_bid'], "credit")
    #block money from new buyer
    update_user_balance(user_id, bid_amount, "debit")
    #update auction
    cursor.execute(
        "UPDATE Auctions SET highest_bid = ?, buyer_id = ? WHERE auction_id = ?",
        (bid_amount, user_id, auction_id),
    )
    
    #insert in bids db the bid
    bid_id = str(uuid.uuid4())
    bid_time = datetime.now()
    cursor.execute(
        "INSERT INTO Bids (bid_id, auction_id, user_id, bid_amount, bid_time) VALUES (?, ?, ?, ?, ?)",
        (bid_id, auction_id, user_id, bid_amount, bid_time),
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Bid placed successfully"}), 200

# Endpoint to retrieve all bids for a specific auction
@app.route("/bids", methods=["GET"])
def get_bids():
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

# Endpoint to retrieve the highest bid for a specific auction

# Run the Flask app on the specified port
if __name__ == "__main__":
    app.run()

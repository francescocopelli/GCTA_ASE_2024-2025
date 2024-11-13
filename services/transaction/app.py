import logging
from flask import Flask, request, jsonify
import sqlite3
import hashlib

# Configura il logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

DATABASE = './transactions_db/transactions.db'

# Helper function to connect to the database
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Endpoint to make a payment, used for purchasing a gacha roll or placing an auction bid
@app.route('/make_payment', methods=['POST'])
def make_payment():
    # Extracting payment details from the request JSON
    data = request.get_json()
    username = data.get('username')
    transaction_type = data.get('transaction_type')
    amount = data.get('amount')
    
    # Checking if all required fields are provided
    if not all([username, transaction_type, amount]):
        return jsonify({'error': 'Missing data for transaction'}), 400
    
    # Connecting to the database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if the user has enough funds for the payment
    cursor.execute("SELECT currency_balance FROM PLAYER WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    if user and user['currency_balance'] >= amount:
        # Update user balance after payment
        new_balance = user['currency_balance'] - amount
        cursor.execute("UPDATE PLAYER SET currency_balance = ? WHERE username = ?", (new_balance, username))
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Payment successful', 'new_balance': new_balance}), 200
    else:
        conn.close()
        return jsonify({'error': 'Insufficient funds'}), 403

# Endpoint to lock funds for an auction bid, ensuring the user can't exceed their balance during bidding
@app.route('/auction_lock', methods=['POST'])
def auction_lock():
    # Extracting auction lock details from the request JSON
    data = request.get_json()
    username = data.get('username')
    bid_amount = data.get('bid_amount')
    
    # Check if both required fields are provided
    if not all([username, bid_amount]):
        return jsonify({'error': 'Missing data for auction lock'}), 400

    # Connecting to the database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if the user has sufficient funds to cover the bid amount
    cursor.execute("SELECT currency_balance FROM PLAYER WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    if user and user['currency_balance'] >= bid_amount:
        # Deduct the bid amount from the user's balance as a temporary lock
        new_balance = user['currency_balance'] - bid_amount
        cursor.execute("UPDATE PLAYER SET currency_balance = ? WHERE username = ?", (new_balance, username))
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Bid accepted, funds locked', 'new_balance': new_balance}), 200
    else:
        conn.close()
        return jsonify({'error': 'Insufficient funds for bid'}), 403

# Endpoint to remove a lock from a user's currency after an auction ends or bid is canceled
@app.route('/auction_lock/<username>/<auction_id>', methods=['DELETE'])
def remove_auction_lock(username, auction_id):
    # This would typically involve returning locked funds to the user's balance
    # since the auction has ended or the bid has been canceled.
    
    # For this example, we'll assume a simple lock release where we add a predefined amount back
    # In a real application, we would track the actual locked amount for each user and auction
    
    # Placeholder locked amount; in production, this should come from a log or lock record
    locked_amount = 100  # Example amount that was previously locked
    
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Retrieve current balance and add the locked amount back
    cursor.execute("SELECT currency_balance FROM PLAYER WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    if user:
        # Unlock the funds by adding the locked amount back to user's balance
        new_balance = user['currency_balance'] + locked_amount
        cursor.execute("UPDATE PLAYER SET currency_balance = ? WHERE username = ?", (new_balance, username))
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Auction lock removed', 'new_balance': new_balance}), 200
    else:
        conn.close()
        return jsonify({'error': 'User not found or no funds locked'}), 404

# Run the Flask app on the specified port
if __name__ == '__main__':
    app.run()

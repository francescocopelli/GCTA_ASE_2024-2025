from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
DATABASE = 'AUCTIONS.db'

# Helper function to connect to the database
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Endpoint to retrieve all active or expired auctions
@app.route('/auctions/all', methods=['GET'])
def get_all_auctions():
    # Optional query parameter to filter by auction status (active or expired)
    status = request.args.get('status')
    
    conn = get_db_connection()
    cursor = conn.cursor()

    # If status filter is provided, retrieve only the matching auctions
    if status == 'active':
        cursor.execute("SELECT * FROM Auctions WHERE status = 'active' AND end_time > ?", (datetime.now(),))
    elif status == 'expired':
        cursor.execute("SELECT * FROM Auctions WHERE status = 'expired' OR end_time <= ?", (datetime.now(),))
    else:
        # If no status filter is provided, return all auctions
        cursor.execute("SELECT * FROM Auctions")
    
    auctions = cursor.fetchall()
    conn.close()

    # Format the auctions for JSON response
    result = [dict(auction) for auction in auctions]
    return jsonify({'auctions': result}), 200

# Endpoint to add a new auction
@app.route('/auctions/add', methods=['POST'])
def add_auction():
    # Extract auction details from the request JSON
    data = request.get_json()
    gacha_id = data.get('gacha_id')
    base_price = data.get('base_price')
    end_time = data.get('end_time')
    
    # Check if all required fields are provided
    if not all([gacha_id, base_price, end_time]):
        return jsonify({'error': 'Missing data for new auction'}), 400

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Insert the new auction record
    cursor.execute(
        "INSERT INTO Auctions (gacha_id, base_price, highest_bid, status, end_time) VALUES (?, ?, ?, ?, ?)",
        (gacha_id, base_price, 0, 'active', end_time)
    )
    auction_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return jsonify({'message': 'Auction created successfully', 'auction_id': auction_id}), 201

# Endpoint to end an auction manually
@app.route('/auctions/end', methods=['POST'])
def end_auction():
    # Extract the auction ID from the request JSON
    data = request.get_json()
    auction_id = data.get('auction_id')
    
    if not auction_id:
        return jsonify({'error': 'Auction ID is required to end auction'}), 400

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if the auction exists and is still active
    cursor.execute("SELECT * FROM Auctions WHERE auction_id = ? AND status = 'active'", (auction_id,))
    auction = cursor.fetchone()
    
    if not auction:
        conn.close()
        return jsonify({'error': 'Auction not found or already ended'}), 404

    # Update the auction status to 'expired'
    cursor.execute("UPDATE Auctions SET status = 'expired' WHERE auction_id = ?", (auction_id,))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Auction ended successfully'}), 200

# Run the Flask app on the specified port
if __name__ == '__main__':
    app.run()

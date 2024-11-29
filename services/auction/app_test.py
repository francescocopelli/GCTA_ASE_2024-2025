from flask import Flask, request, jsonify
import logging
import uuid
from datetime import datetime, timedelta
from unittest.mock import patch

app = Flask(__name__)

app.config['SECRET_KEY'] = 'your_secret_key'

# Mock data
mock_auctions = [
    {
        "auction_id": str(uuid.uuid4()),
        "gacha_id": 1,
        "seller_id": 1,
        "base_price": 100,
        "highest_bid": 150,
        "buyer_id": 2,
        "status": "active",
        "end_time": (datetime.now() + timedelta(hours=6)).timestamp()
    },
    {
        "auction_id": str(uuid.uuid4()),
        "gacha_id": 2,
        "seller_id": 2,
        "base_price": 200,
        "highest_bid": 250,
        "buyer_id": 3,
        "status": "completed",
        "end_time": (datetime.now() - timedelta(hours=1)).timestamp()
    }
]

mock_bids = [
    {
        "bid_id": str(uuid.uuid4()),
        "auction_id": mock_auctions[0]["auction_id"],
        "user_id": 2,
        "bid_amount": 150,
        "bid_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
]

# Mock responses for external services
def mock_get_user_balance(url, timeout, headers, verify):
    user_id = url.split('/')[-1]
    return MockResponse({"balance": 1000}, 200)

def mock_get_gacha_details(url, timeout, headers, verify):
    gacha_id = url.split('/')[-1]
    return MockResponse({"gacha_id": gacha_id, "details": "Gacha details"}, 200)

class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data

# Helper function to get auction by ID
def get_auction_by_id(auction_id):
    return next((auction for auction in mock_auctions if auction["auction_id"] == auction_id), None)

# Helper function to get bids by auction ID
def get_bids_by_auction_id(auction_id):
    return [bid for bid in mock_bids if bid["auction_id"] == auction_id]

# Endpoint to retrieve all auctions
@app.route("/all", methods=["GET"])
def get_all_auctions():
    status = request.args.get("status", "all")
    if status == "all":
        return jsonify(mock_auctions), 200
    filtered_auctions = [auction for auction in mock_auctions if auction["status"] == status]
    return jsonify(filtered_auctions), 200

# Endpoint to retrieve all active auctions
@app.route("/all_active", methods=["GET"])
def get_all_active_auctions():
    active_auctions = [auction for auction in mock_auctions if auction["status"] == "active"]
    return jsonify(active_auctions), 200

# Endpoint to add a new auction
@app.route("/add", methods=["POST"])
def add_auction():
    data = request.get_json()
    new_auction = {
        "auction_id": str(uuid.uuid4()),
        "gacha_id": data["gacha_id"],
        "seller_id": data["seller_id"],
        "base_price": data["base_price"],
        "highest_bid": 0,
        "buyer_id": None,
        "status": "active",
        "end_time": (datetime.now() + timedelta(hours=6)).timestamp()
    }
    mock_auctions.append(new_auction)
    return jsonify(new_auction), 201

# Endpoint to place a bid on an auction
@app.route("/bid", methods=["POST"])
@patch('requests.get', side_effect=mock_get_user_balance)
def place_bid(mock_get):
    data = request.get_json()
    auction = get_auction_by_id(data["auction_id"])
    if not auction:
        return jsonify({"error": "Auction not found"}), 404
    if data["bid_amount"] <= auction["highest_bid"]:
        return jsonify({"error": "Bid amount must be higher than current highest bid"}), 400
    auction["highest_bid"] = data["bid_amount"]
    auction["buyer_id"] = data["user_id"]
    new_bid = {
        "bid_id": str(uuid.uuid4()),
        "auction_id": auction["auction_id"],
        "user_id": data["user_id"],
        "bid_amount": data["bid_amount"],
        "bid_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    mock_bids.append(new_bid)
    return jsonify(new_bid), 200

# Endpoint to retrieve bids for a specific auction
@app.route("/bids", methods=["GET"])
def get_bids():
    auction_id = request.args.get("auction_id")
    if not auction_id:
        return jsonify({"error": "Missing auction_id parameter"}), 400
    bids = get_bids_by_auction_id(auction_id)
    return jsonify({"bids": bids}), 200

# Endpoint to retrieve auction details
@app.route("/get_auction", methods=["GET"])
@patch('requests.get', side_effect=mock_get_gacha_details)
def get_auction(mock_get):
    auction_id = request.args.get("auction_id")
    if not auction_id:
        return jsonify({"error": "Missing auction_id parameter"}), 400
    auction = get_auction_by_id(auction_id)
    if not auction:
        return jsonify({"error": "Auction not found"}), 404
    return jsonify(auction), 200

# Endpoint to update an auction
@app.route("/update", methods=["PUT"])
def update_auction():
    data = request.get_json()
    auction = get_auction_by_id(data["auction_id"])
    if not auction:
        return jsonify({"error": "Auction not found"}), 404
    auction["base_price"] = data.get("base_price", auction["base_price"])
    auction["highest_bid"] = data.get("highest_bid", auction["highest_bid"])
    auction["buyer_id"] = data.get("buyer_id", auction["buyer_id"])
    auction["end_time"] = data.get("end_time", auction["end_time"])
    auction["status"] = data.get("status", auction["status"])
    return jsonify(auction), 200

# Endpoint to delete an auction
@app.route("/delete", methods=["DELETE"])
def delete_auction():
    auction_id = request.args.get("auction_id")
    if not auction_id:
        return jsonify({"error": "Missing auction_id parameter"}), 400
    auction = get_auction_by_id(auction_id)
    if not auction:
        return jsonify({"error": "Auction not found"}), 404
    mock_auctions.remove(auction)
    return jsonify({"message": "Auction deleted successfully"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
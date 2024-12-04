from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import functools

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mock_secret_key'

# Mock Data
mock_auctions = [
    {
        "auction_id": "uuid1",
        "seller_id": 1,
        "gacha_id": 1,
        "end_time": (datetime.now() + timedelta(days=1)).isoformat(),
        "status": "active",
        "base_price": 10,
        "highest_bid": 10,
        "buyer_id": None
    },
    {
        "auction_id": "uuid2",
        "seller_id": 2,
        "gacha_id": 2,
        "end_time": (datetime.now() + timedelta(days=1)).isoformat(),
        "status": "active",
        "base_price": 20,
        "highest_bid": 20,
        "buyer_id": None
    },
    {
        "auction_id": "uuid3",
        "seller_id": 2,
        "gacha_id": 5,
        "end_time": (datetime.now() - timedelta(days=1)).isoformat(),
        "status": "completed",
        "base_price": 25,
        "highest_bid": 50,
        "buyer_id": 1
    },
    {
    "auction_id": "uuid4",
    "seller_id": 2,
    "gacha_id": 10,
    "end_time": (datetime.now() - timedelta(days=1)).isoformat(),
    "status": "expired",
    "base_price": 10,
    "highest_bid": 10,
    "buyer_id": None
}
]

mock_bids = {
    "bids": []  
}
mock_users = {1: {"user_id": 1, "username": "User1", "balance": 100}, 2: {"user_id": 2, "username": "User2", "balance": 50}}

# Middleware Mocks
def admin_required(f):
    @functools.wraps(f)
    def admin_wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return admin_wrapper

def login_required_void(f):
    @functools.wraps(f)
    def login_wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    
    return login_wrapper

def token_required_void(f):
    @functools.wraps(f)
    def token_wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return token_wrapper

# Helper Functions
def get_auction_by_id(auction_id):
    return next((auction for auction in mock_auctions if auction["auction_id"] == auction_id), None)

def get_user_by_id(user_id):
    return mock_users.get(user_id)

# Endpoints
@app.route('/all', methods=['GET'])
@login_required_void
def get_all_auctions():
    return jsonify(mock_auctions), 200

@app.route('/add', methods=['POST'])
@login_required_void
def add_auction():
    data = request.json
    if "base_price" not in data:
        return jsonify({"error": "Missing base_price parameter"}), 400

    new_auction = {
        "auction_id": "uuid" + str(len(mock_auctions) + 1),
        "seller_id": data["seller_id"],
        "gacha_id": data["gacha_id"],
        "end_time": (datetime.now() + timedelta(hours=6)).isoformat(),
        "status": "active",
        "base_price": data["base_price"],
        "highest_bid": data["base_price"],
        "buyer_id": None
    }
    mock_auctions.append(new_auction)
    return jsonify({"message": "Auction created successfully", "auction_id": new_auction["auction_id"]}), 201

@app.route('/bid', methods=['POST'])
@login_required_void
def place_bid():
    data = request.json
    auction = get_auction_by_id(data["auction_id"])
    user = get_user_by_id(data["user_id"])

    if not auction:
        return jsonify({"error": "Auction not found"}), 404

    if auction["status"] != "active":
        return jsonify({"error": "Auction is not active"}), 400

    if data["bid_amount"] <= auction["highest_bid"]:
        return jsonify({"error": "Bid must be higher than the current bid"}), 400

    if user["balance"] < data["bid_amount"]:
        return jsonify({"error": "Insufficient funds"}), 403

    user["balance"] -= data["bid_amount"]
    auction["highest_bid"] = data["bid_amount"]
    auction["user_id"] = data["user_id"]

    bid = {
        "bid_id": len(mock_bids["bids"]) + 1,  # Use integers for IDs
        "auction_id": data["auction_id"],
        "user_id": data["user_id"],
        "bid_amount": data["bid_amount"],
        "bid_time": datetime.now().isoformat()
    }
    mock_bids["bids"].append(bid)

    return jsonify({"message": "Bid placed successfully"}), 200

@app.route('/bids', methods=['GET'])
def get_bids():
    auction_id = request.args.get("auction_id")
    if not auction_id:
        return jsonify({"error": "Missing auction_id parameter"}), 400
    
    bids = [bid for bid in mock_bids["bids"] if bid["auction_id"] == auction_id]
    return jsonify(bids), 200

@app.route('/delete/<auction_id>', methods=['DELETE'])
@admin_required
def delete_auction(auction_id):
    auction = get_auction_by_id(auction_id)
    if not auction:
        return jsonify({"error": "Auction not found"}), 404

    mock_auctions.remove(auction)
    return jsonify({"message": "Auction deleted successfully"}), 200

@app.route('/get/<auction_id>', methods=['GET'])
@admin_required
def get_auction(auction_id):
    auction = get_auction_by_id(auction_id)
    if not auction:
        return jsonify({"error": "Auction not found"}), 404
    return jsonify(auction), 200

@app.route('/all_active', methods=['GET'])
def get_active_auctions():
    active_auctions = [auction for auction in mock_auctions if auction["status"] == "active"]
    return jsonify(active_auctions), 200

@app.route('/update', methods=['PUT'])
@admin_required
def update_auction():
    data = request.json
    auction_id = data.get("auction_id")
    auction = get_auction_by_id(auction_id)

    if not auction:
        return jsonify({"error": "Auction not found"}), 404

    if auction["status"] != "active":
        return jsonify({"error": "Cannot update a completed or expired auction"}), 400

    auction["end_time"] = (datetime.now() + timedelta(hours=data.get("end_time", 6))).isoformat()
    auction["base_price"] = data.get("base_price", auction["base_price"])
    return jsonify({"message": "Auction updated successfully"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

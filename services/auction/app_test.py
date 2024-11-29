from flask import Flask, request, jsonify
import uuid
from datetime import datetime, timedelta
import functools

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test_secret_key'

# Mock Data
mock_auctions = [
    {
        "auction_id": str(uuid.uuid4()),
        "gacha_id": 1,
        "seller_id": 1,
        "base_price": 100,
        "highest_bid": 0,
        "buyer_id": None,
        "status": "active",
        "end_time": (datetime.now() + timedelta(hours=6)).timestamp(),
    }
]

mock_bids = []
mock_users = [{"user_id": 1, "balance": 1000}, {"user_id": 2, "balance": 2000}]

# Mock Helper Functions
def mock_get_user_balance(user_id):
    user = next((u for u in mock_users if u["user_id"] == user_id), None)
    if user:
        return {"balance": user["balance"]}
    return {"error": "User not found"}

def mock_is_gacha_unlocked(user_id, gacha_id):
    return {"status": "unlocked"}

def mock_update_gacha_status(user_id, gacha_id, status):
    return {"status": "success"}

def mock_create_transaction(user_id, amount, transaction_type):
    return {"transaction_id": str(uuid.uuid4()), "status": "success"}

def mock_update_user_balance(user_id, amount, type):
    user = next((u for u in mock_users if u["user_id"] == user_id), None)
    if user:
        if type == "auction_credit":
            user["balance"] += amount
        elif type == "auction_debit":
            user["balance"] -= amount
        return {"status": "success"}
    return {"error": "User not found"}

# Mock Middleware
def login_required_void(f):
    @functools.wraps(f)
    def login_wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return login_wrapper

def admin_required(f):
    @functools.wraps(f)
    def admin_wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return admin_wrapper

# Endpoints

@app.route("/all", methods=["GET"])
@admin_required
def get_all_auctions():
    status = request.args.get("status", "all")
    if status == "all":
        return jsonify(mock_auctions), 200
    filtered_auctions = [auction for auction in mock_auctions if auction["status"] == status]
    return jsonify(filtered_auctions), 200

@app.route("/all_active", methods=["GET"])
@login_required_void
def get_all_active_auctions():
    active_auctions = [auction for auction in mock_auctions if auction["status"] == "active"]
    return jsonify(active_auctions), 200

@app.route("/add", methods=["POST"])
@login_required_void
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
        "end_time": (datetime.now() + timedelta(hours=6)).timestamp(),
    }
    mock_auctions.append(new_auction)
    return jsonify(new_auction), 201

@app.route("/bid", methods=["POST"])
@login_required_void
def place_bid():
    data = request.get_json()
    auction = next((a for a in mock_auctions if a["auction_id"] == data["auction_id"]), None)
    if not auction:
        return jsonify({"error": "Auction not found"}), 404
    if data["bid_amount"] <= auction["highest_bid"]:
        return jsonify({"error": "Bid amount must be higher than current highest bid"}), 400
    user_balance = mock_get_user_balance(data["user_id"]).get("balance", 0)
    if user_balance < data["bid_amount"]:
        return jsonify({"error": "Insufficient balance"}), 403
    auction["highest_bid"] = data["bid_amount"]
    auction["buyer_id"] = data["user_id"]
    mock_update_user_balance(data["user_id"], -data["bid_amount"], "auction_debit")
    new_bid = {
        "bid_id": str(uuid.uuid4()),
        "auction_id": auction["auction_id"],
        "user_id": data["user_id"],
        "bid_amount": data["bid_amount"],
        "bid_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }
    mock_bids.append(new_bid)
    return jsonify(new_bid), 200

@app.route("/bids", methods=["GET"])
def get_bids():
    auction_id = request.args.get("auction_id")
    if not auction_id:
        return jsonify({"error": "Missing auction_id parameter"}), 400
    bids = [bid for bid in mock_bids if bid["auction_id"] == auction_id]
    return jsonify({"bids": bids}), 200

@app.route("/get_auction", methods=["GET"])
@admin_required
def get_auction():
    auction_id = request.args.get("auction_id")
    if not auction_id:
        return jsonify({"error": "Missing auction_id parameter"}), 400
    auction = next((a for a in mock_auctions if a["auction_id"] == auction_id), None)
    if not auction:
        return jsonify({"error": "Auction not found"}), 404
    return jsonify(auction), 200

@app.route("/delete", methods=["DELETE"])
@admin_required
def delete_auction():
    auction_id = request.args.get("auction_id")
    auction = next((a for a in mock_auctions if a["auction_id"] == auction_id), None)
    if not auction:
        return jsonify({"error": "Auction not found"}), 404
    mock_auctions.remove(auction)
    return jsonify({"message": "Auction deleted successfully"}), 200

@app.route("/update", methods=["PUT"])
@login_required_void
def update_auction():
    data = request.get_json()
    auction = next((a for a in mock_auctions if a["auction_id"] == data["auction_id"]), None)
    if not auction:
        return jsonify({"error": "Auction not found"}), 404
    auction["base_price"] = data.get("base_price", auction["base_price"])
    auction["end_time"] = data.get("end_time", auction["end_time"])
    auction["status"] = data.get("status", auction["status"])
    auction["highest_bid"] = data.get("highest_bid", auction["highest_bid"])
    auction["buyer_id"] = data.get("buyer_id", auction["buyer_id"])
    return jsonify(auction), 200

@app.route("/highest_bid", methods=["GET"])
@admin_required
def get_highest_bid():
    gacha_id = request.args.get("gacha_id")
    if not gacha_id:
        return jsonify({"error": "Missing gacha_id parameter"}), 400
    auction = next((a for a in mock_auctions if a["gacha_id"] == int(gacha_id)), None)
    if not auction:
        return jsonify({"error": "Auction not found"}), 404
    return jsonify({"highest_bid": auction["highest_bid"], "buyer_id": auction["buyer_id"]}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

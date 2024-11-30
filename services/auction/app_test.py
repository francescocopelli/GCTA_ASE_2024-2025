from flask import Flask, request, jsonify
import uuid
import base64
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test_secret_key'

# Mock Data
mock_gacha_items = [
    {
        "gacha_id": str(uuid.uuid4()),
        "name": "Gacha Item 1",
        "rarity": "common",
        "status": "available",
        "description": "A common gacha item",
        "image": None
    },
    {
        "gacha_id": str(uuid.uuid4()),
        "name": "Gacha Item 2",
        "rarity": "rare",
        "status": "available",
        "description": "A rare gacha item",
        "image": None
    }
]

mock_user_inventory = {
    "1": [mock_gacha_items[0]["gacha_id"], mock_gacha_items[1]["gacha_id"]]
}

# Mock Helper Functions
def get_gacha_item_by_id(gacha_id):
    return next((item for item in mock_gacha_items if item["gacha_id"] == gacha_id), None)

def mock_get_user(user_id):
    return {"user_id": user_id, "username": "testuser"}

def mock_update_user_balance(user_id, amount, type):
    return {"status": "success"}

def mock_create_transaction(user_id, amount, transaction_type):
    return {"transaction_id": str(uuid.uuid4()), "status": "success"}

# Endpoints
@app.route('/all', methods=['GET'])
def get_all_gacha_items():
    return jsonify(mock_gacha_items), 200

@app.route('/add', methods=['POST'])
def add_gacha_item():
    data = request.form
    new_gacha_item = {
        "gacha_id": str(uuid.uuid4()),
        "name": data.get("name"),
        "rarity": data.get("rarity"),
        "status": data.get("status"),
        "description": data.get("description"),
        "image": base64.b64encode(data.get("image").read()).decode('utf-8') if data.get("image") else None
    }
    mock_gacha_items.append(new_gacha_item)
    return jsonify(new_gacha_item), 201

@app.route('/roll', methods=['POST'])
def roll_gacha():
    data = request.get_json()
    user_id = data["user_id"]
    roll_cost = 5

    # Mock user balance check
    user_balance = 100
    if user_balance < roll_cost:
        return jsonify({"error": "Insufficient funds for gacha roll"}), 403

    # Perform the gacha roll by selecting a random item based on rarity
    selected_item = mock_gacha_items[0]  # Simplified for mock
    mock_user_inventory.setdefault(user_id, []).append(selected_item["gacha_id"])

    return jsonify({
        'message': 'Gacha roll successful',
        'gacha_id': selected_item['gacha_id'],
        'name': selected_item['name'],
        'rarity': selected_item['rarity'],
    }), 200

@app.route('/inventory/<user_id>', methods=['GET'])
def get_user_inventory(user_id):
    inventory = mock_user_inventory.get(user_id, [])
    items = [get_gacha_item_by_id(gacha_id) for gacha_id in inventory]
    return jsonify(items), 200

@app.route('/inventory/add', methods=['POST'])
def add_to_inventory():
    data = request.get_json()
    user_id = data["user_id"]
    gacha_id = data["gacha_id"]
    mock_user_inventory.setdefault(user_id, []).append(gacha_id)
    return jsonify({"message": "Gacha item successfully added to user's inventory"}), 201

@app.route('/update', methods=['PUT'])
def update_gacha_item():
    data = request.form
    gacha_id = data.get("gacha_id")
    gacha_item = get_gacha_item_by_id(gacha_id)
    if not gacha_item:
        return jsonify({"error": "Gacha item not found"}), 404

    gacha_item["name"] = data.get("name", gacha_item["name"])
    gacha_item["rarity"] = data.get("rarity", gacha_item["rarity"])
    gacha_item["status"] = data.get("status", gacha_item["status"])
    gacha_item["description"] = data.get("description", gacha_item["description"])
    if data.get("image"):
        gacha_item["image"] = base64.b64encode(data.get("image").read()).decode('utf-8')

    return jsonify(gacha_item), 200

@app.route('/get/<gacha_id>', methods=['GET'])
def get_gacha_item(gacha_id):
    gacha_item = get_gacha_item_by_id(gacha_id)
    if not gacha_item:
        return jsonify({"error": "Gacha item not found"}), 404
    return jsonify(gacha_item), 200

@app.route('/get/<user_id>/<gacha_id>', methods=['GET'])
def get_user_gacha_item(user_id, gacha_id):
    inventory = mock_user_inventory.get(user_id, [])
    if gacha_id not in inventory:
        return jsonify({"error": "Gacha item not found in user's inventory"}), 404
    gacha_item = get_gacha_item_by_id(gacha_id)
    return jsonify(gacha_item), 200

@app.route('/is_gacha_unlocked/<user_id>/<gacha_id>', methods=['GET'])
def is_gacha_unlocked(user_id, gacha_id):
    inventory = mock_user_inventory.get(user_id, [])
    if gacha_id in inventory:
        return jsonify({"status": "unlocked"}), 200
    return jsonify({"status": "locked"}), 404

@app.route('/update_gacha_status', methods=['PUT'])
def update_gacha_status():
    data = request.get_json()
    user_id = data["user_id"]
    gacha_id = data["gacha_id"]
    status = data["status"]

    gacha_item = get_gacha_item_by_id(gacha_id)
    if not gacha_item:
        return jsonify({"error": "Gacha item not found"}), 404

    gacha_item["status"] = status
    return jsonify({"message": "Gacha status updated successfully"}), 200

@app.route('/update_gacha_owner', methods=['PUT'])
def update_gacha_owner():
    data = request.get_json()
    buyer_id = data["buyer_id"]
    seller_id = data["seller_id"]
    gacha_id = data["gacha_id"]
    status = data["status"]

    if gacha_id not in mock_user_inventory.get(seller_id, []):
        return jsonify({"error": "Gacha item not found in seller's inventory"}), 404

    mock_user_inventory[seller_id].remove(gacha_id)
    mock_user_inventory.setdefault(buyer_id, []).append(gacha_id)

    return jsonify({"message": "Gacha owner updated successfully"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
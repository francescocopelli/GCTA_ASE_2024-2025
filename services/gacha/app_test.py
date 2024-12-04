from flask import Flask, jsonify, request
import base64
import uuid
from datetime import datetime
import functools

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mock_secret_key'

# Mock Data
mock_gacha_items = [
    {
        "gacha_id": 20,
        "name": "Car1",
        "rarity": "common",
        "status": "available",
        "description": "A basic car.",
        "image": None,
    },
    {
        "gacha_id": 21,
        "name": "Cool Car",
        "rarity": "rare",
        "status": "available",
        "description": "A sturdy car.",
        "image": None,
    },
]

mock_user_inventory = [
    {
        "user_id": 1,
        "gacha_id": 21,
        "acquired_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "locked": "unlocked",
    }
]

mock_users = [{"user_id": 1, "currency_balance": 100}, {"user_id": 2, "currency_balance": 200}]

# Mock Helper Functions
def mock_get_user(user_id):
    return next((u for u in mock_users if u["user_id"] == user_id), None)

def mock_update_user_balance(user_id, amount, action):
    user = mock_get_user(user_id)
    if not user:
        return {"error": "User not found"}
    if action == "roll_purchase" and user["currency_balance"] >= amount:
        user["currency_balance"] -= amount
        return {"status": "success"}
    elif action == "credit":
        user["currency_balance"] += amount
        return {"status": "success"}
    return {"error": "Insufficient balance"}

def mock_is_gacha_unlocked(user_id, gacha_id):
    inventory = next((item for item in mock_user_inventory if item["user_id"] == user_id and item["gacha_id"] == gacha_id), None)
    return {"message": "Gacha item is unlocked"} if inventory and inventory["locked"] == "unlocked" else {"message": "Gacha item is locked"}

def mock_update_gacha_status(user_id, gacha_id, status):
    inventory = next((item for item in mock_user_inventory if item["user_id"] == user_id and item["gacha_id"] == gacha_id), None)
    if inventory:
        inventory["locked"] = status
        return {"message": "Gacha status updated"}
    return {"error": "Gacha status update failed"}

def mock_update_gacha_owner(buyer_id, seller_id, gacha_id, status):
    inventory = next((item for item in mock_user_inventory if item["user_id"] == seller_id and item["gacha_id"] == gacha_id), None)
    if not inventory:
        return {"error": "Gacha item not found in seller's inventory"}
    inventory["user_id"] = buyer_id
    inventory["locked"] = status
    return {"message": "Gacha owner updated successfully"}

def mock_delete_gacha_item(gacha_id):
    global mock_gacha_items
    gacha_item = next((item for item in mock_gacha_items if item["gacha_id"] == int(gacha_id)), None)
    if not gacha_item:
        return {"error": "Gacha item not found"}
    mock_gacha_items = [item for item in mock_gacha_items if item["gacha_id"] != int(gacha_id)]
    return {"message": "Gacha item deleted successfully"}

# Middleware Mocks
def admin_required(f):
    @functools.wraps(f)
    def admin_wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return admin_wrapper

def login_required_ret(f):
    @functools.wraps(f)
    def login_wrapper(*args, **kwargs):
        user = mock_get_user(1)  # Mock user with ID 1
        return f(user, *args, **kwargs)
    
    return login_wrapper

def token_required_void(f):
    @functools.wraps(f)
    def token_wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return token_wrapper

# Endpoints
@app.post('/add')
@admin_required
def add():
    data = request.form.to_dict()
    name, rarity, status = data.get("name"), data.get("rarity"), data.get("status")
    description = data.get("description")
    image = request.files.get("image").read() if "image" in request.files else None

    if not all([name, rarity, status]):
         return jsonify({'error': 'Missing data to add gacha item'}, 400)

    new_item = {
        "gacha_id": len(mock_gacha_items) + 1,
        "name": name,
        "rarity": rarity,
        "status": status,
        "description": description,
        "image": base64.b64encode(image).decode() if image else None,
    }
    mock_gacha_items.append(new_item)
    return jsonify({"message": "Gacha item added", "gacha_id": new_item["gacha_id"]}), 201


@app.route('/inventory/<user_id>', methods=['GET'])
@token_required_void
def get_user_inventory(user_id):
    inventory = [item for item in mock_user_inventory if item["user_id"] == int(user_id)]
    if not inventory:
        return jsonify({"error": "No gacha items found"}), 404

    inventory_list = []
    for item in inventory:
        gacha = next((g for g in mock_gacha_items if g["gacha_id"] == int(item["gacha_id"])), {})
        inventory_list.append({
            "gacha_id": gacha.get("gacha_id"),
            "name": gacha.get("name"),
            "rarity": gacha.get("rarity"),
            "status": gacha.get("status"),
            "description": gacha.get("description"),
            "acquired_date": item["acquired_date"],
            "locked": item["locked"],
        })

    return jsonify({"inventory": inventory_list}), 200

@app.route('/roll', methods=['POST'])
@login_required_ret
def roll_gacha(user):
    roll_cost = 5
    if user["currency_balance"] < roll_cost:
        return jsonify({"error": "Insufficient balance"}), 403

    mock_update_user_balance(user["user_id"], roll_cost, "roll_purchase")

    rolled_item = mock_gacha_items[0]
    mock_user_inventory.append({
        "user_id": user["user_id"],
        "gacha_id": rolled_item["gacha_id"],
        "acquired_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "locked": "unlocked",
    })

    return jsonify({"message": "Gacha roll successful", "gacha_id": rolled_item["gacha_id"], "name":rolled_item["name"], "rarity":rolled_item["rarity"]}), 200

@app.route('/inventory/add', methods=['POST'])
@admin_required
def add_to_inventory():
    data = request.get_json()
    user_id, gacha_id = data.get("user_id"), data.get("gacha_id")

    if not all([user_id, gacha_id]):
        return jsonify({"error": "Missing data"}), 400

    gacha = next((g for g in mock_gacha_items if g["gacha_id"] == gacha_id and g["status"] == "available"), None)
    if not gacha:
        return jsonify({"error": "Gacha item not available"}), 404

    mock_user_inventory.append({
        "user_id": int(user_id),
        "gacha_id": gacha_id,
        "acquired_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "locked": "unlocked",
    })

    return jsonify({"message": "Gacha item successfully added to user's inventory"}), 201
  

@app.route('/all', methods=['GET'])
def get_all():
    # Optional offset for pagination
    offset = int(request.args.get("offset", 0))
    limit = 10
    paginated_items = mock_gacha_items[offset:offset + limit]

    if not paginated_items:
        return jsonify({"error": "No gacha items found"}), 404

    result = [
        {
            "gacha_id": item["gacha_id"],
            "name": item["name"],
            "rarity": item["rarity"],
            "status": item["status"],
            "description": item["description"],
            "image": base64.b64encode(item["image"]).decode() if item["image"] else None,
        }
        for item in paginated_items
    ]

    return jsonify({"message": result}), 200


@app.route('/update', methods=['PUT'])
@admin_required
def update_gacha_item():
    """Update an existing gacha item."""
    data = request.form.to_dict()
    gacha_id = data.get("gacha_id")
    name = data.get("name")
    rarity = data.get("rarity")
    status = data.get("status")
    description = data.get("description")
    image = request.files.get("image").read() if "image" in request.files else None

    gacha_item = next((item for item in mock_gacha_items if item["gacha_id"] == int(gacha_id)), None)
    if not gacha_item:
        return jsonify({"error": "Gacha item not found"}), 404

    # Update fields if provided
    gacha_item["name"] = name if name else gacha_item["name"]
    gacha_item["rarity"] = rarity if rarity else gacha_item["rarity"]
    gacha_item["status"] = status if status else gacha_item["status"]
    gacha_item["description"] = description if description else gacha_item["description"]
    if image:
        gacha_item["image"] = base64.b64encode(image).decode()

    return jsonify({"message": "Gacha item updated successfully"}), 200


@app.route('/get/<gacha_id>', methods=['GET'])
def get_gacha_item(gacha_id):
    """Retrieve information about a specific gacha item."""
    gacha_item = next((item for item in mock_gacha_items if item["gacha_id"] == int(gacha_id)), None)

    if not gacha_item:
        return jsonify({"error": "Gacha item not found"}), 404

    return jsonify({
        "gacha_id": gacha_item["gacha_id"],
        "name": gacha_item["name"],
        "rarity": gacha_item["rarity"],
        "status": gacha_item["status"],
        "description": gacha_item["description"],
        "image": base64.b64encode(gacha_item["image"]).decode('utf-8') if gacha_item["image"] else None,
    }), 200

  
@app.route('/update_gacha_status', methods=['PUT'])
@admin_required
def update_gacha_status():
    data = request.get_json()
    user_id = data.get("user_id")
    gacha_id = data.get("gacha_id")
    status = data.get("status")

    if not all([user_id, gacha_id, status]):
        return jsonify({"error": "Missing data"}), 400

    gacha_item = next((item for item in mock_user_inventory if item["user_id"] == int(user_id) and item["gacha_id"] == int(gacha_id)), None)
    if not gacha_item:
        return jsonify({"error": "Gacha item not found"}), 404

    gacha_item["locked"] = status
    return jsonify({"message": "Gacha status updated successfully"}), 200

@app.route('/update_gacha_owner', methods=['PUT'])
@admin_required
def update_gacha_owner():
    data = request.json
    buyer_id, seller_id, gacha_id, status = data.get("buyer_id"), data.get("seller_id"), data.get("gacha_id"), data.get("status")

    if not all([buyer_id, seller_id, gacha_id, status]):
        return jsonify({"error": "Missing data"}), 400

    result = mock_update_gacha_owner(buyer_id, seller_id, gacha_id, status)
    return jsonify(result), 200 if "message" in result else 500


@app.route('/delete/<gacha_id>', methods=['DELETE'])
@admin_required
def delete_gacha_item(gacha_id):
    result = mock_delete_gacha_item(gacha_id)
    if "error" in result:
        return jsonify(result), 404
    return jsonify(result), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

from flask import Flask, request, jsonify
import base64
import functools

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mock_secret_key'

# Mock Data
mock_users = {
    1: {"user_id": 1, "username": "User1", "email": "user1@example.com", "currency_balance": 100, "image": None},
    2: {"user_id": 2, "username": "User2", "email": "user2@example.com", "currency_balance": 50, "image": None}
}

mock_gacha_inventory = {
    1: [
        {
            "gacha_id": 1,
            "name": "Gacha A",
            "description": "Description A",
            "image": "image_a.png",
            "acquired_date": "2023-01-01",
            "locked": False,
            "rarity": "common",
            "status": "active"
        },
        {
            "gacha_id": 2,
            "name": "Gacha B",
            "description": "Description B",
            "image": "image_b.png",
            "acquired_date": "2023-01-02",
            "locked": True,
            "rarity": "rare",
            "status": "inactive"
        }
    ],
    2: [
        {
            "gacha_id": 3,
            "name": "Gacha C",
            "description": "Description C",
            "image": "image_c.png",
            "acquired_date": "2023-01-03",
            "locked": False,
            "rarity": "epic",
            "status": "active"
        }
    ]
}

mock_transactions = []

# Mock Middleware
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


# Helper functions
def find_user(user_id):
    return mock_users.get(user_id)

def find_gacha(user_id, gacha_id):
    return next((g for g in mock_gacha_inventory.get(user_id, []) if g['gacha_id'] == gacha_id), None)

# Endpoints
@app.route("/my_gacha_list", methods=["GET"])
@token_required_void
def my_gacha_list():
    user_id = int(request.args.get('user_id', 0))
    if user_id not in mock_gacha_inventory:
        return jsonify({"error": "No gacha inventory found for user."}), 404
    return jsonify(mock_gacha_inventory[user_id]), 200

@app.route("/gacha/<int:user_id>/<int:gacha_id>", methods=["GET"])
@token_required_void
def gacha_info(user_id, gacha_id):
    gacha = find_gacha(user_id, gacha_id)
    if not gacha:
        return jsonify({"error": "Gacha item not found."}), 404
    return jsonify(gacha), 200

@app.route("/real_money_transaction", methods=["POST"])
@token_required_void
def real_money_transaction():
    data = request.get_json()
    user_id = data.get("user_id")
    amount = data.get("amount")

    if not user_id or amount is None:
        return jsonify({"error": "Missing user_id or amount in request"}), 400

    if amount <= 0:
        return jsonify({"error": "Invalid amount"}), 400

    user = find_user(user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404

    user["currency_balance"] += amount
    mock_transactions.append({
        "transaction_id": len(mock_transactions) + 1,
        "user_id": user_id,
        "amount": amount,
        "type": "top_up"
    })

    return jsonify({"message": "Account topped up successfully"}), 200

@app.route("/get_user_balance", methods=["GET"])
@token_required_void
def get_user_balance():
    user_id = int(request.args.get('user_id', 0))
    user = find_user(user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404
    return jsonify({"currency_balance": user["currency_balance"]}), 200

@app.route("/get_user", methods=["GET"])
def get_user():
    user_id = int(request.args.get('user_id', 0))
    user = find_user(user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404
    return jsonify(user), 200

@app.route("/get_user/<int:user_id>", methods=["GET"])
@admin_required
def get_user_by_id(user_id):
    user = find_user(user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404
    return jsonify(user), 200

@app.route("/update_balance/<string:user_type>", methods=["PUT"])
@admin_required
def update_balance(user_type):
    data = request.get_json()
    user_id = data.get("user_id")
    amount = data.get("amount")
    transaction_type = data.get("type")

    user = find_user(user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404

    if transaction_type == "credit":
        user["currency_balance"] += amount
    elif transaction_type == "debit":
        if user["currency_balance"] < amount:
            return jsonify({"error": "Insufficient balance."}), 400
        user["currency_balance"] -= amount
    else:
        return jsonify({"error": "Invalid transaction type."}), 400

    return jsonify({"message": "Balance updated successfully."}), 200

@app.route("/update", methods=["PUT"])
@login_required_void
def update():
    data = request.form
    user_id = int(request.args.get('user_id', 0))
    user = find_user(user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404

    user["username"] = data.get("username", user["username"])
    user["email"] = data.get("email", user["email"])

    image = request.files.get("image")
    if image:
        user["image"] = base64.b64encode(image.read()).decode('utf-8')

    return jsonify({"message": "User updated successfully."}), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

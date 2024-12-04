from flask import Flask, jsonify, request
import functools

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test_secret_key'

# Mock Data
mock_transactions = [
    {
        "transaction_id": "uuid1",
        "user_id": 101,
        "transaction_type": "roll_purchase",
        "amount": 10.0,
    },
    {
        "transaction_id": "uuid2",
        "user_id": 102,
        "transaction_type": "auction_credit",
        "amount": 50.0,
    },
]

mock_users = [
    {"user_id": 101, "user_type": "PLAYER"},
    {"user_id": 102, "user_type": "ADMIN"},
]

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

def login_required_ret(f):
    @functools.wraps(f)
    def user_wrapper(*args, **kwargs):
        user = mock_users[0]  # Default to the first mock user (Player)
        return f(user, *args, **kwargs)
    return user_wrapper

# Endpoints

@app.route("/add_transaction", methods=["POST"])
@admin_required
def add_transaction():
    """Add a new transaction."""
    data = request.get_json()
    user_id = data.get("user_id")
    amount = data.get("amount")
    transaction_type = data.get("type", "unknown")

    if not all([user_id, amount, transaction_type]):
        return jsonify({"error": "Missing transaction data"}), 400

    new_transaction = {
        "transaction_id": "uuid" + str(len(mock_transactions) + 1),  # Incremental ID
        "user_id": user_id,
        "transaction_type": transaction_type,
        "amount": amount,
    }
    mock_transactions.append(new_transaction)
    return jsonify({"message": "Transaction added successfully", "transaction_id": new_transaction["transaction_id"]}), 200

@app.route("/get_transaction/<transaction_id>", methods=["GET"])
@login_required_void
def get_transaction(transaction_id):
    """Retrieve a transaction by its ID."""
    transaction = next((t for t in mock_transactions if t["transaction_id"] == transaction_id), None)
    if not transaction:
        return jsonify({"error": "Transaction not found"}), 404

    return jsonify(transaction), 200

@app.route("/get_user_transactions", methods=["GET"])
@login_required_ret
def get_my_transactions(user):
    """Retrieve all transactions for the logged-in user."""
    if user["user_type"] == "ADMIN":
        return jsonify({"error": "Admins do not have transaction history"}), 403

    user_transactions = [t for t in mock_transactions if t["user_id"] == user["user_id"]]
    if not user_transactions:
        return jsonify({"error": "No transactions found"}), 404

    return jsonify(user_transactions), 200

@app.route("/get_user_transactions/<int:user_id>", methods=["GET"])
@admin_required
def get_user_transactions(user_id):
    """Retrieve all transactions for a specific user."""
    user_transactions = [t for t in mock_transactions if t["user_id"] == user_id]
    if not user_transactions:
        return jsonify({"error": "No transactions found for the user"}), 404

    return jsonify(user_transactions), 200

@app.get("/all")
@login_required_void
def get_all_transactions():
    """Retrieve all transactions."""
    user = mock_users[0]  # Default mock user
    is_admin = user["user_type"] == "ADMIN"

    if is_admin:
        return jsonify(mock_transactions), 200

    user_transactions = [t for t in mock_transactions if t["user_id"] == user["user_id"]]
    if not user_transactions:
        return jsonify({"error": "No transactions found"}), 404

    return jsonify(user_transactions), 200

# Run Server
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

from flask import Flask, request, jsonify
import logging
import jwt

app = Flask(__name__)

app.config['SECRET_KEY'] = 'your_secret_key'

# Mock data
mock_transactions = [
    {"id": 1, "user_id": 1, "description": "Transaction 1", "amount": 100.00},
    {"id": 2, "user_id": 2, "description": "Transaction 2", "amount": 150.50},
    {"id": 3, "user_id": 3, "description": "Transaction 3", "amount": 50.50},
]

mock_transaction_details = {t["id"]: t for t in mock_transactions}

# Get all transactions
@app.route('/all', methods=['GET'])
def get_all_transactions():
    user = jwt.decode(request.headers["Authorization"].split(" ")[1], app.config["SECRET_KEY"], algorithms=["HS256"])
    is_admin = not user['user_type'] == 'PLAYER'
    if not is_admin:
        user_transactions = [t for t in mock_transactions if t["user_id"] == user['user_id']]
        return jsonify(user_transactions), 200
    return jsonify(mock_transactions), 200

# Get transactions by user ID
@app.route('/transactions/<string:user_id>', methods=['GET'])
def get_transactions_by_user_id(user_id):
    user_transactions = [t for t in mock_transactions if t["user_id"] == user_id]
    if user_transactions:
        return jsonify(user_transactions), 200
    return jsonify({"error": "No transactions found for the user"}), 404

# Get transaction by ID
@app.route('/get_transaction/<int:transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    transaction = mock_transaction_details.get(transaction_id)
    if transaction:
        return jsonify(transaction), 200
    return jsonify({"error": "Transaction not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
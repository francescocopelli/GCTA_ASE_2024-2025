import uuid
from datetime import datetime
from flask import jsonify


import app as main_app

# Mock data for testing
transactions = [
    {
        "transaction_id": str(uuid.uuid4()),
        "user_id": "12345",
        "transaction_type": "roll_purchase",
        "amount": 50.0,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    },
    {
        "transaction_id": str(uuid.uuid4()),
        "user_id": "67890",
        "transaction_type": "auction_credit",
        "amount": 100.0,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    },
]

# Mock implementation for endpoints
def gigio(endpoint, **kwargs):
    if "add_transaction" in endpoint:
        transaction_id = str(uuid.uuid4())
        data = kwargs.get("json", {})
        transactions.append(
            {
                "transaction_id": transaction_id,
                "user_id": str(data["user_id"]),
                "transaction_type": data["type"],
                "amount": data["amount"],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
        return {"message": "Transaction added successfully"}

    elif "get_transaction" in endpoint:
        transaction_id = kwargs.get("transaction_id")
        for transaction in transactions:
            if transaction["transaction_id"] == transaction_id:
                return transaction
        return transactions[0]

    elif "get_user_transactions" in endpoint:
        user_id = kwargs.get("user_id")
        user_transactions = [
            t for t in transactions if t["user_id"] == user_id
        ]
        if user_transactions:
            return user_transactions
        else:
            first_user_transactions = [
                t for t in transactions if t["user_id"] == transactions[0]["user_id"]
            ]
            return first_user_transactions

    elif "all" in endpoint:
        return transactions if transactions else {"error": "No transactions found"}

    return {"error": "Endpoint not implemented"}

flask_app = main_app.app  # Flask app
# Assigning the mock implementation
main_app.gigio = gigio
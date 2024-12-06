import logging
from flask import jsonify, request

import app as main_app

# Mock data for testing
users = [
    {"user_id": "1", "username": "admin_test_1", "email": "admin1@example.com", "user_type": "ADMIN", "balance": 1000},
    {"user_id": "2", "username": "test_2", "email": "player1@example.com", "user_type": "PLAYER", "balance": 500},
]

# Mock database manager endpoints
def gigio(endpoint, **kwargs):
    logging.warning(f"Mock endpoint: {endpoint}")

    if "get_all" in endpoint:
        user_type = endpoint.split("/")[-1]
        return [user for user in users if user["user_type"] == user_type]

    elif "get_user" in endpoint:
        user_id = endpoint.split("/")[-1]
        for user in users:
            if user["user_id"] == user_id:
                return user
        return users[0], 200

    elif "update/ADMIN" in endpoint:
        data = kwargs.get("json", {})
        for user in users:
            if user["user_id"] == data["user_id"]:
                user.update(data)
                return {"message": "Admin user updated successfully"}
        return {"message": "Admin user updated successfully"}

    elif "update/PLAYER" in endpoint:
        data = kwargs.get("json", {})
        for user in users:
            if user["user_id"] == data["user_id"]:
                user.update(data)
                return {"message": "Player user updated successfully"}
        return {"message": "Player user updated successfully"}

    elif "balance/PLAYER" in endpoint:
        user_id = kwargs["user_id"]
        for user in users:
            if user["user_id"] == user_id:
                return {"currency_balance": user["balance"]}
        return {"currency_balance":  users[0]["balance"]}

    return {"error": "Endpoint not implemented"}, 501

flask_app = main_app.app  # Flask app
# Assigning the mock implementation
main_app.gigio = gigio
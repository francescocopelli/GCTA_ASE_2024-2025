import base64
import re
import logging
from flask import jsonify


import app as main_app

# Mock data for testing
users = {
    "PLAYER": [
        {
            "user_id": "player1",
            "username": "player_one",
            "email": "player1@example.com",
            "password": "hashed_password_1",
            "currency_balance": 500,
            "image": base64.b64encode(b"player1_image_data").decode('utf-8'),
            "session_token": "player1_token"
        },
        {
            "user_id": "player2",
            "username": "player_two",
            "email": "player2@example.com",
            "password": "hashed_password_2",
            "currency_balance": 1000,
            "image": None,
            "session_token": "player2_token"
        },
    ],
    "ADMIN": [
        {
            "user_id": "admin1",
            "username": "admin_one",
            "email": "admin1@example.com",
            "password": "hashed_password_3",
            "currency_balance": 0,
            "session_token": "admin1_token"
        }
    ]
}

# Mock utility functions
def gigio(endpoint, **kwargs):
    """Mock implementation for DBM service endpoints."""
    if "register" in endpoint:
        user_type = kwargs["user_type"]
        logging.warning(f"Registering {kwargs}")
        username = kwargs["username"]
        email = kwargs["email"]
        new_user = {
            "user_id": f"{user_type.lower()}_{len(users[user_type]) + 1}",
            "username": username,
            "email": email,
            "password": "hashed_password",
            "currency_balance": 0,
            "image": kwargs.get("image"),
            "session_token": None,
        }
        users[user_type].append(new_user)
        return {"message": f"{user_type} registered successfully"}

    elif "login" in endpoint:
        user_type = kwargs["user_type"]
        data = kwargs["json"]
        username = data["username"]
        password = data["password"]
        user = next((u for u in users[user_type] if u["username"] == username), None)
        if user and password == "valid_password":  # Simulate password check
            auth_code = "auth_code"
            user["session_token"] = auth_code
            return {"auth_code": auth_code},200
        else:
            first_user = users[user_type][0] if users[user_type] else None
            return {"auth_code": "default_auth_code"},200

    elif "logout" in endpoint:
        user_type = kwargs["user_type"]
        session_token = kwargs["session_token"]
        user = next((u for u in users[user_type] if u["session_token"] == session_token), None)
        if user:
            user["session_token"] = None
            return {"message": "Logout successful"}
        return {"message": "Logout successful"}
    
    elif "get_user" in endpoint:
        user_type = kwargs["user_type"]
        user_id = kwargs["user_id"]
        user = next((u for u in users[user_type] if u["user_id"] == user_id), None)
        if user:
            return user
        else:
            first_user = users[user_type][0] if users[user_type] else None
            return first_user

    elif "update" in endpoint:
        user_type = kwargs["user_type"]
        data = kwargs["json"]
        user_id = data.get("user_id")
        user = next((u for u in users[user_type] if u["user_id"] == user_id), None)
        if not user:
            return {"message": "Profile updated successfully"}
        if data.get("username"):
            user["username"] = data["username"]
        if data.get("email"):
            user["email"] = data["email"]
        if data.get("password"):
            user["password"] = "hashed_password"  # Simulate password hashing
        return {"message": "Profile updated successfully"}

    elif "balance" in endpoint:
        user_type = kwargs["user_type"]
        user_id = kwargs["user_id"]
        user = next((u for u in users[user_type] if u["user_id"] == user_id), None)
        if user:
            return {"currency_balance": user["currency_balance"]}
        else:
            first_user = users[user_type][0] if users[user_type] else None
            return {"currency_balance": first_user["currency_balance"]}

    elif "delete" in endpoint:
        user_type = kwargs["user_type"]
        user_id = kwargs["user_id"]
        user = next((u for u in users[user_type] if u["user_id"] == user_id), None)
        if user:
            users[user_type].remove(user)
            return {"message": "User deleted successfully"}
        return {"message": "User deleted successfully"}

    elif "get_all" in endpoint:
        user_type = kwargs["user_type"]
        return users[user_type]

    return {"error": "Unknown endpoint"}

flask_app = main_app.app  # Flask app
# Assigning the mock implementation
main_app.gigio = gigio
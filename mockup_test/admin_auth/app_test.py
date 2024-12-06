import logging
from datetime import datetime

import app as main_app
import random
from auth_middleware import *

users = [
    {
        "user_id": 1,
        "username": "user1",
        "email": "mockup@test.com",
        "currency_balance": 100,
        "session_token": None,
        "password":"hashed_password"
    },
    {
        "user_id": 2,
        "username": "user2",
        "email": "mockup2@test.com",
        "currency_balance": 36,
        "session_token": None,
        "password":"hashed_password"
    }
]


# Assigning the implementation in app.py
def gigio(endpoint, **kwargs):  # Implementation
    logging.warning(f"endpoint: {endpoint}")
    logging.warning(f"kwargs: {kwargs}")
    if "login" in endpoint:
        user_id=random.randint(1, 100)
        token=generate_session_token(user_id,"ADMIN")
        return {
                    "message": "Login successful",
                    "session_token": token,
                    "user_id": user_id
                }

    elif "register" in endpoint:
        user_id=random.randint(1, 100)
        username=kwargs["username"]
        email=kwargs["email"]
        password=kwargs["password"]
        currency_balance=20
        users.append({
            "user_id": user_id,
            "username": username,
            "email": email,
            "currency_balance": currency_balance,
            "password":"hashed_password",
            "session_token": None   
        })
        logging.warning(f"users: {users}")
        return {    "message": "ADMIN registered successfully"}
    elif "logout" in endpoint:
        #remove the session token from the user array which has it
        for user in users:
            logging.warning(f"user: {user}")
            if user["session_token"] == kwargs["session_token"]:
                user["session_token"] = None
                break
        return {    "message": "Logout successful"}
    
    


flask_app = main_app.app  # Flask app


def filtro(elem, column, expected):
    return (
            elem[column] == expected
    )


main_app.gigio = gigio

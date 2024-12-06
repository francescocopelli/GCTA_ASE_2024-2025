import logging
from datetime import datetime

import app as main_app

gachas = [
    {
        "description": "Gacha 1",
        "gacha_id": 1,
        "name": "Gacha 1",
        "rarity": "common",
        "status": "out_of_stock",
        "locked": "unlocked",
        "image": None
    },
    {
        "description": "Gacha 2",
        "gacha_id": 2,
        "name": "Gacha 2",
        "rarity": "rare",
        "status": "available",
        "locked": "unlocked",
        "image": None
    }
]
users = [
    {
        "user_id": 1,
        "username": "user1",
        "email": "mockup@test.com",
        "image": None,
        "currency_balance": 100
    },
    {
        "user_id": 2,
        "username": "user2",
        "email": "mockup2@test.com",
        "image": None,
        "currency_balance": 36
    }
]


# Assigning the implementation in app.py
def gigio(endpoint, **kwargs):  # Implementation
    logging.warning(f"endpoint: {endpoint}")
    logging.warning(f"kwargs: {kwargs}")
    if "inventory_user" in endpoint:
        return gachas
    elif "get_user_gacha" in endpoint:
        gacha_id = kwargs["gacha_id"]
        gachas[0]["gacha_id"] = int(gacha_id)
        gachas[0]["name"] = f"Gacha {gacha_id}"
        gachas[0]["description"] = f"Gacha {gacha_id}"
        gachas[0]["acquired_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        gachas[0]["locked"] = True if gachas[0]["locked"] == "locked" else False
        return gachas[0]
    elif "real_money_transaction" in endpoint:
        return {"message": "Account topped up successfully"}
    elif "get_user_balance" in endpoint:
        return {"currency_balance": 100}
    elif "get_user" in endpoint:
        user_id = kwargs["user_id"]
        users[0]["user_id"] = user_id
        users[0]["username"] = f"user{user_id}"
        return users[0]
    elif "get_user_admin" in endpoint:
        return users[1]
    elif "update_balance" in endpoint:
        return "Balance updated successfully"
    elif "update_user" in endpoint:
        return "Profile updated successfully"


flask_app = main_app.app  # Flask app


def filtro(elem, column, expected):
    return (
            elem[column] == expected
    )


main_app.gigio = gigio

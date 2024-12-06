import logging
import random
from datetime import datetime

import app as main_app

gachas = [
    {
        "description": "Gacha 1",
        "gacha_id": 1,
        "name": "Gacha 1",
        "rarity": "common",
        "status": "available",
        "locked": "unlocked",
        "image": None
    }
]


# Assigning the implementation in app.py
def gigio(endpoint, **kwargs):  # Implementation
    logging.warning(f"endpoint: {endpoint}")

    if "inventory_user" in endpoint:
        for gacha in gachas:
            gacha['gacha_id'] = int(gacha['gacha_id'])
            # remove image
            gacha.pop('image', None)
            gacha['acquired_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return gachas

    elif "all" in endpoint:
        for gacha in gachas:
            gacha['gacha_id'] = int(gacha['gacha_id'])
        return gachas
    elif "gacha_add" in endpoint:
        x = gachas[random.randint(0, len(gachas) - 1)]
        gachas.append(
            {"gacha_id": x['gacha_id'],
             "name": x['name'],
             "rarity": x['rarity'],
             "status": x['status'],
             "description": x['description'],
             "acquired_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
             "locked": x['locked'] == 'locked',
             "image": None
             })
        return 'Gacha item added successfully', x['gacha_id']
    elif 'inventory_add' in endpoint:
        return "Gacha item successfully added to user's inventory"
    elif "roll" in endpoint:
        gachas[0]['gacha_id'] = random.randint(1, 100)
        gachas[0]['name'] = f"Gacha {gachas[0]['gacha_id']}"
        gachas[0]['rarity'] = random.choice(["common", "rare", "epic"])
        return {
            'message': 'Gacha roll successful',
            'gacha_id': gachas[0]['gacha_id'],
            'name': gachas[0]['name'],
            'rarity': gachas[0]['rarity'],
        }
    elif "update_status" == endpoint:
        return "Gacha status updated successfully"
    elif "update" == endpoint:
        return "Gacha item updated successfully"
    elif "get_a_gacha" in endpoint:
        gachas[0]['gacha_id'] = kwargs['gacha_id']
        gachas[0]['name'] = f"Gacha {gachas[0]['gacha_id']}"
        gachas[0]['description'] = f"Gacha {gachas[0]['gacha_id']}"
        return gachas[0]
    elif "get_user_gacha" in endpoint:
        return {
            "gacha_id": 1,
            "name": "Gacha 1",
            "rarity": "common",
            "status": "available",
            "description": "Gacha 1",
            "acquired_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "locked": False,
            "image": None
        }
    elif "is_unlocked" in endpoint:
        return {
            "message": "Gacha item is unlocked"
        }
    elif "update_owner" in endpoint:
        return "Gacha owner updated successfully"
    elif "delete" in endpoint:
        return "Gacha item deleted successfully"


flask_app = main_app.app  # Flask app


def filtro(elem, column, expected):
    return (
            elem[column] == expected
    )


main_app.gigio = gigio

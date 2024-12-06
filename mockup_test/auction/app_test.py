import logging
import random
from datetime import datetime

import app as main_app

auctions = [
    {"name": "scooter", "status": "active"},
    {"name": "bus", "status": "completed"},
]

def filtro(elem, column, expected):
    return (
        elem[column] == expected
    )

def gigio(endpoint, **kwargs):  # Implementation
    logging.warning(f"endpoint: {endpoint}")
    if "all" in endpoint:
        if kwargs['status'] == "all":
            return {
                "message": "All auctions",
                "auctions": auctions
            }
        return {
            "message": "Auction with status",
            "auctions": list(filter(lambda x: filtro(x, "status", query), auctions))
        }

flask_app = main_app.app  # Flask app

# Assigning the implementation in app.py

main_app.gigio = gigio

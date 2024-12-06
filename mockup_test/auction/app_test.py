import datetime
import logging
import random
import uuid

import app as main_app

auctions = [
    {"auction_id": uuid.uuid4().hex,
     "base_price": random.randint(1, 100),
     "end_time": datetime.datetime.now() + datetime.timedelta(hours=6),
     "gacha_id": random.randint(1, 100),
     "highest_bid": random.randint(1, 12),
     "seller_id": random.randint(11, 20),
     "buyer_id": random.randint(1, 10),
     "status": "active"
     },
    {"auction_id": uuid.uuid4().hex,
     "base_price": random.randint(1, 100),
     "end_time": datetime.datetime.now() + datetime.timedelta(hours=6),
     "gacha_id": random.randint(1, 100),
     "highest_bid": random.randint(1, 12),
     "seller_id": random.randint(11, 20),
     "buyer_id": random.randint(1, 10),
     "status": "active"
     },
    {"auction_id": uuid.uuid4().hex,
     "base_price": random.randint(1, 100),
     "end_time": datetime.datetime.now() + datetime.timedelta(hours=6),
     "gacha_id": random.randint(1, 100),
     "highest_bid": random.randint(1, 12),
     "seller_id": random.randint(11, 20),
     "buyer_id": random.randint(1, 10),
     "status": "completed"
     },
]

bids = [
    {"bid_id": uuid.uuid4().hex,
     "auction_id": auctions[random.randint(0, len(auctions) - 1)]["auction_id"],
     "user_id": random.randint(1, 10),
     "bid_amount": random.randint(1, 100),
     "bid_time": datetime.datetime.now()
     },
    {"bid_id": uuid.uuid4().hex,
     "auction_id": auctions[random.randint(0, len(auctions) - 1)]["auction_id"],
     "user_id": random.randint(1, 10),
     "bid_amount": random.randint(1, 100),
     "bid_time": datetime.datetime.now()
     },
    {"bid_id": uuid.uuid4().hex,
     "auction_id": auctions[random.randint(0, len(auctions) - 1)]["auction_id"],
     "user_id": random.randint(1, 10),
     "bid_amount": random.randint(1, 100),
     "bid_time": datetime.datetime.now()
     },
    {"bid_id": uuid.uuid4().hex,
     "auction_id": auctions[random.randint(0, len(auctions) - 1)]["auction_id"],
     "user_id": random.randint(1, 10),
     "bid_amount": random.randint(1, 100),
     "bid_time": datetime.datetime.now()
     },
]


def filtro(elem, column, expected):
    return (
            elem[column] == expected
    )


def gigio(endpoint, **kwargs):  # Implementation
    logging.warning(f"endpoint: {endpoint}")
    if "all" == endpoint:
        status = kwargs['status'] or "all"
        if status == "all":
            return auctions
        else:
            return list(filter(lambda x: filtro(x, "status", status), auctions))
    elif "add_auction" == endpoint:
        gacha_id = kwargs['gacha_id']
        seller_id = kwargs['seller_id']
        base_price = kwargs['base_price']
        auction_id = uuid.uuid4().hex
        auctions.append(
            {
                "auction_id": auction_id,
                "base_price": base_price,
                "end_time": datetime.datetime.now() + datetime.timedelta(hours=6),
                "gacha_id": gacha_id,
                "highest_bid": base_price,
                "seller_id": seller_id,
                "buyer_id": 1,
                "status": "active"
            }
        )
        return ("Auction created successfully", auction_id)
    elif "get_gacha_auctions" == endpoint:
        gacha_id = kwargs['gacha_id']
        res = list(filter(lambda x: filtro(x, "gacha_id", gacha_id), auctions))
        if len(res) == 0:
            a = auctions[0]
            a["gacha_id"] = int(gacha_id)
            return {"auctions": [a]}
    elif "get_all_bids" == endpoint:
        auction_id = kwargs['auction_id']
        res = list(filter(lambda x: filtro(x, "auction_id", auction_id), auctions))
        # if len(res) == 0:
        #     return []
        return list(filter(lambda x: filtro(x, "auction_id", auction_id), bids))
    elif "bid" == endpoint:
        auction_id = kwargs['auction_id']
        buyer_id = kwargs['buyer_id']
        amount = kwargs['amount']
        bids.append(
            {
                "bid_id": uuid.uuid4().hex,
                "auction_id": auction_id,
                "user_id": buyer_id,
                "bid_amount": amount,
                "bid_time": datetime.datetime.now()
            }
        )
        return ("Bid placed successfully")
    elif "get_random_auction" in endpoint:
        return random.choice(auctions)
    elif "get_specific_auction" in endpoint:
        if 'user_id' in kwargs:
            user_id = kwargs['user_id']
            return {'auctions':list(filter(lambda x: filtro(x, "seller_id", user_id), auctions)) or list(
                filter(lambda x: filtro(x, "buyer_id", user_id), auctions)) or list(
                filter(lambda x: filtro(x, "seller_id", auctions[0]['seller_id']), auctions))}
        elif 'auction_id' in kwargs:
            auction_id = kwargs['auction_id']
            return {'auctions':list(filter(lambda x: filtro(x, "auction_id", auction_id), auctions)) or list(
                filter(lambda x: filtro(x, "auction_id", auctions[0]['auction_id']), auctions))}
    elif "get_highest_bid" == endpoint:
        gacha_id = kwargs['gacha_id'] or auctions[0]['gacha_id']
        # return the highest bid for the gacha
        all_auction_per_gacha = list(filter(lambda x: filtro(x, "gacha_id", gacha_id), auctions))
        logging.warning(f"all_auction_per_gacha: {all_auction_per_gacha}")
        if len(all_auction_per_gacha) == 0:
            bid = bids[0]
            bid['gacha_id'] = gacha_id
            return {"auction": bid['auction_id'], "highest_bid": bid['bid_amount'], "buyer_id": bid['user_id']}
        else:
            return max(all_auction_per_gacha, key=lambda x: x['highest_bid'])['highest_bid']
    elif "update_auction" == endpoint:
        auction_id = kwargs['auction_id']
        base_price = kwargs['base_price']
        end_time = kwargs['end_time']
        auction = list(filter(lambda x: filtro(x, "auction_id", auction_id), auctions))
        if len(auction) == 0:
            auction = auctions[0]
        auction['base_price'] = base_price
        auction['end_time'] = end_time
        return "Auction updated successfully"

    elif "delete" in endpoint:
        gacha_id = kwargs['gacha_id']
        return "Auction deleted successfully"


flask_app = main_app.app  # Flask app

# Assigning the implementation in app.py

main_app.gigio = gigio

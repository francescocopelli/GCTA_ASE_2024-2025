
import uuid
from urllib import request

from flask import Flask

from shared.auth_middleware import *

app = Flask(__name__)


app.config['SECRET_KEY'] = SECRET_KEY
DATABASE = "auctions"
DB_HOST = "auctions_db"
gacha_url = "https://gacha:5000"
user_url = "https://user_player:5000"
transaction_url = "https://transaction:5000"
admin_url = "https://user_admin:5000"

logging.basicConfig(level=logging.DEBUG)

@app.route("/all", methods=["GET"])
@admin_required
# Endpoint to retrieve all auction
def get_all_auctions():
    check_auction_status()
    status = request.args.get("status") or "all"
    """
    Retrieve all auctions or filter by auction status.
    This endpoint retrieves all auctions from the database. Optionally, it can filter
    the auctions based on their status (active or expired) using a query parameter.
    Query Parameters:
        status (str, optional): The status of the auctions to filter by. Can be "active" or "expired".
    Returns:
        Response: A JSON response containing a list of auctions. Each auction is represented
        as a dictionary. The response status code is 200.
    Example:
        GET /all
        GET /all?status=active
        GET /all?status=expired
    """
    # Optional query parameter to filter by auction status (active or expired)

    try:
        conn = get_db_connection(DB_HOST, DATABASE)
        cursor = conn.cursor(dictionary=True)

        # If status filter is provided, retrieve only the matching auctions
        if ("active" in status) or ("expired" in status) or ("completed" in status):
            cursor.execute("SELECT * FROM Auctions WHERE status =%s", (status,))
        else:
            # If no status filter is provided, return all auctions
            cursor.execute("SELECT * FROM Auctions")

        auctions = cursor.fetchall()

        # Format the auctions for JSON response
        result = [dict(auction) for auction in auctions]

        return send_response({"auctions": result}, 200)
    except Exception as e:
        return manage_errors(e)
    finally:
        release_db_connection(conn, cursor)


@app.route("/all_active", methods=["GET"])
@login_required_void
def get_all_auctions_restricted():
    req = requests.get("https://localhost:5000/all?status=active",  timeout=3, verify=False, headers=generate_session_token_system())
    return send_response(req.json(), req.status_code)


# Function to check if the gacha is unlocked
def is_gacha_unlocked(user_id, gacha_id):
    try:
        response = requests.get(f"{gacha_url}/is_gacha_unlocked/{user_id}/{gacha_id}", timeout=3, verify=False, 
                                headers=generate_session_token_system())
        response.raise_for_status()
        logging.debug(f"Response from gacha service: {response.json()}")
        return True
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        return False
    except Exception as err:
        logging.error(f"Other error occurred: {err}")
        return False


# Function to update gacha status
def update_gacha_status(user_id, gacha_id, status):
    try:
        response = requests.put(f"{gacha_url}/update_gacha_status", timeout=3, verify=False, 
                                json={"user_id": user_id, "gacha_id": gacha_id, "status": status},
                                headers=generate_session_token_system())
        response.raise_for_status()
        logging.debug(f"Response from gacha service: {response.json()}")
        return send_response(response.json(), 200)
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        return send_response({"error": "Failed to update gacha status"}, 408)
    except Exception as err:
        logging.error(f"Other error occurred: {err}")
        return send_response({"error": "An error occurred"}, 500)


# Function to update gacha owner
def update_gacha_owner(buyer_id, gacha_id, seller_id, status):
    try:
        response = requests.put(f"{gacha_url}/update_gacha_owner", timeout=3, verify=False, 
                                json={"buyer_id": buyer_id, "seller_id": seller_id, "gacha_id": gacha_id,
                                      "status": status}, headers=generate_session_token_system())
        response.raise_for_status()
        logging.debug(f"Response from gacha service: {response.json()}")
        return send_response(response.json(), 200)
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        return send_response({"error": "Failed to update gacha owner"}, 408)
    except Exception as err:
        logging.error(f"Other error occurred: {err}")
        return send_response({"error": "An error occurred"}, 500)


# Function to create a transaction
def create_transaction(user_id, amount, transaction_type):
    try:
        response = requests.post(f"{transaction_url}/add_transaction", timeout=3, verify=False, 
                                 json={"user_id": user_id, "amount": amount, "type": transaction_type},
                                 headers=generate_session_token_system())
        response.raise_for_status()
        logging.debug(f"Response from transaction service: {response.json()}")
        return send_response(response.json(), 200)
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        return send_response({"error": "Failed to create transaction"}, 408)
    except Exception as err:
        logging.error(f"Other error occurred: {err}")
        return send_response({"error": "An error occurred"}, 500)


def update_user_balance(user_id, amount, type):
    try:
        response = requests.put(f"{user_url}/update_balance/PLAYER", headers=generate_session_token_system(), timeout=3, verify=False, 
                                json={"user_id": user_id, "amount": amount, "type": type})
        response.raise_for_status()
        logging.debug(f"Response from user service: {response.json()}")
        return send_response(response.json(), 200)
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        return send_response({"error": "Failed to update user balance"}, 408)
    except Exception as err:
        logging.error(f"Other error occurred: {err}")
        return send_response({"error": "An error occurred"}, 500)


# write a function that sends a get request to user service to get the user's balance if the user exists
def get_user_balance(user_id):
    try:
        response = requests.get(f"{admin_url}/get_user_balance/{user_id}", timeout=3, verify=False,  headers=generate_session_token_system())
        response.raise_for_status()
        logging.debug(f"Response from user service: {response.json()}")
        return send_response(response.json(), 200)
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        return send_response({"error": "User not found"}, 408)
    except Exception as err:
        logging.error(f"Other error occurred: {err}")
        return send_response({"error": "An error occurred"}, 500)


# Endpoint to add a new auction
@app.route("/add", methods=["POST"])
@login_required_void
def add_auction():

    user = jwt.decode(request.headers["Authorization"].split(" ")[1], app.config["SECRET_KEY"], algorithms=["HS256"])
    if user['user_type'] != "PLAYER":
        return send_response({"error": "Only players can create auctions"}, 403)
    if check_header() is True and user["user_type"] == "PLAYER":
        return send_response({"error": "Unauthorized access"}, 403)
    try:
        # Extract auction details from the request JSON
        data = request.get_json()
        gacha_id = data.get("gacha_id")
        seller_id = user["user_id"]
        base_price = data.get("base_price")

        # Check if all required fields are provided
        if not all([gacha_id, base_price, seller_id]):
            logging.error("Missing data for new auction")
            return send_response({"error": "Missing data for new auction"}, 400)

        # Connect to the database
        conn = get_db_connection(DB_HOST, DATABASE)
        cursor = conn.cursor(dictionary=True)

        # VERIFY IF THE GACHA EXIST AND IF ITS NOT LOCKED
        # Make a GET request to the Gacha service to verify the gacha
        if is_gacha_unlocked(seller_id, gacha_id):
            # Insert the new auction record
            auction_id = str(uuid.uuid4())
            end_time = (datetime.now() + timedelta(hours=6)).timestamp()

            response, status_code = update_gacha_status(seller_id, gacha_id, "locked")
            if status_code == 200:
                cursor.execute(
                    "INSERT INTO Auctions (auction_id, gacha_id, seller_id, base_price, highest_bid, buyer_id, status, end_time) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                    (auction_id, gacha_id, seller_id, base_price, 0, None, "active", datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')),
                )

                # UPDATE GACHA INVENTORY WITH BLOCKED GACHA
                conn.commit()
                logging.debug("Auction created successfully")
                return send_response({"message": "Auction created successfully", "auction_id": auction_id}, 201)
            else:
                logging.error("Failed to lock gacha")
                return send_response({"error": "Failed to lock gacha"}, 400)
        else:
            logging.error("Gacha is locked or does not exist")
            return send_response({"error": "Gacha is locked or does not exist"}, 404)

    except Exception as e:
            return manage_errors(e)
    finally:
        release_db_connection(conn, cursor)


# write a function that checks if the auction has ended and if it has, update the status to expired
def check_auction_status():
    conn = get_db_connection(DB_HOST, DATABASE)
    try:
        # Connect to the database
        cursor = conn.cursor(dictionary=True)

        logging.debug("Inside check auction status. Before query")
        # Retrieve all active auctions that have ended
        cursor.execute("SELECT * FROM Auctions WHERE status = 'active'")
        auctions = cursor.fetchall()

        today = datetime.now()
        # Update the status of each expired auction
        logging.debug("Current datetime is: %s", today)
        for auction in auctions:
            end_time = auction["end_time"]
            logging.debug("End time is: %s", end_time)

            if today.timestamp() <= end_time.timestamp():
                continue

            logging.debug(f"Inside check auction status. Auction ({auction['auction_id']}) ended")
            if auction["highest_bid"] > 0:
                cursor.execute(
                    "UPDATE Auctions SET status = 'completed' WHERE auction_id =%s",
                    (auction["auction_id"],),
                )
                # Update the owner of the gacha
                if update_gacha_owner(auction['buyer_id'], auction['gacha_id'], auction['seller_id'], "unlocked")[
                    1] != 200:
                    logging.error("Failed to unlock gacha")
                    continue

                logging.debug("Owner updated")

                # Update the seller's balance
                if update_user_balance(auction['seller_id'], auction['highest_bid'], "auction_credit")[1] != 200:
                    logging.error("Failed to update seller's balance")
                    continue

                logging.debug("Seller balance updated")

                # Create transaction for seller
                if create_transaction(auction['seller_id'], auction['highest_bid'], "auction_credit")[1] != 200:
                    logging.error("Failed to create transaction for seller")
                    continue

                logging.debug("Transaction for seller created")

                # Create transaction for buyer
                if create_transaction(auction['buyer_id'], auction['highest_bid'], "auction_debit")[1] != 200:
                    logging.error("Failed to create transaction for buyer")
                    continue

                logging.debug("Transaction for buyer created")

            else:
                cursor.execute(
                    "UPDATE Auctions SET status = 'expired' WHERE auction_id =%s",
                    (auction["auction_id"],),
                )
                if update_gacha_status(auction['seller_id'], auction['gacha_id'], "unlocked")[1] != 200:
                    logging.error("Failed to unlock gacha")
                    continue

        conn.commit()
        logging.debug("Auction status updated successfully")
        return send_response({"message": "Auction status updated successfully"}, 200)
    except Exception as e:
        return manage_errors(e)
    finally:
        release_db_connection(conn, cursor)


# Endpoint to retrieve all auctions for a specific gacha
@app.route('/get_gacha_auctions', methods=['GET'])
@login_required_void
def get_gacha_auctions():
    """
    Endpoint to retrieve gacha auctions based on gacha_id.
    This endpoint handles GET requests to fetch auctions associated with a specific gacha_id.
    If the gacha_id parameter is missing, it returns a 400 error with a message indicating the missing parameter.
    If auctions are found for the given gacha_id, it returns a JSON list of auctions with a 200 status code.
    If no auctions are found, it returns a 404 error with a message indicating no auctions were found.
    Returns:
        Response: JSON response containing the list of auctions or an error message with the appropriate HTTP status code.
    """
    gacha_id = request.args.get('gacha_id')
    if not gacha_id:
        logging.error("Missing gacha_id parameter")
        return send_response({'error': 'Missing gacha_id parameter'}, 400)

    try:
        conn = get_db_connection(DB_HOST, DATABASE)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Auctions WHERE gacha_id =%s", (gacha_id,))
        auctions = cursor.fetchall()

        if auctions:
            logging.debug(f"Found {len(auctions)} auctions for gacha_id {gacha_id}")
            res = [dict(auction) for auction in auctions]
            return send_response(res, 200)
        else:
            logging.debug(f"No auctions found for gacha_id {gacha_id}")
            return send_response({'error': 'No auctions found for the gacha'}, 404)

    except Exception as e:
        return manage_errors(e)
    finally:
        release_db_connection(conn, cursor)


# Functions for Bidding
# Endpoint to place a bid on an auction
@app.route("/bid", methods=["POST"])
@login_required_ret
def place_bid(user):
    check_auction_status()
    # Extract bid details from the request JSON
    data = request.get_json()
    auction_id = data.get("auction_id")
    user_id = user["user_id"]
    bid_amount = data.get("bid_amount")

    # Check if all required fields are provided
    if not all([auction_id, user_id, bid_amount]):
        return send_response({"error": "Missing data for bid"}, 400)

    conn = None
    if jwt.decode(request.headers["Authorization"].split(" ")[1], app.config["SECRET_KEY"], algorithms=["HS256"])['user_type'] == "ADMIN":
        return send_response({"error": "You cannot place a bid as an admin"}, 403)
    try:
        # Connect to the database
        conn = get_db_connection(DB_HOST, DATABASE)
        cursor = conn.cursor(dictionary=True)

        # Check if the auction exists and is active
        cursor.execute(
            "SELECT * FROM Auctions WHERE auction_id = %s AND status = 'active'",
            (auction_id,),
        )
        auction = cursor.fetchone()

        if not auction:
            return send_response({"error": "Auction not found or already ended"}, 408)

        # Check if the bid amount is higher than the current highest bid
        if int(bid_amount) <= auction["highest_bid"]:
            return send_response({"error": "Bid amount must be higher than current highest bid"}, 400)

        # Check if the user has enough funds for the bid
        user_balance = str(get_user_balance(user_id)[0].get_json().get("currency_balance"))
        if int(user_balance) < int(bid_amount):
            return send_response({"error": "Insufficient funds"}, 403)

        # Update the auction with the new highest bid
        # Send back money to previous buyer
        if auction['buyer_id']:
            update_user_balance(auction['buyer_id'], auction['highest_bid'], "auction_credit")
        # Block money from new buyer
        update_user_balance(user_id, bid_amount, "auction_debit")
        # Update auction
        cursor.execute(
            "UPDATE Auctions SET highest_bid =%s, buyer_id = %s WHERE auction_id =%s",
            (int(bid_amount), user_id, auction_id),
        )

        # Insert in bids db the bid
        bid_id = str(uuid.uuid4())
        bid_time = datetime.now()
        cursor.execute(
            "INSERT INTO Bids (bid_id, auction_id, user_id, bid_amount, bid_time) VALUES (%s,%s,%s,%s,%s)",
            (bid_id, auction_id, user_id, bid_amount, bid_time),
        )
        conn.commit()

        if cursor.rowcount == 0:
            return send_response({"error": "Failed to place bid"}, 409)

        return send_response({"message": "Bid placed successfully"}, 200)
    except Exception as e:
        return manage_errors(e)
    finally:
        release_db_connection(conn, cursor)


# Endpoint to retrieve all bids for a specific auction
@app.route("/bids", methods=["GET"])
def get_bids():
    """
    Endpoint to retrieve bids for a specific auction.
    This endpoint handles GET requests to the /bids route. It expects an 
    auction_id parameter to be provided in the query string. If the 
    auction_id parameter is missing, it returns a 400 error with a 
    message indicating the missing parameter. 
    The function connects to the database, retrieves all bids associated 
    with the given auction_id, and returns them in JSON format.
    Returns:
        Response: A JSON response containing the list of bids for the 
        specified auction_id, or an error message if the auction_id 
        parameter is missing.
    """
    auction_id = request.args.get("auction_id")
    if not auction_id:
        logging.error("Missing auction_id parameter")
        return send_response({"error": "Missing auction_id parameter"}, 400)

    try:
        conn = get_db_connection(DB_HOST, DATABASE)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Bids WHERE auction_id =%s", (auction_id,))
        bids = cursor.fetchall()
        result = [dict(bid) for bid in bids]
        logging.debug(f"Retrieved {len(result)} bids for auction_id {auction_id}")
        return send_response({"bids": result}, 200)

    except Exception as e:
        return manage_errors(e)
    finally:
        release_db_connection(conn, cursor)


@app.get("/my")
@login_required_ret
def all_my_auction(user):
    user_id = user["user_id"]
    if jwt.decode(request.headers["Authorization"].split(" ")[1], app.config["SECRET_KEY"], algorithms=["HS256"])['user_type'] == "ADMIN":
        return send_response({"error": "Admins don't have auctions"}, 403)
    req = requests.get("https://localhost:5000/get_auction?user_id=" + str(user_id), timeout=3, verify=False, 
                       headers=generate_session_token_system())
    return send_response(req.json(), req.status_code)


@app.route("/get_auction", methods=["GET"])
@admin_required
def get_auction():
    check_auction_status()
    """
    Endpoint to retrieve information for a specific auction.
    This endpoint handles GET requests to the /get_auction route. It expects an
    auction_id parameter to be provided in the query string. If the
    auction_id parameter is missing, it returns a 400 error with a
    message indicating the missing parameter.
    The function connects to the database, retrieves the auction information
    associated with the given auction_id, and returns it in JSON format.
    Returns:
        Response: A JSON response containing the auction information for the
        specified auction_id, or an error message if the auction_id
        parameter is missing.
    """
    auction_id = request.args.get("auction_id") or None
    user_id = request.args.get("user_id") or None
    if all([auction_id, user_id]):
        return send_response({"error": "Both auction_id and user_id cannot be provided"}, 400)
    if not auction_id and not user_id:
        return send_response({"error": "Missing auction_id or user_id parameter"}, 400)

    try:
        if auction_id:
            conn = get_db_connection(DB_HOST, DATABASE)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Auctions WHERE auction_id =%s", (auction_id,))
            auction = cursor.fetchone()

            if not auction:
                logging.error(f"No auction found for auction_id {auction_id}")
                return send_response({"error": "No auction found"}, 404)

            logging.debug(f"Retrieved auction information for auction_id {auction_id}")
            res = dict(auction)
            return send_response(res, 200)
        elif user_id:
            conn = get_db_connection(DB_HOST, DATABASE)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Auctions WHERE buyer_id = %s OR seller_id =%s", (user_id, user_id))
            auctions = cursor.fetchall()

            result = [dict(auction) for auction in auctions]
            logging.debug(f"Retrieved {len(result)} auctions for user_id {user_id}")
            return send_response({"auctions": result}, 200)
        else:
            return send_response({"error": "Missing auction_id or user_id parameter"}, 400)

    except Exception as e:
        return manage_errors(e)
    finally:
        release_db_connection(conn, cursor)


@app.get("/highest_bid")
@admin_required
def get_highest_bid():
    gacha_id = request.args.get("gacha_id") or None
    """
    Retrieve the highest bid for a specific auction.
    This endpoint queries the database for the highest bid amount for the specified auction_id.
    If the auction_id is not provided or if the auction is not found, an error message is returned.
    Returns:
        Response: A JSON response containing the highest bid amount for the specified auction_id.
    """
    if not gacha_id:
        return send_response({"error": "Missing gacha_id parameter"}, 400)
    try:
        conn = get_db_connection(DB_HOST, DATABASE)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT auction_id,highest_bid,buyer_id FROM Auctions WHERE gacha_id =%s", (gacha_id,))
        auction = cursor.fetchone()

        if auction:
            return send_response(
                {"auction": auction['auction_id'], "highest_bid": auction["highest_bid"], "buyer_id": auction["buyer_id"]},
                200)
        else:
            return send_response({"error": "Auction not found"}, 404)
    except Exception as e:
        return manage_errors(e)
    finally:
        release_db_connection(conn, cursor)


@app.route("/update", methods=["PUT"])
@login_required_ret
def update_auction(user):
    """
    Update an existing auction.
    This endpoint updates an existing auction in the database with the provided data.
    The auction_id parameter must be provided in the request JSON to identify the auction to update.
    The function connects to the database, updates the auction record, and returns a success message.
    Returns:
        Response: A JSON response indicating that the auction was updated successfully.
    """
    auction_id = request.args.get("auction_id") or None
    if not auction_id:
        return send_response({"error": "Missing auction_id parameter"}, 400)
    try:
        conn = get_db_connection(DB_HOST, DATABASE)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Auctions WHERE auction_id =%s", (auction_id,))
        auction = cursor.fetchone()

        if not auction:
            return send_response({"error": "Auction not found"}, 404)

        if auction['seller_id'] != user["user_id"] and user["user_type"] == "PLAYER":
            return send_response({"error": "You are not the seller of this auction"}, 403)

        if auction['status'] != 'active':
            return send_response({"error": "Auction has finished"}, 400)

        data = request.get_json()
        base_price = data.get("base_price") or auction["base_price"]
        end_time = auction["end_time"]

        if data.get("end_time"):
            end_time = (datetime.strptime(data.get("end_time"), "%Y-%m-%d %H:%M:%S") + timedelta(hours=1)).timestamp()

        # Update the auction record with the new data
        cursor.execute(
            "UPDATE Auctions SET base_price =%s, end_time = %s WHERE auction_id =%s",
            (
                base_price,
                end_time,
                auction_id,
            ),
        )
        conn.commit()

        check_auction_status()
        if not cursor.rowcount:
            return send_response({"error": "Failed to update auction"}, 400)
        return send_response({"message": "Auction updated successfully"}, 200)

    except Exception as e:
        return manage_errors(e)
    finally:
        release_db_connection(conn, cursor)

@app.route("/delete", methods=["DELETE"])
@admin_required
# only for internal purposes
def delete_auction():
    """
    Delete an existing auction.
    This endpoint deletes an existing auction from the database.
    The auction_id parameter must be provided in the request JSON to identify the auction to delete.
    The function connects to the database, deletes the auction record, and returns a success message.
    Returns:
        Response: A JSON response indicating that the auction was deleted successfully.
    """
    gacha_id = request.args.get("gacha_id") or None
    if not gacha_id:
        return send_response({"error": "Missing gacha_id parameter"}, 400)
    try:
        conn = get_db_connection(DB_HOST, DATABASE)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Auctions WHERE gacha_id =%s", (gacha_id,))
        auctions = cursor.fetchall()

        if not auctions:
            return send_response({"error": "Auction not found"}, 404)

        for auction in auctions:
            cursor.execute("DELETE FROM Auctions WHERE auction_id =%s", (auction["auction_id"],))
            cursor.execute("DELETE FROM Bids WHERE auction_id =%s", (auction["auction_id"],))

        conn.commit()


        if not cursor.rowcount:
            return send_response({"error": "Failed to delete auction"}, 400)
        return send_response({"message": "Auction deleted successfully"}, 200)

    except Exception as e:
        return manage_errors(e)
    finally:
        release_db_connection(conn, cursor)
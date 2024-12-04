# create an hello world endpoint
import base64

from flask import Flask

from shared.auth_middleware import *

app = Flask(__name__)


app.config['SECRET_KEY'] = SECRET_KEY

logging.basicConfig(level=logging.DEBUG)

# A function that adds a transaction to the transaction service
def create_transaction(user_id, amount, transaction_type):
    response = requests.post(f"{transaction_url}/add_transaction", headers=generate_session_token_system(), timeout=30, verify=False, 
                             json={"user_id": user_id, "amount": amount, "type": transaction_type})
    return response


# make a function that ask to the service gacha the list of all my gacha inside the db of gacha user invetory

@app.get("/my_gacha_list")
@token_required_void
def my_gacha_list():
    user_id = str(decode_session_token(request.headers["Authorization"].split(" ")[1])[            "user_id"])
    response = requests.get(f"{gacha_url}/inventory/" + user_id,  timeout=30, verify=False, headers=request.headers)
    return send_response(response.json(), response.status_code)


# function to ask for the information of a specific gacha for that user
@app.get("/gacha/<user_id>/<gacha_id>")
@token_required_void
def gacha_info(user_id, gacha_id):
    gacha_id=sanitize(gacha_id)
    response = requests.get(f"{gacha_url}/get/" + str(user_id) + "/" + str(gacha_id), timeout=30, verify=False, 
                            headers=generate_session_token_system())
    return send_response(response.json(), response.status_code)


def update_user_balance(user_id, amount, type):
    response = requests.put(
        f"{dbm_url}/update_balance/PLAYER", headers=request.headers, timeout=30, verify=False, 
        json={"user_id": user_id, "amount": amount, "type": type},
    )
    return response


@app.route("/real_money_transaction", methods=["POST"])
@token_required_ret
def real_money_transaction(user):
    """
    Handle real money transactions.
    This endpoint processes a real money transaction by updating the user's balance
    and recording the transaction in the database.
    Request JSON format:
    {
        "user_id": str,
        "amount": float
    }
    Returns:
        Response: A JSON response indicating success or failure of the transaction.
        - 200: Transaction added successfully.
        - 400: Failed to update user balance.
    """
    data = request.get_json()
    user_id = str(user['user_id'])
    amount = data.get("amount")

    if not user_id or amount is None:
        logging.error("Missing user_id or amount in request")
        return send_response({"error": "Missing amount in request"}, 400)
    if amount <= 0:
        return send_response({"error": "Invalid amount"}, 400)
    # Update the user's balance
    if update_user_balance(user_id, amount, "credit").status_code != 200:
        return send_response({"error": "Failed to update user balance"}, 400)

    if create_transaction(user_id, amount, "top_up").status_code != 200:
        return send_response({"error": "Failed to create transaction"}, 400)

    return send_response({"message": "Account topped up successfully"}, 200)


# function to get the user balance information
@app.get("/get_user_balance")
@token_required_ret
def get_user_balance(current_user):
    user_type=decode_session_token(request.headers["Authorization"].split(" ")[1])['user_type']
    logging.debug("Current user: %s", current_user)
    if user_type != 'PLAYER':
        return send_response({"error": "Only players can view their balance"}, 403)
    user_id = current_user['user_id']
    response = requests.get(f"{dbm_url}/balance/PLAYER", params={"user_id": user_id},  timeout=30, verify=False, headers=request.headers)
    return send_response(response.json(), response.status_code)

@app.get("/get_user")
@token_required_ret
def get_user(user):
    if decode_session_token(request.headers["Authorization"].split(" ")[1])['user_type'] != 'PLAYER':
        return send_response({"error": "Only players can view their information"}, 403)
    url = f"{dbm_url}/get_user/" + str(user['user_id'])
    response = requests.get(url,  timeout=30, verify=False, headers=request.headers)
    return send_response(response.json(), response.status_code)

# Hidden endpoint from the API documentation
@app.get("/get_user/<user_id>")
@admin_required
def get_user_by_id(user_id):
    url = f"{dbm_url}/get_user/" + str(user_id)
    response = requests.get(url,  timeout=30, verify=False, headers=generate_session_token_system())
    logging.debug("User_player response: %s", response)
    return send_response(response.json(), response.status_code)



@app.route("/update_balance/<user_type>", methods=['PUT'])
@admin_required
def update_balance(user_type):
    user_id = request.json['user_id']
    amount = request.json['amount']
    type = request.json['type']

    url = f"{dbm_url}/update_balance/" + user_type
    data = {
        "user_id": user_id,
        "amount": amount,
        "type": type
    }
    logging.debug("Sending data: %s", data)
    # takes the request headers and add a new key called X-Gateway-Port with the value 8081
    response = requests.put(url,  timeout=30, verify=False, json=data, headers=request.headers)
    logging.debug("Received response: %s", response)
    return send_response(response.json(), response.status_code)


@app.route("/update", methods=['PUT'])
@login_required_ret
def update(user):
    if not any(request.form):
        return send_response({"error": "No fields to update"}, 400)

    data = request.form
    user_id = user['user_id']
    username = data.get("username") or user['username']
    email = data.get("email") or user['email']
    image = request.files.get("image") or None
    password = data.get("password") or None

    if image:
        image = base64.b64encode(image.read()).decode('utf-8')

    url = f"{dbm_url}/update/PLAYER"
    data = {
        "session_token": request.headers["Authorization"].split(" ")[1],
        "user_id": user_id,
        "username": sanitize(username),
        "email": email,
        "image": image,
        "password": password
    }
    response = requests.put(url,  timeout=30, verify=False, json=data, headers=generate_session_token_system())
    return send_response(response.json(), response.status_code)

if __name__ == "__main__":
    app.run()

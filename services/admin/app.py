import base64

from flask import Flask

# from services.gacha.app import add_to_inventory
from shared.auth_middleware import *

app = Flask(__name__)

print(SECRET_KEY)
app.config['SECRET_KEY'] = SECRET_KEY
logging.basicConfig(level=logging.DEBUG)

@app.get('/get_all/<user_type>')
@admin_required
def get_all(user_type):
    logging.info(f"Get all users {user_type}")
    url = f"{dbm_url}/get_all/{user_type}"
    response = requests.get(url,  timeout=3, verify=False, headers=generate_session_token_system())
    return send_response(response.json(), response.status_code)


@app.get("/get_user/<user_id>")
@admin_required
def get_user(user_id):
    url = f"{dbm_url}/get_user/" + user_id
    response = requests.get(url,  timeout=3, verify=False, headers=generate_session_token_system())
    return send_response(response.json(), response.status_code)

@app.route('/update', methods=['PUT'])
@admin_required
@login_required_ret
def update_myself(user):
    if not any(request.json):
        return send_response({"error": "No fields to update"}, 400)
    logging.info(f"Received as user value:  {user}")
    data = request.json
    user_id = user['user_id']
    if not user_id:
        return send_response({"error": "Missing user_id parameter"}, 400)
    if jwt.decode(request.headers["Authorization"].split(" ")[1], app.config["SECRET_KEY"], algorithms=["HS256"])["user_type"] != "PLAYER":
        req = requests.get(f"{dbm_url}/get_user/{user_id}",  timeout=3, verify=False, headers=generate_session_token_system())
        user = req.json()
        if not user:
            return send_response({"error": "User not found"}, 404)

    username = data.get("username") or user['username']
    email = data.get("email") or user['email']
    password = data.get("password") or user['password']

    url = f"{admin_url}/update/{user_id}?user_type=ADMIN"
    data = {
        "user_id": user_id,
        "username": username,
        "email": email,
        "password": password
    }
    response = requests.put(url,  timeout=3, verify=False, json=data, headers=request.headers)
    return send_response(response.json(), response.status_code)

@app.route('/update/<user_id>', methods=['PUT'])
@admin_required
def update(user_id):
    user_type = request.args.get("user_type") or "PLAYER"
    user = requests.get(f"{dbm_url}/get_user/{user_type}/{user_id}", timeout=3, verify=False,  headers=generate_session_token_system()).json()
    if not user:
        return send_response({"error": "User not found"}, 404)

    if not any(request.json):
        return send_response({"error": "No fields to update"}, 400)
    logging.info(f"Received as user value:  {user}")
    data = request.json

    username = data.get("username") or user['username']
    email = data.get("email") or user['email']
    password = data.get("password") or None

    url = f"{dbm_url}/update/{user_type}"
    data = {
        "user_id": user_id,
        "username": username,
        "email": email,
        "password": password
    }
    response = requests.put(url,  timeout=3, verify=False, json=data, headers=generate_session_token_system())
    return send_response(response.json(), response.status_code)

# function to get the user balance information
@app.route("/get_user_balance/<user_id>")
@admin_required
def get_user_balance_admin(user_id):
    response = requests.get(f"{dbm_url}/balance/PLAYER",  timeout=3, verify=False,  params={"user_id": user_id}, headers=request.headers)
    return send_response(response.json(), response.status_code)

# Esempio di utilizzo
if __name__ == '__main__':
    app.run()

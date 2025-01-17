import base64
import os
from flask import Flask

mockup = os.getenv("MOCKUP", "0") == "1"

if mockup:
    from auth_middleware import *
else:
    from shared.auth_middleware import *
    
app = Flask(__name__)

gigio = None


app.config['SECRET_KEY'] = SECRET_KEY

@app.get('/get_all/<user_type>')
@admin_required
def get_all(user_type):
    logging.info(f"Get all users {user_type}")
    
    if mockup:
        # Mock implementation
        return send_response(gigio(f"get_all/{user_type}"), 200)
    
    url = f"{dbm_url}/get_all/{user_type}"
    response = requests.get(url,  timeout=30, verify=False, headers=generate_session_token_system())
    return send_response(response.json(), response.status_code)


@app.get("/get_user/<user_id>")
@admin_required
def get_user(user_id):
    logging.info(f"Fetching user with ID: {user_id}")
    
    if mockup:
        # Mock implementation
        return send_response(gigio(f"get_user/{user_id}"), 200)
    
    url = f"{dbm_url}/get_user/" + user_id
    response = requests.get(url,  timeout=30, verify=False, headers=generate_session_token_system())
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
    
    if mockup:
        # Mock implementation
        return send_response(gigio("update", user_id=user_id, json=data),200)
    
    if not user_id:
        return send_response({"error": "Missing user_id parameter"}, 400)
    if decode_session_token(request.headers["Authorization"].split(" ")[1])["user_type"] != "PLAYER":
        req = requests.get(f"{dbm_url}/get_user/{user_id}",  timeout=30, verify=False, headers=generate_session_token_system())
        user = req.json()
        if not user:
            return send_response({"error": "User not found"}, 404)

    username = data.get("username") or user['username']
    email = data.get("email") or user['email']
    password = data.get("password") or None

    url = f"{admin_url}/update/{user_id}?user_type=ADMIN"
    data = {
        "user_id": user_id,
        "username": sanitize(username),
        "email": email,
        "password": password
    }
    response = requests.put(url,  timeout=30, verify=False, json=data, headers=request.headers)
    return send_response(response.json(), response.status_code)

@app.route('/update/<user_id>', methods=['PUT'])
@admin_required
def update(user_id):
    user_type = request.args.get("user_type") or "PLAYER"
    data = request.json

    if mockup:
        # Mock implementation
        return send_response(gigio("update", user_id=user_id, json=data),200)
        
    user = requests.get(f"{dbm_url}/get_user/{user_type}/{user_id}", timeout=30, verify=False,  headers=generate_session_token_system()).json()
    if not user:
        return send_response({"error": "User not found"}, 404)

    if not any(request.json):
        return send_response({"error": "No fields to update"}, 400)
    logging.info(f"Received as user value:  {user}")

    username = data.get("username") or user['username']
    email = data.get("email") or user['email']
    password = data.get("password") or None

    url = f"{dbm_url}/update/{user_type}"
    data = {
        "user_id": user_id,
        "username": sanitize(username),
        "email": email,
        "password": password
    }
    response = requests.put(url,  timeout=30, verify=False, json=data, headers=generate_session_token_system())
    return send_response(response.json(), response.status_code)

# function to get the user balance information
@app.route("/get_user_balance/<user_id>")
@admin_required
def get_user_balance_admin(user_id):
    
    if mockup:
        # Mock implementation
        return send_response(gigio(f"balance/PLAYER",user_id = user_id), 200)
    
    response = requests.get(f"{dbm_url}/balance/PLAYER",  timeout=30, verify=False,  params={"user_id": user_id}, headers=request.headers)
    return send_response(response.json(), response.status_code)

# Esempio di utilizzo
if __name__ == '__main__':
    app.run()

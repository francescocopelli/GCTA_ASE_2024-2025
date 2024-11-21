import base64

from flask import Flask

# from services.gacha.app import add_to_inventory
from shared.auth_middleware import *

app = Flask(__name__)

print(SECRET_KEY)
app.config['SECRET_KEY'] = SECRET_KEY
logging.basicConfig(level=logging.DEBUG)


@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']
    url = f"http://db-manager:5000/login/ADMIN"
    data = {
        "username": username,
        "password": password
    }
    response = requests.post(url, json=data)
    return send_response(response.json(), response.status_code)


@app.route('/logout', methods=['POST'])
def logout():
    username = request.json['username']
    url = f"http://db-manager:5000/logout/ADMIN"
    data = {
        "username": username
    }
    response = requests.post(url, json=data)
    return send_response(response.json(), response.status_code)


@app.route('/reset_pwd', methods=['POST'])
def reset_password():
    email = request.json['email']
    new_password = request.json['new_password']
    url = f"http://db-manager:5000/reset_pwd/ADMIN"
    data = {
        "email": email,
        "new_password": new_password
    }
    response = requests.post(url, json=data)
    return send_response(response.json(), response.status_code)


@app.get('/get_all/<user_type>')
@admin_required
def get_all(user_type):
    logging.info(f"Get all users {user_type}")
    url = f"http://db-manager:5000/get_all/{user_type}"
    response = requests.get(url, headers=generate_session_token_system())
    return send_response(response.json(), response.status_code)


@app.get("/get_user/<user_id>")
@admin_required
def get_user(user_id):
    url = f"http://db-manager:5000/get_user/" + user_id
    response = requests.get(url, headers=generate_session_token_system())
    return send_response(response.json(), response.status_code)

@app.route('/update', methods=['PUT'])
@admin_required
@login_required_ret
def update(user):
    if not any(request.form):
        return send_response({"error": "No fields to update"}, 400)
    logging.info(f"Received as user value:  {user}")
    data = request.form
    user_id = request.args.get("user_id")
    if not user_id:
        return send_response({"error": "Missing user_id parameter"}, 400)
    if jwt.decode(request.headers["Authorization"].split(" ")[1], app.config["SECRET_KEY"], algorithms=["HS256"])["user_type"] != "PLAYER":
        req = requests.get(f"http://db-manager:5000/get_user/{user_id}", headers=generate_session_token_system())
        user = req.json()
        if not user:
            return send_response({"error": "User not found"}, 404)

    username = data.get("username") or user['username']
    email = data.get("email") or user['email']
    image = request.files.get("image") or None

    if image:
        image = base64.b64encode(image.read()).decode('utf-8')

    url = f"http://db-manager:5000/update/PLAYER"
    data = {
        "user_id": user_id,
        "username": username,
        "email": email,
        "image": image
    }
    response = requests.put(url, json=data, headers=generate_session_token_system())
    return send_response(response.json(), response.status_code)

# Esempio di utilizzo
if __name__ == '__main__':
    app.run()

import base64
import re

import bcrypt
from flask import Flask

from shared.auth_middleware import *

# Configura il logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

app.config['SECRET_KEY'] = SECRET_KEY

DATABASE = 'users'
DB_HOST = 'users_db'


def hash_password(password: str):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode()


def check_hash(password: str, hashed_password: str):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


# Endpoint di registrazione per USER e ADMIN
@app.route("/register/<user_type>", methods=["POST"])
def register(user_type):
    if user_type not in ["PLAYER", "ADMIN"]:
        return send_response({"error": "Invalid user type"}, 401)

    try:
        conn = get_db_connection(DB_HOST, DATABASE)
        cursor = conn.cursor(dictionary=True)
        data = request.form
        username = sanitize(data.get("username"))
        password = data.get("password")
        email = data.get("email")
        if not all([username, password, email]):
            return send_response({"error": "Missing required fields"}, 400)
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return send_response({"error": "Invalid email address"}, 400)
        hashed_password = hash_password(password)

        # Inserimento nel database
        if "PLAYER" in user_type:
            image = base64.b64decode(data.get("image")) if data.get("image") else None
            query = (
                "INSERT INTO PLAYER (username, password, email, image, session_token) VALUES (%s,%s,%s,%s,%s)"
            )
            cursor.execute(query, (username, hashed_password, email, image, 0))
        elif "ADMIN" in user_type:
            query = (
                "INSERT INTO ADMIN (username, password, email, session_token) VALUES (%s,%s,%s,%s)"
            )
            cursor.execute(query, (username, hashed_password, email, 0))
        conn.commit()
        return send_response({"message": f"{user_type} registered successfully"}, 200)
    except Exception as e:
        return manage_errors(e)
    finally:
        release_db_connection(conn, cursor)


def authorize(username, password, user_type):
    conn = get_db_connection(DB_HOST, DATABASE)
    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT * FROM PLAYER WHERE username = %s" if "PLAYER" in user_type else "SELECT * FROM ADMIN WHERE username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()

        if user and check_hash(password, user["password"]):
            auth_code = uuid4().hex
            # query = "UPDATE PLAYER SET session_token = %s WHERE username =%s" if "PLAYER" in user_type else "UPDATE ADMIN SET session_token = %s WHERE username =%s"
            query = "INSERT INTO AUTH_CODES(auth_code, user_id, user_type, expires_at) VALUES (%s, %s, %s, %s)"
            expiration = datetime.now() + timedelta(minutes=30)
            cursor.execute(query, (auth_code, user["user_id"], user_type, expiration))
            conn.commit()
            # response.set_cookie('session_token', session_token, httponly=True, secure=True)
            return ({'auth_code': auth_code}), 200
        return ({"error": "Invalid credentials"}), 401

    except Exception as e:
        return manage_errors(e)
    finally:
        release_db_connection(conn, cursor)

def token_release(auth_code, username, user_type):
    conn = get_db_connection(DB_HOST, DATABASE)
    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT * FROM AUTH_CODES WHERE auth_code = %s AND user_type = %s"
        cursor.execute(query, (auth_code,user_type))
        auth = cursor.fetchone()
        if auth and auth["expires_at"] > datetime.now():
            logging.info(f"User {username} logged in successfully")
            token = generate_session_token(auth["user_id"], user_type)
            query = "UPDATE PLAYER SET session_token = %s WHERE username =%s" if "PLAYER" in user_type else "UPDATE ADMIN SET session_token = %s WHERE username =%s"
            cursor.execute(query, (token, username))
            query = "DELETE FROM AUTH_CODES WHERE auth_code = %s AND user_type = %s"
            cursor.execute(query, (auth_code, user_type))
            conn.commit()
            return ({"message": "Login successful",
                            "session_token": token,
                            "user_id": auth["user_id"]}), 200

        return ({"error": "Invalid credentials"}), 401
    except Exception as e:
        return manage_errors(e)
    finally:
        release_db_connection(conn, cursor)


# Endpoint di login per USER e ADMIN
@app.route("/login/<user_type>", methods=["POST"])
def login(user_type):
    if user_type not in ["PLAYER", "ADMIN"]:
        logging.error(f"Invalid user type: {user_type}")
        return send_response({"error": "Invalid user type"}, 400)

    data = request.get_json()
    username = sanitize(data.get("username"))
    password = data.get("password")

    auth_code, status_code = authorize(username, password, user_type)
    if not status_code == 200:
        return send_response({"error": "Invalid credentials"}, status_code)
    return token_release(auth_code['auth_code'], username, user_type)


# Endpoint per il logout
@app.route("/logout", methods=["DELETE"])
@login_required_ret
def logout(user):
    user_type = decode_session_token(user["session_token"])["user_type"]
    if user_type not in ["PLAYER", "ADMIN"]:
        logging.error(f"Invalid user type: {user_type}")
        return send_response({"error": "Invalid user type"}, 401)
    conn = get_db_connection(DB_HOST, DATABASE)
    cursor = conn.cursor(dictionary=True)
    try:

        # Elimina il token dalla tabella PLAYER o ADMIN
        query_delete = "UPDATE PLAYER SET session_token = 0 WHERE user_id =%s" if "PLAYER" in user_type else "UPDATE ADMIN SET session_token = 0 WHERE user_id =%s"
        user_id = user["user_id"]
        cursor.execute(query_delete, (user_id,))
        conn.commit()
        logging.info(f"User with user_id {user_id} logged out successfully")
        return send_response({"message": "Logout successful"}, 200)
    except Exception as e:
        return manage_errors(e)
    finally:
        release_db_connection(conn, cursor)


# Endpoint per visualizzare il saldo della valuta di gioco
@app.route("/balance/<user_type>", methods=["GET"])
@login_required_void
def get_balance(user_type):
    if user_type not in ["PLAYER", "ADMIN"]:
        logging.error(f"Invalid user type: {user_type}")
        return send_response({"error": "Invalid user type"}, 400)

    user_id = request.args.get("user_id")
    if not user_id:
        logging.error("User ID is required")
        return send_response({"error": "User ID is required"}, 400)

    try:
        conn = get_db_connection(DB_HOST, DATABASE)
        cursor = conn.cursor(dictionary=True)
        query = "SELECT currency_balance FROM PLAYER WHERE user_id =%s" if "PLAYER" in user_type else "SELECT currency_balance FROM ADMIN WHERE user_id =%s"
        cursor.execute(query, (user_id,))
        balance = cursor.fetchone()

        if balance:
            logging.info(f"User ID {user_id} balance retrieved successfully")
            return send_response({"currency_balance": balance["currency_balance"]}, 200)
        else:
            logging.warning(f"User not found: {user_id}")
            return send_response({"error": "User not found"}, 408)

    except Exception as e:
        return manage_errors(e)
    finally:
        release_db_connection(conn, cursor)


# Delete profile
@app.route("/delete/<user_type>", methods=["DELETE"])
@admin_required
def delete(user_type):
    if user_type not in ["PLAYER", "ADMIN"]:
        logging.error(f"Invalid user type: {user_type}")
        return send_response({"error": "Invalid user type"}, 400)
    user_id = request.args.get("user_id")
    if not user_id:
        logging.error("User ID is required")
        return send_response({"error": "User ID is required"}, 400)
    try:
        conn = get_db_connection(DB_HOST, DATABASE)
        cursor = conn.cursor(dictionary=True)
        # Elimina il token dalla tabella PLAYER o ADMIN
        query_delete = "DELETE FROM PLAYER WHERE user_id =%s" if "PLAYER" in user_type else "DELETE FROM ADMIN WHERE user_id=%s"
        cursor.execute(query_delete, (user_id,))
        conn.commit()
        logging.info(f"User with session token {user_id} deleted successfully")
        return send_response({"message": "Profile deleted successfully"}, 200)
    except Exception as e:
        return manage_errors(e)
    finally:
        release_db_connection(conn, cursor)


def change_user_info(conn, cursor, user_type, request, column, identifier):
    logging.warning(f"Session token: {identifier}")
    # Verifica se il token si trova nella tabella PLAYER
    query_player = "SELECT * FROM PLAYER WHERE user_id =%s" if "PLAYER" in user_type else "SELECT * FROM ADMIN WHERE user_id =%s"
    if column == "session_token":
        query_player = "SELECT * FROM PLAYER WHERE session_token =%s" if "PLAYER" in user_type else "SELECT * FROM ADMIN WHERE session_token =%s"

    # query_player = "SELECT * FROM PLAYER WHERE " + column + " =%s" if "PLAYER" in user_type else "SELECT * FROM ADMIN WHERE  =%s"
    cursor.execute(query_player, (identifier,))
    token_found = cursor.fetchone()

    if token_found:
        # Update the player profile
        if sanitize(request.json.get("username")):
            query_update = (
                "UPDATE PLAYER SET username = %s WHERE user_id =%s" if "PLAYER" in user_type else "UPDATE ADMIN SET username = %s WHERE user_id =%s"
            )
            if column == "session_token":
                query_update = (
                    "UPDATE PLAYER SET username = %s WHERE session_token =%s" if "PLAYER" in user_type else "UPDATE ADMIN SET username = %s WHERE session_token =%s"
                )

            cursor.execute(query_update, (request.json.get("username"), identifier))
        if request.json.get("password"):
            query_update = (
                "UPDATE PLAYER SET password = %s WHERE user_id =%s" if "PLAYER" in user_type else "UPDATE ADMIN SET password = %s WHERE user_id =%s"
            )
            if column == "session_token":
                query_update = (
                    "UPDATE PLAYER SET password = %s WHERE session_token =%s" if "PLAYER" in user_type else "UPDATE ADMIN SET password = %s WHERE session_token =%s"
                )
            cursor.execute(
                query_update,
                (hash_password(request.json.get("password")), identifier),
            )
        if request.json.get("email"):
            if not re.match(r"[^@]+@[^@]+\.[^@]+", request.json.get("email")):
                return send_response({"error": "Invalid email address"}, 400)
            query_update = (
                "UPDATE PLAYER SET email = %s WHERE user_id =%s" if "PLAYER" in user_type else "UPDATE ADMIN SET email = %s WHERE user_id =%s"

            )
            if column == "session_token":
                query_update = (
                    "UPDATE PLAYER SET email = %s WHERE session_token =%s" if "PLAYER" in user_type else "UPDATE ADMIN SET email = %s WHERE session_token =%s"
                )

            cursor.execute(query_update, (request.json.get("email"), identifier))
        if request.json.get("image"):
            logging.warning("Image found in request" + request.json.get("image"))
            image = base64.b64decode(request.json.get("image"))
            query_update = (
                "UPDATE PLAYER SET image = %s WHERE user_id =%s" if "PLAYER" in user_type else "UPDATE ADMIN SET image = %s WHERE user_id =%s"
            )
            if column == "session_token":
                query_update = (
                    "UPDATE PLAYER SET image = %s WHERE session_token =%s" if "PLAYER" in user_type else "UPDATE ADMIN SET image = %s WHERE session_token=%s"
                )
            cursor.execute(query_update, (image, identifier))

    else:
        return send_response({"error": column + " not found"}, 408)

    conn.commit()
    return send_response({"message": "Profile updated successfully"}, 200)


# create a function to update the player profile
@app.route("/update/<user_type>", methods=["PUT"])
@admin_required
def update(user_type):
    if user_type not in ["PLAYER", "ADMIN"]:
        return send_response({"error": "Invalid user type"}, 400)

    try:
        conn = get_db_connection(DB_HOST, DATABASE)
        cursor = conn.cursor(dictionary=True)
        session_token = request.json.get("session_token") or request.headers["Authorization"].split(" ")[1]

        if decode_session_token(session_token)["user_type"] != "PLAYER":
            return change_user_info(conn, cursor, user_type, request, "user_id", request.json.get("user_id"))
        return change_user_info(conn, cursor, user_type, request, "session_token", session_token)
    except Exception as e:
        return manage_errors(e)
    finally:
        release_db_connection(conn, cursor)


# Create a function that updates user balance of a given user_id with a given amount


@app.route('/update_balance/<user_type>', methods=['PUT'])
@login_required_void
def update_balance_user(user_type):
    if user_type not in ['PLAYER', 'ADMIN']:
        logging.error(f"Invalid user type: {user_type}")
        return send_response({'error': 'Invalid user type'}, 400)

    user_id = request.json.get("user_id")
    amount = request.json.get("amount")
    transaction_type = request.json.get("type")
    if not user_id or not amount or not transaction_type:
        logging.error("user_id, amount, and type are required")
        return send_response({"error": "user_id, amount, and type are required"}, 400)

    try:
        conn = get_db_connection(DB_HOST, DATABASE)
        cursor = conn.cursor(dictionary=True)
        if transaction_type == "credit":
            query_update = "UPDATE PLAYER SET currency_balance = currency_balance + %s WHERE user_id =%s" if "PLAYER" in user_type else "UPDATE ADMIN SET currency_balance = currency_balance + %s WHERE user_id =%s"
        else:
            query_update = "UPDATE PLAYER SET currency_balance = currency_balance - %s WHERE user_id =%s" if "PLAYER" in user_type else "UPDATE ADMIN SET currency_balance = currency_balance - %s WHERE user_id =%s"

        cursor.execute(query_update, (amount, user_id))
        conn.commit()
        logging.info(f"Balance updated successfully for user_id={user_id}")
        return send_response({"message": "Balance updated successfully"}, 200)
    except Exception as e:
        return manage_errors(e)
    finally:
        release_db_connection(conn, cursor)


@app.route("/get_user/<user_id>", methods=["GET"])
@login_required_void
def get_users(user_id):
    url = "https://db-manager:5000/get_user/PLAYER/" + user_id
    response = requests.get(url, timeout=30, verify=False, headers=generate_session_token_system())
    return send_response(response.json(), response.status_code)


@app.route("/get_user/<user_type>/<user_id>", methods=["GET"])
@admin_required
def get_user(user_type, user_id):
    if user_type not in ["PLAYER", "ADMIN"]:
        logging.error(f"Invalid user type: {user_type}")
        return send_response({"error": "Invalid user type"}, 400)

    try:
        conn = get_db_connection(DB_HOST, DATABASE)
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM PLAYER WHERE user_id =%s" if "PLAYER" in user_type else "SELECT * FROM ADMIN WHERE user_id =%s"
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()
        if not user:
            logging.warning(f"User not found: {user_id}")
            return send_response({"error": "User not found"}, 404)
        usr = {
            "user_id": user["user_id"],
            "username": user["username"],
            "email": user["email"],
            "currency_balance": user["currency_balance"],
            "image": base64.b64encode(user["image"]).decode('utf-8') if "PLAYER" in user_type and user[
                "image"] else None,
            "session_token": user["session_token"],
        }
        logging.info(f"User {user_id} retrieved successfully")
        return send_response(usr, 200)
    except Exception as e:
        return manage_errors(e)
    finally:
        release_db_connection(conn, cursor)


@app.route("/get_all/<user_type>", methods=["GET"])
@admin_required
def get_all(user_type):
    if user_type not in ["PLAYER", "ADMIN"]:
        return send_response({"error": "Invalid user type"}, 400)

    try:
        conn = get_db_connection(DB_HOST, DATABASE)
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM PLAYER" if "PLAYER" in user_type else "SELECT * FROM ADMIN"
        cursor.execute(query)
        users = cursor.fetchall()
        logging.info(f"Users retrieved successfully from {user_type} #{users.count}")
        if not users:
            logging.warning(f"No users found")
            return send_response({"error": "No users found"}, 404)
        users_list = []
        for user in users:
            usr = {
                "user_id": user["user_id"],
                "username": user["username"],
                "email": user["email"],
                "currency_balance": user["currency_balance"],
                # "image": base64.b64encode(user["image"]).decode('utf-8') if user["image"] else None,
                "session_token": user["session_token"],
            }
            users_list.append(usr)

        logging.info(f"Users retrieved successfully")
        return send_response({"users": users_list}, 200)

    except Exception as e:
        return manage_errors(e)
    finally:
        release_db_connection(conn, cursor)


# Make the function that delete the user from the database with the given session_token
@app.route('/delete/<user_type>/<session_token>', methods=['DELETE'])
def delete_user(user_type, session_token):
    if user_type not in ['PLAYER', 'ADMIN']:
        logging.error(f"Invalid user type: {user_type}")
        return send_response({'error': 'Invalid user type'}, 400)

    if not session_token:
        logging.error("Session token is required")
        return send_response({"error": "Session token is required"}, 400)

    try:
        conn = get_db_connection(DB_HOST, DATABASE)
        cursor = conn.cursor(dictionary=True)

        # Verify if the session_token exists in the table
        query = "SELECT * FROM PLAYER WHERE session_token =%s" if "PLAYER" in user_type else "SELECT * FROM ADMIN WHERE session_token=%s"
        cursor.execute(query, (session_token,))
        user = cursor.fetchone()

        if user:
            # Delete the user from the table
            query_delete = "DELETE FROM PLAYER WHERE session_token =%s" if "PLAYER" in user_type else "DELETE FROM ADMIN WHERE session_token=%s"
            cursor.execute(query_delete, (session_token,))
            conn.commit()
            logging.info(f"User with session token {session_token} deleted successfully")
            return send_response({"message": "User deleted successfully", "user_id": user["user_id"]}, 200)
        else:
            logging.warning(f"Session token not found: {session_token}")
            return send_response({"error": "Session token not found"}, 404)
    except Exception as e:
        return manage_errors(e)
    finally:
        release_db_connection(conn, cursor)


if __name__ == '__main__':
    app.run()

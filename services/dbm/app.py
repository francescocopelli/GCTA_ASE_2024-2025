import logging
from flask import Flask, request, jsonify, make_response
import sqlite3
import hashlib
import uuid

import requests

# Configura il logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

DATABASE = './users.db/user.db'
transaction_url = "http://transaction:5000"

# make a function that take jason data and return a response


def send_response(message, status_code):
    return jsonify(message), status_code

# Funzione di connessione al database


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Funzione di hashing della password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# Funzione per generare un token di sessione unico
def generate_session_token():
    return str(uuid.uuid4())


# Endpoint di registrazione per USER e ADMIN
@app.route("/register/<user_type>", methods=["POST"])
def register(user_type):
    if user_type not in ["PLAYER", "ADMIN"]:
        return send_response({"error": "Invalid user type"}, 401)

    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        email = data.get("email")
        hashed_password = hash_password(password)

        # Inserimento nel database
        conn = get_db_connection()
        cursor = conn.cursor()
        query = f"INSERT INTO {
            user_type} (username, password, email, currency_balance,session_token) VALUES (?, ?, ?, 0,0)"
        cursor.execute(query, (username, hashed_password, email))
        conn.commit()
        return send_response({"message": f"{user_type} registered successfully"}, 200)
    except sqlite3.IntegrityError:
        return send_response({"error": "Username or email already exists"}, 409)
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return send_response({"error": "Database error"}, 500)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return send_response({"error": "Unexpected error"}, 500)
    finally:
        conn.close()


# Endpoint di login per USER e ADMIN
@app.route("/login/<user_type>", methods=["POST"])
def login(user_type):
    if user_type not in ["PLAYER", "ADMIN"]:
        logging.error(f"Invalid user type: {user_type}")
        return send_response({"error": "Invalid user type"}, 400)

    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        hashed_password = hash_password(password)

        # Verifica delle credenziali
        conn = get_db_connection()
        cursor = conn.cursor()
        query = f"SELECT * FROM {user_type} WHERE username = ? AND password = ?"
        cursor.execute(query, (username, hashed_password))
        user = cursor.fetchone()

        if user:
            session_token = generate_session_token()
            query = f"UPDATE {
                user_type} SET session_token = ? WHERE username = ?"
            cursor.execute(query, (session_token, username))
            conn.commit()
            # response.set_cookie('session_token', session_token, httponly=True, secure=True)
            logging.info(f"User {username} logged in successfully")
            return send_response(({"message": "Login successful", "session_token": session_token, "user_id": user["user_id"]}), 200)
        else:
            logging.warning(f"Invalid credentials for user: {username}")
            return send_response({"error": "Invalid credentials"}, 401)
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return send_response({"error": "Database error"}, 500)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return send_response({"error": "Unexpected error"}, 500)
    finally:
        try:
            cursor.close()
        except Exception as e:
            logging.error(f"Error closing cursor: {e}")
        try:
            conn.close()
        except Exception as e:
            logging.error(f"Error closing connection: {e}")


# Endpoint per il logout
@app.route("/logout/<user_type>", methods=["POST"])
def logout(user_type):
    if user_type not in ["PLAYER", "ADMIN"]:
        logging.error(f"Invalid user type: {user_type}")
        return send_response({"error": "Invalid user type"}, 401)

    session_token = request.json.get("session_token")
    if not session_token or session_token == "0":
        logging.error("Session token is required")
        return send_response({"error": "Session token is required"}, 400)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verifica se il token si trova nella tabella PLAYER o ADMIN
        query = f"SELECT session_token FROM {
            user_type} WHERE session_token = ?"
        cursor.execute(query, (session_token,))
        token_found = cursor.fetchone()

        if token_found:
            # Elimina il token dalla tabella PLAYER o ADMIN
            query_delete = f"UPDATE {
                user_type} SET session_token = 0 WHERE session_token = ?"
            cursor.execute(query_delete, (session_token,))
            conn.commit()
            logging.info(f"User with session token {
                         session_token} logged out successfully")
            return send_response({"message": "Logout successful"}, 200)
        else:
            logging.warning(f"Session token not found: {session_token}")
            return send_response({"error": "Session token not found"}, 408)
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return send_response({"error": "Database error"}, 500)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return send_response({"error": "Unexpected error"}, 500)
    finally:
        try:
            cursor.close()
        except Exception as e:
            logging.error(f"Error closing cursor: {e}")
        try:
            conn.close()
        except Exception as e:
            logging.error(f"Error closing connection: {e}")


# Endpoint per visualizzare il saldo della valuta di gioco
@app.route("/balance/<user_type>", methods=["GET"])
def get_balance(user_type):
    if user_type not in ["PLAYER", "ADMIN"]:
        logging.error(f"Invalid user type: {user_type}")
        return send_response({"error": "Invalid user type"}, 400)

    user_id = request.args.get("user_id")
    if not user_id:
        logging.error("User ID is required")
        return send_response({"error": "User ID is required"}, 400)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = f"SELECT currency_balance FROM {user_type} WHERE user_id = ?"
        cursor.execute(query, (user_id,))
        balance = cursor.fetchone()
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return send_response({"error": "Database error"}, 500)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return send_response({"error": "Unexpected error"}, 500)
    finally:
        try:
            cursor.close()
        except Exception as e:
            logging.error(f"Error closing cursor: {e}")
        try:
            conn.close()
        except Exception as e:
            logging.error(f"Error closing connection: {e}")

    if balance:
        logging.info(f"User ID {user_id} balance retrieved successfully")
        return send_response({"currency_balance": balance["currency_balance"]}, 200)
    else:
        logging.warning(f"User not found: {user_id}")
        return send_response({"error": "User not found"}, 408)


# Delete profile
@app.route("/delete/<user_type>", methods=["DELETE"])
def delete(user_type):
    if user_type not in ["PLAYER", "ADMIN"]:
        logging.error(f"Invalid user type: {user_type}")
        return send_response({"error": "Invalid user type"}, 400)

    session_token = request.json.get("session_token")
    if not session_token:
        logging.error("Session token is required")
        return send_response({"error": "Session token is required"}, 400)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verifica se il token si trova nella tabella PLAYER o ADMIN
        query_player = f"SELECT * FROM {user_type} WHERE session_token = ?"
        cursor.execute(query_player, (session_token,))
        token_found = cursor.fetchone()

        if token_found:
            # Elimina il token dalla tabella PLAYER o ADMIN
            query_delete = f"DELETE FROM {user_type} WHERE session_token = ?"
            cursor.execute(query_delete, (session_token,))
            conn.commit()
            logging.info(f"User with session token {
                         session_token} deleted successfully")
            return send_response({"message": "Profile deleted successfully"}, 200)
        else:
            logging.warning(f"Session token not found: {session_token}")
            return send_response({"error": "Session token not found"}, 408)
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return send_response({"error": "Database error"}, 500)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return send_response({"error": "Unexpected error"}, 500)
    finally:
        try:
            cursor.close()
        except Exception as e:
            logging.error(f"Error closing cursor: {e}")
        try:
            conn.close()
        except Exception as e:
            logging.error(f"Error closing connection: {e}")


# create a function to update the player profile
@app.route("/update/<user_type>", methods=["PUT"])
def update(user_type):
    if user_type not in ["PLAYER", "ADMIN"]:
        return send_response({"error": "Invalid user type"}, 400)

    session_token = request.json.get("session_token")
    if not session_token:
        return send_response({"error": "Session token is required"}, 400)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
    except sqlite3.Error as e:
        logging.error(f"Database connection error: {e}")
        return send_response({"error": "Database connection error"}, 500)

    try:
        # Verifica se il token si trova nella tabella PLAYER
        query_player = "SELECT * FROM " + user_type + " WHERE session_token = ?"
        cursor.execute(query_player, (session_token,))
        token_found = cursor.fetchone()

        if token_found:
            # Update the player profile
            if request.json.get("username"):
                query_update = (
                    "UPDATE " + user_type + " SET username = ? WHERE session_token = ?"
                )
                cursor.execute(
                    query_update, (request.json.get("username"), session_token))
            if request.json.get("password"):
                query_update = (
                    "UPDATE " + user_type + " SET password = ? WHERE session_token = ?"
                )
                cursor.execute(
                    query_update,
                    (hash_password(request.json.get("password")), session_token),
                )
            if request.json.get("email"):
                query_update = (
                    "UPDATE " + user_type + " SET email = ? WHERE session_token = ?"
                )
                cursor.execute(
                    query_update, (request.json.get("email"), session_token))
        else:
            return send_response({"error": "Session token not found"}, 408)

        conn.commit()
        return send_response({"message": "Profile updated successfully"}, 200)
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return send_response({"error": "Database error"}, 500)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return send_response({"error": "Unexpected error"}, 500)
    finally:
        try:
            cursor.close()
        except Exception as e:
            logging.error(f"Error closing cursor: {e}")
        try:
            conn.close()
        except Exception as e:
            logging.error(f"Error closing connection: {e}")

# Create a function that updates user balance of a given user_id with a given amount


@app.route('/update_balance/<user_type>', methods=['PUT'])
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
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verify if the user_id exists in the table
        query = f"SELECT * FROM {user_type} WHERE user_id = ?"
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()
        logging.debug(f"Received: user_id={user_id}, amount={
                      amount}, type={transaction_type}")

        if user:
            if transaction_type == "credit":
                query_update = f"UPDATE {
                    user_type} SET currency_balance = currency_balance + ? WHERE user_id = ?"
            else:
                query_update = f"UPDATE {
                    user_type} SET currency_balance = currency_balance - ? WHERE user_id = ?"

            cursor.execute(query_update, (amount, user_id))
            conn.commit()
            logging.info(f"Balance updated successfully for user_id={user_id}")
            return send_response({"message": "Balance updated successfully"}, 200)
        else:
            logging.warning(f"User not found: user_id={user_id}")
            return send_response({"error": "User not found"}, 404)
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return send_response({"error": "Database error"}, 500)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return send_response({"error": "Unexpected error"}, 500)
    finally:
        try:
            cursor.close()
        except Exception as e:
            logging.error(f"Error closing cursor: {e}")
        try:
            conn.close()
        except Exception as e:
            logging.error(f"Error closing connection: {e}")


@app.route("/get_user/<user_id>", methods=["GET"])
def get_users(user_id):
    return get_user("PLAYER", user_id)


@app.route("/get_user/<user_type>/<user_id>", methods=["GET"])
def get_user(user_type, user_id):
    if user_type not in ["PLAYER", "ADMIN"]:
        logging.error(f"Invalid user type: {user_type}")
        return send_response({"error": "Invalid user type"}, 400)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = f"SELECT user_id, username, email, currency_balance, session_token FROM {
            user_type} WHERE user_id = ?"
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()
        conn.close()
        if not user:
            logging.warning(f"User not found: {user_id}")
            return send_response({"error": "User not found"}, 404)
        usr = {
            "user_id": user["user_id"],
            "username": user["username"],
            "email": user["email"],
            "currency_balance": user["currency_balance"],
            "session_token": user["session_token"],
        }
        logging.info(f"User {user_id} retrieved successfully")
        return send_response(usr, 200)
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return send_response({"error": "Database error"}, 500)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return send_response({"error": "Unexpected error"}, 500)


@app.route("/update_balance/<user_type>", methods=["PUT"])
def update_balance(user_type):
    if user_type not in ["PLAYER", "ADMIN"]:
        logging.error(f"Invalid user type: {user_type}")
        return send_response({"error": "Invalid user type"}, 400)

    user_id = request.json.get("user_id")
    new_balance = request.json.get("new_balance")
    if not user_id or new_balance is None:
        logging.error("user_id and new_balance are required")
        return send_response({"error": "user_id and new_balance are required"}, 400)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = f"UPDATE {
            user_type} SET currency_balance = ? WHERE user_id = ?"
        cursor.execute(query, (new_balance, user_id))
        conn.commit()
        if cursor.rowcount == 0:
            logging.warning(f"User not found: {user_id}")
            return send_response({"error": "User not found"}, 404)
        logging.info(f"Balance updated successfully for user_id={user_id}")
        return send_response({"message": "Balance updated successfully"}, 200)
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return send_response({"error": "Database error"}, 500)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return send_response({"error": "Unexpected error"}, 500)
    finally:
        try:
            cursor.close()
        except Exception as e:
            logging.error(f"Error closing cursor: {e}")
        try:
            conn.close()
        except Exception as e:
            logging.error(f"Error closing connection: {e}")

#Make the function that delete the user from the database with the given session_token
@app.route('/delete/<user_type>/<session_token>', methods=['DELETE'])
def delete_user(user_type,session_token):
    if user_type not in ['PLAYER', 'ADMIN']:
        logging.error(f"Invalid user type: {user_type}")
        return send_response({'error': 'Invalid user type'}, 400)

    if not session_token:
        logging.error("Session token is required")
        return send_response({"error": "Session token is required"}, 400)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verify if the session_token exists in the table
        query = f"SELECT * FROM {user_type} WHERE session_token = ?"
        cursor.execute(query, (session_token,))
        user = cursor.fetchone()

        if user:
            # Delete the user from the table
            query_delete = f"DELETE FROM {user_type} WHERE session_token = ?"
            cursor.execute(query_delete, (session_token,))
            conn.commit()
            logging.info(f"User with session token {session_token} deleted successfully")
            return send_response({"message": "User deleted successfully", "user_id": user["user_id"]}, 200)
        else:
            logging.warning(f"Session token not found: {session_token}")
            return send_response({"error": "Session token not found"}, 404)
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return send_response({"error": "Database error"}, 500)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return send_response({"error": "Unexpected error"}, 500)
    finally:
        try:
            cursor.close()
        except Exception as e:
            logging.error(f"Error closing cursor: {e}")
        try:
            conn.close()
        except Exception as e:
            logging.error(f"Error closing connection: {e}")

if __name__ == '__main__':
    app.run()

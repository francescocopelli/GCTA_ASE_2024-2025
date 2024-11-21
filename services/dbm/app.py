import base64
import hashlib
import logging
import os
import sqlite3
import uuid
from datetime import datetime, timedelta

from flask import Flask, request, jsonify, make_response
from shared.auth_middleware import *

# Configura il logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
SECRET_KEY = os.environ.get('SECRET_KEY') or 'this is a secret'
print(SECRET_KEY)
app.config['SECRET_KEY'] = SECRET_KEY

DATABASE = './users.db/user.db'
transaction_url = "http://transaction:5000"

import time
from threading import Lock
from functools import wraps

# Circuit breaker variables
DB_ERROR_THRESHOLD = 5  # Maximum number of errors before tripping the circuit
COOLDOWN_PERIOD = 30    # Time in seconds before attempting to recover

# Circuit breaker state
circuit_breaker_state = {
    "failure_count": 0,
    "last_failure_time": None,
    "is_open": False,
    "lock": Lock()
}

# Circuit breaker decorator
def circuit_breaker(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with circuit_breaker_state["lock"]:
            # Check if the circuit is open
            if circuit_breaker_state["is_open"]:
                elapsed_time = time.time() - circuit_breaker_state["last_failure_time"]
                if elapsed_time > COOLDOWN_PERIOD:
                    # Reset the circuit breaker after cooldown
                    circuit_breaker_state["failure_count"] = 0
                    circuit_breaker_state["is_open"] = False
                else:
                    # Circuit is still open
                    logging.error("Circuit breaker is open. Rejecting the request.")
                    return jsonify({"error": "Database is temporarily unavailable"}), 503

        # Try executing the function
        try:
            result = func(*args, **kwargs)
            logging.info(f"result: {result}")
            if circuit_breaker_state["failure_count"] > 0:
                # Reset failure count if the request is successful
                with circuit_breaker_state["lock"]:
                    circuit_breaker_state["failure_count"] = 0
                    logging.info(f"counter: {circuit_breaker_state['failure_count']}")
                return result
        except sqlite3.Error as e:
            with circuit_breaker_state["lock"]:
                # Increment failure count and check threshold
                circuit_breaker_state["failure_count"] += 1
                logging.error(f"Database error: {e}")
                if circuit_breaker_state["failure_count"] >= DB_ERROR_THRESHOLD:
                    circuit_breaker_state["is_open"] = True
                    circuit_breaker_state["last_failure_time"] = time.time()
                    logging.critical("Circuit breaker tripped due to repeated database failures.")
            return jsonify({"error": f'Database error11111111111111111111111111111111 {circuit_breaker_state["failure_count"]}'}), 500
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            circuit_breaker_state["failure_count"] +=1
            if circuit_breaker_state["failure_count"] >= DB_ERROR_THRESHOLD:
                    circuit_breaker_state["is_open"] = True
                    circuit_breaker_state["last_failure_time"] = time.time()
                    logging.critical("Circuit breaker tripped due to repeated errors.")
            return jsonify({"error": f'Database error00000000000000000000000000000000000 {circuit_breaker_state["failure_count"]}'}), 500

    return wrapper


# Funzione di connessione al database
@circuit_breaker
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Funzione di hashing della password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# Funzione per generare un token di sessione unico
def generate_session_token(user_id, user_type):
    logging.debug(user_type)
    exp = datetime.now() + timedelta(hours=6)
    return jwt.encode({'user_id': user_id, "user_type": user_type, "expiration":str(exp)}, app.config['SECRET_KEY'], algorithm='HS256')
    # return str(uuid.uuid4())


# Endpoint di registrazione per USER e ADMIN
@app.route("/register/<user_type>", methods=["POST"])
@circuit_breaker
def register(user_type):
    if user_type not in ["PLAYER", "ADMIN"]:
        return send_response({"error": "Invalid user type"}, 401)

    conn = get_db_connection()
    try:
        data = request.form
        username = data.get("username")
        password = data.get("password")
        email = data.get("email")
        image = base64.b64decode(data.get("image")) if data.get("image") else None

        hashed_password = hash_password(password)

        # Inserimento nel database
        cursor = conn.cursor()
        query = f"INSERT INTO {user_type} (username, password, email, image) VALUES (?, ?, ?,?)"
        cursor.execute(query, (username, hashed_password, email,image))
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
@circuit_breaker
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
            session_token = generate_session_token(user_id=user["user_id"], user_type=user_type)
            query = f"UPDATE {user_type} SET session_token = ? WHERE username = ?"
            cursor.execute(query, (session_token, username))
            conn.commit()
            # response.set_cookie('session_token', session_token, httponly=True, secure=True)
            logging.info(f"User {username} logged in successfully")
            return send_response(({"message": "Login successful", "session_token": session_token,
                                   'user_id': user["user_id"]}), 200)
        else:
            logging.warning(f"Invalid credentials for user: {username}")
            return send_response({"error": "Invalid credentials"}, 401)
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        raise e
        #return send_response({"error": "Database error"}, 500)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise e
        #return send_response({"error": "Unexpected error"}, 500)


# Endpoint per il logout
@app.route("/logout/<user_type>", methods=["POST"])
@circuit_breaker
@login_required_ret
def logout(user_type):
    if user_type not in ["PLAYER", "ADMIN"]:
        logging.error(f"Invalid user type: {user_type}")
        return send_response({"error": "Invalid user type"}, 401)
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Elimina il token dalla tabella PLAYER o ADMIN
        query_delete = f"UPDATE {user_type} SET session_token = 0 WHERE user_id = ?"
        user_id = jwt.decode(request.headers["Authorization"].split(" ")[1], app.config['SECRET_KEY'], algorithms=["HS256"])["user_id"]
        cursor.execute(query_delete, (user_id,))
        conn.commit()
        logging.info(f"User with user_id {user_id} logged out successfully")
        return send_response({"message": "Logout successful"}, 200)
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
@circuit_breaker
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
@circuit_breaker
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
            logging.info(f"User with session token {session_token} deleted successfully")
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
@circuit_breaker
# @token_required_void
def update(user_type):
    if user_type not in ["PLAYER", "ADMIN"]:
        return send_response({"error": "Invalid user type"}, 400)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
    except sqlite3.Error as e:
        logging.error(f"Database connection error: {e}")
        return send_response({"error": "Database connection error"}, 500)
    session_token = request.headers["Authorization"].split(" ")[1]
    try:
        logging.warning(f"Session token: {session_token}")
        # Verifica se il token si trova nella tabella PLAYER
        query_player = "SELECT * FROM " + user_type + " WHERE session_token = ?"
        cursor.execute(query_player, (session_token,))
        token_found = cursor.fetchone()
        logging.info(f"Token found: {token_found}")
        if token_found:
            # Update the player profile
            if request.json.get("username"):
                query_update = (
                    "UPDATE " + user_type + " SET username = ? WHERE session_token = ?"
                )
                cursor.execute(query_update, (request.json.get("username"), session_token))
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
                cursor.execute(query_update, (request.json.get("email"), session_token))
            if request.json.get("image"):
                logging.warning("Image found in request" + request.json.get("image"))
                image = base64.b64decode(request.json.get("image"))
                query_update = (
                    "UPDATE " + user_type + " SET image = ? WHERE session_token = ?"
                )
                cursor.execute(query_update, (image, session_token))

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
@circuit_breaker
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
        logging.debug(f"Received: user_id={user_id}, amount={amount}, type={transaction_type}")

        if user:
            if transaction_type == "credit":
                query_update = f"UPDATE {user_type} SET currency_balance = currency_balance + ? WHERE user_id = ?"
            else:
                query_update = f"UPDATE {user_type} SET currency_balance = currency_balance - ? WHERE user_id = ?"

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
@circuit_breaker
def get_user(user_type, user_id):
    if user_type not in ["PLAYER", "ADMIN"]:
        logging.error(f"Invalid user type: {user_type}")
        return send_response({"error": "Invalid user type"}, 400)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = f"SELECT * FROM {user_type} WHERE user_id = ?"
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
            "image": base64.b64encode(user["image"]).decode('utf-8') if "PLAYER" in user_type and user["image"] else None,
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
@circuit_breaker
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
        query = f"UPDATE {user_type} SET currency_balance = ? WHERE user_id = ?"
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

@app.route("/get_all/<user_type>", methods=["GET"])
@circuit_breaker
@admin_required
def get_all(user_type):
    if user_type not in ["PLAYER", "ADMIN"]:
        return send_response({"error": "Invalid user type"}, 400)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = f"SELECT * FROM {user_type}"
        cursor.execute(query)
        users = cursor.fetchall()
        logging.info(f"Users retrieved successfully from {user_type} #{users.count}")
        conn.close()
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
        return send_response({"users":users_list}, 200)
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return send_response({"error": "Database error"}, 500)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return send_response({"error": "Unexpected error"}, 500)

if __name__ == '__main__':
    app.run()

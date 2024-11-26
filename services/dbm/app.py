import base64
#import hashlib
import bcrypt
import re
import sqlite3

from flask import Flask

from shared.auth_middleware import *

# Configura il logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

app.config['SECRET_KEY'] = SECRET_KEY

DATABASE = './users.db/user.db'


# Funzione di connessione al database


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password:str):
    salt=bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'),salt).decode()


def check_hash(password:str,hashed_password:str):
    return bcrypt.checkpw(password.encode('utf-8'),hashed_password.encode('utf-8'))
'''
# Funzione di hashing della password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()
'''

# Funzione per generare un token di sessione unico
def generate_session_token(user_id, user_type):
    logging.debug(user_type)
    exp = datetime.now() + timedelta(hours=6)
    return jwt.encode({'user_id': user_id, "user_type": user_type, "expiration": str(exp)}, app.config['SECRET_KEY'],
                      algorithm='HS256')
    # return str(uuid.uuid4())


# Endpoint di registrazione per USER e ADMIN
@app.route("/register/<user_type>", methods=["POST"])
def register(user_type):
    if user_type not in ["PLAYER", "ADMIN"]:
        return send_response({"error": "Invalid user type"}, 401)

    conn = get_db_connection()
    try:
        data = request.form
        logging.info(f'Se nel mondo esistesse un po\' di {data}')
        username = data.get("username")
        password = data.get("password")
        email = data.get("email")
        if not all([username, password, email]):
            return send_response({"error": "Missing required fields"}, 400)
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return send_response({"error": "Invalid email address"}, 400)
        hashed_password = hash_password(password)

        # Inserimento nel database
        cursor = conn.cursor()
        if "PLAYER" in user_type:
            image = base64.b64decode(data.get("image")) if data.get("image") else None
            query = (
                "INSERT INTO PLAYER (username, password, email, image, session_token) VALUES (?, ?, ?, ?, 0)"
            )
            cursor.execute(query, (username, hashed_password, email, image))
        elif "ADMIN":
            query = (
                "INSERT INTO ADMIN (username, password, email, session_token) VALUES (?, ?, ?, 0)"
            )
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
        #logging.info("Password is " + password +"which is of type "+str(type(password)))

        # Verifica delle credenziali
        conn = get_db_connection()
        cursor = conn.cursor()
        query = f"SELECT user_id, password FROM {user_type} WHERE username = ?"
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        if user and check_hash(password,user["password"]):
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
@app.route("/logout", methods=["DELETE"])
@login_required_ret
def logout(user):
    user_type = jwt.decode(user["session_token"], app.config['SECRET_KEY'], algorithms=["HS256"])["user_type"]
    if user_type not in ["PLAYER", "ADMIN"]:
        logging.error(f"Invalid user type: {user_type}")
        return send_response({"error": "Invalid user type"}, 401)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:

        # Elimina il token dalla tabella PLAYER o ADMIN
        query_delete = f"UPDATE {user_type} SET session_token = 0 WHERE user_id = ?"
        user_id = user["user_id"]
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
            if cursor:
                cursor.close()
        except Exception as e:
            logging.error(f"Error closing cursor: {e}")
        try:
            if conn: conn.close()
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


def change_user_info(conn, cursor, user_type, request, column, identifier):
    logging.warning(f"Session token: {identifier}")
    # Verifica se il token si trova nella tabella PLAYER
    query_player = "SELECT * FROM " + user_type + " WHERE " + column + " = ?"
    cursor.execute(query_player, (identifier,))
    token_found = cursor.fetchone()

    if token_found:
        # Update the player profile
        if request.json.get("username"):
            query_update = (
                    "UPDATE " + user_type + " SET username = ? WHERE " + column + " = ?"
            )
            cursor.execute(query_update, (request.json.get("username"), identifier))
        if request.json.get("password"):
            query_update = (
                    "UPDATE " + user_type + " SET password = ? WHERE " + column + " = ?"
            )
            cursor.execute(
                query_update,
                (hash_password(request.json.get("password")), identifier),
            )
        if request.json.get("email"):
            query_update = (
                    "UPDATE " + user_type + " SET email = ? WHERE " + column + " = ?"
            )
            cursor.execute(query_update, (request.json.get("email"), identifier))
        if request.json.get("image"):
            logging.warning("Image found in request" + request.json.get("image"))
            image = base64.b64decode(request.json.get("image"))
            query_update = (
                    "UPDATE " + user_type + " SET image = ? WHERE " + column + " = ?"
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
        conn = get_db_connection()
        cursor = conn.cursor()
    except sqlite3.Error as e:
        logging.error(f"Database connection error: {e}")
        return send_response({"error": "Database connection error"}, 500)
    try:
        session_token = request.json.get("session_token") or request.headers["Authorization"].split(" ")[1]

        if jwt.decode(session_token, app.config['SECRET_KEY'], algorithms=["HS256"])["user_type"] != "PLAYER":
            return change_user_info(conn, cursor, user_type, request, "user_id", request.json.get("user_id"))
        return change_user_info(conn, cursor, user_type, request, "session_token", session_token)

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
@login_required_void
def get_users(user_id):
    url = f"https://db-manager:5000/get_user/PLAYER/" + user_id
    response = requests.get(url,  timeout=10, headers=generate_session_token_system(),verify=False)
    return send_response(response.json(), response.status_code)


@app.route("/get_user/<user_type>/<user_id>", methods=["GET"])
@admin_required
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
            "image": base64.b64encode(user["image"]).decode('utf-8') if "PLAYER" in user_type and user[
                "image"] else None,
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


@app.route("/get_all/<user_type>", methods=["GET"])
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
        return send_response({"users": users_list}, 200)
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return send_response({"error": "Database error"}, 500)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return send_response({"error": "Unexpected error"}, 500)


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

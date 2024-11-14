import logging
from flask import Flask, request, jsonify, make_response
import sqlite3
import hashlib
import uuid

# Configura il logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

DATABASE = './users.db/user.db'


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
@app.route('/register/<user_type>', methods=['POST'])
def register(user_type):
    if user_type not in ['PLAYER', 'ADMIN']:
        return jsonify({'error': 'Invalid user type'}), 400

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    hashed_password = hash_password(password)

    # Inserimento nel database
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = f"INSERT INTO {user_type} (username, password, email, currency_balance,session_token) VALUES (?, ?, ?, 0,0)"
        cursor.execute(query, (username, hashed_password, email))
        conn.commit()
        conn.close()
        return jsonify({'message': f'{user_type} registered successfully'}), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Username or email already exists'}), 409


# Endpoint di login per USER e ADMIN
@app.route('/login/<user_type>', methods=['POST'])
def login(user_type):
    if user_type not in ['PLAYER', 'ADMIN']:
        return jsonify({'error': 'Invalid user type'}), 400

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    hashed_password = hash_password(password)

    # Verifica delle credenziali
    conn = get_db_connection()
    cursor = conn.cursor()
    query = f"SELECT * FROM {user_type} WHERE username = ? AND password = ?"
    cursor.execute(query, (username, hashed_password))
    user = cursor.fetchone()

    if user:
        session_token = generate_session_token()
        query = f"UPDATE {user_type} SET session_token = ? WHERE username = ?"
        cursor.execute(query, (session_token, username))
        conn.commit()
        cursor.close()
        conn.close()

        # Crea una risposta e imposta il cookie
        response = make_response(jsonify({'message': 'Login successful', 'session_token': session_token}))
        # response.set_cookie('session_token', session_token, httponly=True, secure=True)

        return response
    else:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Invalid credentials'}), 401


# Endpoint per il logout
@app.route('/logout/<user_type>', methods=['POST'])
def logout(user_type):
    if user_type not in ['PLAYER', 'ADMIN']:
        return jsonify({'error': 'Invalid user type'}), 400

    session_token = request.json.get('session_token')
    if not session_token or session_token == "0":
        return jsonify({'error': 'Session token is required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Verifica se il token si trova nella tabella PLAYER
    query_player = "SELECT session_token FROM " + user_type + " WHERE session_token = ?"
    cursor.execute(query_player, (session_token,))
    token_found = cursor.fetchone()

    if token_found:
        # Elimina il token dalla tabella ADMIN
        query_delete_admin = "UPDATE " + user_type + " SET session_token = 0 WHERE session_token = ?"
        cursor.execute(query_delete_admin, (session_token,))
    else:
        conn.close()
        return jsonify({'error': 'Session token not found'}), 404

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': 'Logout successful'}), 200


# Endpoint per visualizzare il saldo della valuta di gioco
@app.route('/balance/<user_type>', methods=['GET'])
def get_balance(user_type):
    if user_type not in ['PLAYER', 'ADMIN']:
        return jsonify({'error': 'Invalid user type'}), 400

    username = request.args.get('username')
    conn = get_db_connection()
    cursor = conn.cursor()
    query = f"SELECT currency_balance FROM {user_type} WHERE username = ?"
    cursor.execute(query, (username,))
    balance = cursor.fetchone()
    conn.close()

    if balance:
        return jsonify({'currency_balance': balance['currency_balance']})
    else:
        return jsonify({'error': 'User not found'}), 404


@app.get("/get_user/<user_id>")
def get_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT user_id, username,email,currency_balance,session_token FROM PLAYER WHERE user_id = ?"
    cursor.execute(query, (user_id,))
    user = cursor.fetchone()
    conn.close()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    usr = {
        'user_id': user['user_id'],
        'username': user['username'],
        'email': user['email'],
        'currency_balance': user['currency_balance'],
        'session_token': user['session_token']
    }
    return jsonify(usr), 200

@app.route("/update_balance", methods=['PUT'])
def update_balance():
    user_id = request.json['user_id']
    new_balance = request.json['new_balance']
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "UPDATE PLAYER SET currency_balance = ? WHERE user_id = ?"
    cursor.execute(query, (new_balance, user_id))
    conn.commit()
    conn.close()
    if cursor.rowcount == 0:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'message': 'Balance updated successfully'}), 200

if __name__ == '__main__':
    app.run()

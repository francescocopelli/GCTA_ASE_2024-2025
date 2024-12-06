import logging
import os
from datetime import datetime, timedelta
from uuid import uuid4

mockup = os.getenv("MOCKUP", "0") == "1"
import jwt

if not mockup:
    import requests

import re
from flask import request, abort, jsonify, current_app


def sanitize(user_input):
    if type(user_input) is not str:
        return user_input
    return re.sub(r'[^_\-a-zA-Z0-9]', '', user_input)


def florence(filename="/run/secrets/novel"):
    poetry = ""
    try:
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()  # Remove surrounding whitespace
                if not line:  # If the line is empty, add a space
                    poetry += " "
                else:
                    poetry += line[0]  # Add the first letter of the line
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return poetry


SECRET_KEY = florence()

transaction_url = "https://transaction:5000"
user_url = "https://user_player:5000"
gacha_url = "https://gacha:5000"
dbm_url = "https://db-manager:5000"
admin_url = "https://user_admin:5000"
# mancano admin e player authentication

import time
from threading import Lock
from functools import wraps

# Constants
DB_ERROR_THRESHOLD = 5
COOLDOWN_PERIOD = 20  # In seconds

import logging
from mysql.connector import *


# Utilizzo della classe

def get_db_connection(db_host, db_name):
    with open("/run/secrets/db_user") as f:
        with open("/run/secrets/db_password") as f1:
            username, password = f.readline(), f1.readline()
            config = {
                'user': username,
                'password': password,
                'host': db_host,
                'database': db_name,
                'ssl_ca': '/run/secrets/ca.pem',
                'ssl_cert': '/run/secrets/client-cert.pem',
                'ssl_key': '/run/secrets/client-key.pem',
                'tls_versions': ['TLSv1.2', 'TLSv1.3'],
                'connection_timeout': 30
            }
            return connect(**config)


def release_db_connection(conn, cursor=None):
    if cursor:
        cursor.close()
    if conn:
        conn.close()


class CircuitBreaker:
    def __init__(self, error_threshold, cooldown_period):
        self.error_threshold = error_threshold
        self.cooldown_period = cooldown_period
        self.failure_count = 0
        self.last_failure_time = None
        self.is_open = False
        self.lock = Lock()

    def reset(self):
        """Reset the circuit breaker state."""
        self.failure_count = 0
        self.is_open = False
        self.last_failure_time = None

    def trip(self):
        """Trip the circuit breaker."""
        self.is_open = True
        self.last_failure_time = time.time()

    def check_state(self):
        """Check if the circuit breaker should be reset based on cooldown."""
        if self.is_open:
            elapsed_time = time.time() - self.last_failure_time
            if elapsed_time > self.cooldown_period:
                self.reset()


# Instantiate the circuit breaker
circuit_breaker = CircuitBreaker(DB_ERROR_THRESHOLD, COOLDOWN_PERIOD)


# Circuit breaker decorator
def circuit_breaker_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with circuit_breaker.lock:
            circuit_breaker.check_state()
            if circuit_breaker.is_open:
                logging.error("Circuit breaker is open. Rejecting the request.")
                return jsonify({"error": "Database is temporarily unavailable"}), 603

        # Execute the function
        try:
            result = func(*args, **kwargs)
            if not result is Exception:
                circuit_breaker.reset()
            return result

        except Error as e:
            with circuit_breaker.lock:
                circuit_breaker.failure_count += 1
                logging.error(f"Database error: {e}")
                if circuit_breaker.failure_count >= circuit_breaker.error_threshold:
                    circuit_breaker.trip()
                    logging.critical("Circuit breaker tripped due to repeated database failures.")
            return jsonify({"error": "Database error occurred"}), 600

        except Exception as e:
            with circuit_breaker.lock:
                circuit_breaker.failure_count += 1
                logging.error(f"Unexpected error: {e.args[0]}")
                if circuit_breaker.failure_count >= circuit_breaker.error_threshold:
                    circuit_breaker.trip()
                    logging.critical("Circuit breaker tripped due to repeated errors.")
            return jsonify({"error": "An unexpected error occurred"}), 602

    return wrapper


# make a function that take json data and return a response
@circuit_breaker_decorator
def send_response(message, status_code):
    if mockup: return jsonify(message), status_code
    if status_code == 500:
        raise Exception(message)
    return jsonify(message), status_code


def is_system_call(token):
    logging.warning("Checking if system call token: " + token)
    try:
        data = decode_session_token(token)
        logging.warning(f"Data: {data}")
        return data["user_id"] == "SYSTEM" and data["user_type"] == "SYSTEM" and token_is_valid(data["exp"])
    except Exception as e:
        logging.error(f"Error: {e}")
        return False


def decode_session_token(token):
    if mockup:
        return {
            "jti": "mockup",
            "iss": "GCTA_24_25",
            "sub": "PLAYER_access",
            "iat": datetime.now(),
            "nbf": datetime.now(),
            "exp": (datetime.now() + timedelta(hours=1)),
            "aud": "ALL",
            "user_id": "1",
            "user_type": "PLAYER",
            "scope": "system_operations",
        }
    return jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"], audience="ALL")


def generate_session_token(user_id, user_type, expiration_hours=1):
    """
    Genera un JWT per un utente basato sul suo tipo.    :param user_id: ID univoco dell'utente
    :param user_type: Tipo di utente ('PLAYER', 'ADMIN', 'SYSTEM')    :param expiration_hours: Ore di validità del token
    :return: Dizionario con l'header Authorization    """
    if user_type not in ["PLAYER", "ADMIN", "SYSTEM"]:
        raise ValueError("Tipo di utente non valido. Deve essere 'PLAYER', 'ADMIN' o 'SYSTEM'.")

    headers = {
        "alg": "HS256",
        "typ": "JWT"  # Tipo di token
    }
    current_datetime = datetime.now() - timedelta(minutes=1)
    payload = {
        "jti": uuid4().hex,
        "iss": "GCTA_24_25",  # Issuer
        "sub": f"{user_type}_access",  # Subject (es. PLAYER_access, ADMIN_access)
        "iat": current_datetime,  # Data di creazione
        "nbf": current_datetime,  # Not Before
        "exp": (current_datetime + timedelta(hours=expiration_hours, minutes=1)),  # Expiration time
        "aud": "ALL",  # Audience
        # Public claims
        "user_id": user_id,
        "user_type": user_type}
    # Aggiunta di claim specifici per tipo di utente
    if user_type == "PLAYER":
        payload["scope"] = "game_access"
    elif user_type == "ADMIN":
        payload["scope"] = "admin_panel"
    elif user_type == "SYSTEM":
        payload["scope"] = "system_operations"
    # Generazione del token JWT
    token = jwt.encode(
        payload=payload,
        key=current_app.config["SECRET_KEY"],
        algorithm="HS256",
        headers=headers
    )
    return token


def generate_session_token_system():
    token = generate_session_token("SYSTEM", "SYSTEM")
    return {"Authorization": f"Bearer {token}"}


def check_header():
    logging.debug(f"Request headers: {request.headers}")
    if not "X-Gateway-Port" in request.headers:
        return False
    if "8081" in request.headers['X-Gateway-Port']:
        return True
    return False


def token_is_valid(expiration_date):
    return datetime.now() < datetime.fromtimestamp(expiration_date)


def _f(require_return, f, *args, **kwargs):
    logging.info("Token required checking")
    token = None
    logging.debug(f"Request headers: {request}")
    if not mockup:
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]

        if not token:
            logging.error("Token is missing")
            abort(401, "Authentication Token is missing!")
        if is_system_call(token):
            return f(*args, **kwargs)
    try:
        if not mockup:
            logging.debug(f"Token: {token}")
            data = decode_session_token(token)
            logging.debug("Expiration time: " + str(data["exp"]))

            if not (token_is_valid(data["exp"])):
                abort(401, "Token expired!")

            rst = requests.get(f"{dbm_url}/get_user/{data['user_type']}/{data['user_id']}", timeout=30, verify=False,
                               headers=generate_session_token_system())
            current_user = rst.json()

            if current_user is None:
                abort(401, "Invalid Authentication token!")

            if not current_user["session_token"] == token:
                abort(401, "Token mismatch!")
        else:
            current_user = {
                "user_id": "1",
                "username": "admin",
                "email": ""
            }

    except Exception as e:
        return {
            "message": "Something went wrong",
            "data": None,
            "error": str(e)
        }, 500

    return f(current_user, *args, **kwargs) if require_return else f(*args, **kwargs)


def token_required_ret(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        return _f(True, f, *args, **kwargs)

    return decorated


def token_required_void(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        return _f(False, f, *args, **kwargs)

    return decorated


def login_required_void(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        return _f(False, f, *args, **kwargs)

    return decorated


def login_required_ret(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        return _f(True, f, *args, **kwargs)

    return decorated


def admin_required(f):
    def admin_f(require_return, f, *args, **kwargs):
        if mockup and not require_return: return f(*args, **kwargs)
        token = None
        if not mockup:
            if "Authorization" in request.headers:
                token = request.headers["Authorization"].split(" ")[1]
            if not token:
                logging.error("Token is missing")
                abort(401, "Authentication Token is missing!")

            if is_system_call(token):
                return f(*args, **kwargs)

            if not check_header():
                abort(403, "Unauthorized access!")

            logging.info("Admin required check")

            data = decode_session_token(token)

            if not (token_is_valid(data["exp"])):
                abort(401, "Token expired!")
            logging.info(f"Data: {data}")
            # user_id = int(data["user_id"]) if not type(data["user_id"]) == int else data["user_id"]
            user_id = data["user_id"]
            logging.info(f"User id: {user_id}")
        try:
            if not mockup:

                rst = requests.get(f"{dbm_url}/get_user/ADMIN/{user_id}", timeout=30, verify=False,
                                   headers=generate_session_token_system())

                current_user = rst.json()
            else:
                current_user = {
                    "user_id": "1",
                    "username": "admin",
                    "email": ""
                }
                rst = {"status_code": 200, "message": "Mockup test response"}
            logging.info(f"Response: {current_user}")
            logging.info(f"Response original: {rst}")

            if not rst.status_code == 200:
                abort(403, "Unauthorized access! Maybe")
            logging.info(f"Current user: {current_user}")

            if not mockup and not current_user["session_token"] == token:
                abort(401, "Token mismatch!")

        except Exception as e:
            abort(500, str(e))

        return f(current_user, *args, **kwargs) if require_return else f(*args, **kwargs)

    @wraps(f)
    def decorated(*args, **kwargs):
        return admin_f(False, f, *args, **kwargs)

    return decorated


def manage_errors(exception):
    logging.error(f"Error: {exception}")
    return send_response({"error": str(exception)}, 500)

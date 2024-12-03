import logging
import os
from datetime import datetime, timedelta

import jwt
import requests
from flask import request, abort, jsonify, current_app

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
logging.basicConfig(level=logging.DEBUG)

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
from queue import Queue

import logging
from queue import Queue
from mysql.connector import *

# Utilizzo della classe

def get_db_connection(db_host,db_name):
    with open("/run/secrets/db_user") as f:
        with open("/run/secrets/db_password") as f1:
            username, password = f.readline(), f1.readline()
            return connect(host=db_host, user=username, password=password, database=db_name)

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
    if status_code == 500:
        raise Exception(message)
    return jsonify(message), status_code



def is_system_call(token):
    logging.warning("Checking if system call token: " + token)
    try:
        data = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        logging.warning(f"Data: {data}")
        return data["user_id"] == "SYSTEM" and data["user_type"] == "SYSTEM" and token_is_valid(data["expiration"])
    except Exception as e:
        logging.error(f"Error: {e}")
        return False


def generate_session_token_system():
    data = jwt.encode(
        {"user_id": "SYSTEM", "user_type": "SYSTEM", "expiration": str(datetime.now() + timedelta(hours=1, minutes=1))},
        current_app.config["SECRET_KEY"], algorithm="HS256")
    return {"Authorization": f"Bearer {data}"}


def check_header():
    logging.debug(f"Request headers: {request.headers}")
    if not "X-Gateway-Port" in request.headers:
        return False
    if "8081" in request.headers['X-Gateway-Port']:
        return True
    return False


def token_is_valid(expiration_date_str):
    expiration_date = datetime.strptime(expiration_date_str, "%Y-%m-%d %H:%M:%S.%f")
    return expiration_date > datetime.now()


def _f(require_return, f, *args, **kwargs):
    logging.info("Token required checking")
    token = None
    logging.debug(f"Request headers: {request}")
    if "Authorization" in request.headers:
        token = request.headers["Authorization"].split(" ")[1]

    if not token:
        logging.error("Token is missing")
        abort(401, "Authentication Token is missing!")
    if is_system_call(token):
        return f(*args, **kwargs)
    logging.debug(f"Token: {token}")
    try:
        data = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        logging.debug("Expiration time: " + str(data["expiration"]))

        if not (token_is_valid(data["expiration"])):
            abort(401, "Token expired!")

        rst = requests.get(f"{dbm_url}/get_user/{data['user_type']}/{data['user_id']}", timeout=30, verify=False, 
                           headers=generate_session_token_system())
        current_user = rst.json()

        if current_user is None:
            abort(401, "Invalid Authentication token!")

        if not current_user["session_token"] == token:
            abort(401, "Token mismatch!")

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
        token = None
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

        try:
            data = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])

            if not (token_is_valid(data["expiration"])):
                abort(401, "Token expired!")
            logging.info(f"Data: {data}")
            # user_id = int(data["user_id"]) if not type(data["user_id"]) == int else data["user_id"]
            user_id = data["user_id"]
            logging.info(f"User id: {user_id}")
            rst = requests.get(f"{dbm_url}/get_user/ADMIN/{user_id}", timeout=30, verify=False, 
                               headers=generate_session_token_system())

            current_user = rst.json()
            logging.info(f"Response: {current_user}")
            logging.info(f"Response original: {rst}")

            if not rst.status_code == 200:
                abort(403, "Unauthorized access! Maybe")
            logging.info(f"Current user: {current_user}")

            if not current_user["session_token"] == token:
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
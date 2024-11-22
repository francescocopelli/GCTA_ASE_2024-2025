import logging
import os
from datetime import datetime, timedelta
from functools import wraps

import jwt
import requests
from flask import request, abort, jsonify, current_app

SECRET_KEY = os.environ.get('SECRET_KEY') or 'this is a secret'
logging.basicConfig(level=logging.DEBUG)

transaction_url = "http://transaction:5000"
user_url = "http://user_player:5000"
gacha_url = "http://gacha:5000"
dbm_url = "http://db-manager:5000"
admin_url = "http://user_admin:5000"
# mancano admin e player authentication

# make a function that take json data and return a response
def send_response(message, status_code):
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

        rst = requests.get(f"{dbm_url}/get_user/{data['user_type']}/{data['user_id']}",
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
            rst = requests.get(f"{dbm_url}/get_user/ADMIN/{user_id}",
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

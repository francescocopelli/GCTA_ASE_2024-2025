import logging
from datetime import datetime
from functools import wraps
import jwt
import requests
from flask import request, abort
from flask import current_app


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
    try:
        data = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        logging.debug("Expiration time: " + str(data["expiration"]))

        if not (token_is_valid(data["expiration"])):
            abort(401, "Token expired!")


        rst = requests.get(f"http://db-manager:5000/get_user/{data['user_type']}/{data['user_id']}")
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

        logging.info("Admin required check")
        token = None

        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
        if not token:
            logging.error("Token is missing")
            abort(401, "Authentication Token is missing!")
        try:
            data=jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])

            if not (token_is_valid(data["expiration"])):
                abort(401, "Token expired!")

            rst = requests.get(f"http://db-manager:5000/get_user/ADMIN/{data['user_id']}")
            current_user = rst

            logging.debug(f"Current user: {current_user}")

            if not current_user.status_code == 200:
                abort(403, "Unauthorized access!")
            current_user = current_user.json()
            if not current_user["session_token"] == token:
                abort(401, "Token mismatch!")

        except Exception as e:
            return {
                "message": "Something went wrong",
                "data": None,
                "error": str(e)
            }, 500

        return f(current_user, *args, **kwargs) if require_return else f(*args, **kwargs)

    @wraps(f)
    def decorated(*args, **kwargs):
        return admin_f(False, f, *args, **kwargs)

    return decorated
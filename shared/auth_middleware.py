import logging
from functools import wraps
import jwt
import requests
from flask import request, abort
from flask import current_app

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        logging.info("Token required checking")
        token = None
        logging.debug(f"Request headers: {request}")
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
        if not token:
            logging.error("Token is missing")
            abort(401, "Authentication Token is missing!")
        try:
            data=jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
            logging.debug(f"Token data: {data}")
            
            rst1 = requests.get(f"http://db-manager:5000/get_user/PLAYER/{data['user_id']}")
            rst2 = requests.get(f"http://db-manager:5000/get_user/ADMIN/{data['user_id']}")
            current_user = rst1.json() if rst1.json() is not None else rst2.json()
            
            if current_user is None:
                abort(401, "Invalid Authentication token!")
                
            # if not current_user["active"]:
            #     abort(403)
        except Exception as e:
            return {
                "message": "Something went wrong",
                "data": None,
                "error": str(e)
            }, 500

        return f(current_user, *args, **kwargs)

    return decorated

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
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
            logging.debug(f"Token data: {data}")

            rst1 = requests.get(f"http://db-manager:5000/get_user/PLAYER/{data['user_id']}")
            rst2 = requests.get(f"http://db-manager:5000/get_user/ADMIN/{data['user_id']}")
            current_user = rst1.json() if rst1.json() is not None else rst2.json()

            if current_user is None:
                abort(401, "Invalid Authentication token!")

            # if not current_user["active"]:
            #     abort(403)
        except Exception as e:
            return {
                "message": "Something went wrong",
                "data": None,
                "error": str(e)
            }, 500

        return f(*args, **kwargs)

    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        logging.info("Admin required check")
        token = None

        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
        if not token:
            logging.error("Token is missing")
            abort(401, "Authentication Token is missing!")
        try:
            data=jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])

            rst = requests.get(f"http://player:5000/get_user/ADMIN/{data['user_id']}")
            current_user = rst.json()

            if current_user is None:
                abort(401, "Invalid Authentication token!")

            if not current_user["admin"]:
                abort(403)

        except Exception as e:
            return {
                "message": "Something went wrong",
                "data": None,
                "error": str(e)
            }, 500

        return f(current_user, *args, **kwargs)

    return decorated
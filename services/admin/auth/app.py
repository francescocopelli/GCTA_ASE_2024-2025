from flask import Flask
import os
mockup = os.getenv("MOCKUP", "0") == "1"
gigio=None
if mockup:
    from auth_middleware import *
else:
    from shared.auth_middleware import *

app = Flask(__name__)

app.config['SECRET_KEY'] = SECRET_KEY

@app.route('/logout', methods=['DELETE'])
@admin_required
def logout():
    url = f"https://db-manager:5000/logout"
    if mockup:
        return gigio("logout", session_token=request.headers.get("Authorization"))
    response = requests.delete(url,  timeout=30, verify=False, headers=request.headers)
    return send_response(response.json(), response.status_code)


@app.route('/login', methods=['POST'])
def login():
    username = sanitize(request.json['username'])
    password = (request.json['password'])
    url = f"https://db-manager:5000/login/ADMIN"
    data = {
        "username": username,
        "password": password
    }
    if mockup:
        return gigio("login", username=username, password=password)
    response = requests.post(url,  timeout=30, verify=False, json=data)
    return send_response(response.json(), response.status_code)


@app.route('/register', methods=['POST'])
def register():
    logging.info(f"Registering new user {request}")
    username = sanitize(request.form.get('username'))
    password = (request.form.get('password'))
    email = request.form.get('email')
    url = f"https://db-manager:5000/register/ADMIN"
    data = {
        "username": username,
        "password": password,
        "email": email
    }
    if mockup:
        return gigio("register", username=username, password=password, email=email)
    response = requests.post(url,  timeout=30, verify=False, data=data)
    return send_response(response.json(), response.status_code)


# Esempio di utilizzo
if __name__ == '__main__':
    app.run()

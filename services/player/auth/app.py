import base64

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

dbm_url = "https://db-manager:5000"


@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']
    url = f"{dbm_url}/login/PLAYER"
    data = {
        "username": sanitize(username),
        "password": password
    }
    if mockup: return send_response(gigio("login", **data), 200)
    response = requests.post(url,  timeout=30, verify=False, json=data)
    return send_response(response.json(), response.status_code)


@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    image = request.files.get('image')
    if image:
        image = image.read()
    url = f"{dbm_url}/register/PLAYER"
    data = {
        "username": sanitize(username),
        "password": password,
        "email": email,
        "image": base64.b64encode(image).decode('utf-8') if image else None
    }
    if mockup: return send_response(gigio("register", **data), 200)
    response = requests.post(url,  timeout=30, verify=False, data=data)
    return send_response(response.json(), response.status_code)


@app.route('/logout', methods=['DELETE'])
@token_required_void
def logout():
    url = f"{dbm_url}/logout"

    if mockup: 
        #grab from the request header the token
        token = request.headers["Authorization"].split(" ")[1]
        return send_response(gigio("logout",session_token=token), 200)
    response = requests.delete(url,  timeout=30, verify=False, headers=request.headers)
    return send_response(response.json(), response.status_code)


# delete my account
@app.route('/delete', methods=['DELETE'])
@token_required_void
def delete():
    token = decode_session_token(request.headers["Authorization"].split(" ")[1])
    user_id = token['user_id']
    if token['user_type'] != "PLAYER":
        user_id = request.args.get('user_id')
    if mockup: return send_response(gigio("delete", user_id=user_id),200)
    url = f"{dbm_url}/delete/PLAYER"
    response = requests.delete(url+f'?user_id={user_id}', timeout=30, verify=False, headers=generate_session_token_system())
    return send_response(response.json(), response.status_code)

# Esempio di utilizzo
if __name__ == '__main__':
    app.run()

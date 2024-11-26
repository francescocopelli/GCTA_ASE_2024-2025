import base64

from flask import Flask

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
        "username": username,
        "password": password
    }
    response = requests.post(url,  timeout=10, json=data,verify=False)
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
        "username": username,
        "password": password,
        "email": email,
        "image": base64.b64encode(image).decode('utf-8') if image else None
    }
    response = requests.post(url,  timeout=10, data=data,verify=False)
    return send_response(response.json(), response.status_code)


@app.route('/logout', methods=['DELETE'])
@token_required_void
def logout():
    url = f"{dbm_url}/logout"
    response = requests.delete(url,  timeout=10, headers=request.headers,verify=False)
    return send_response(response.json(), response.status_code)


# delete my account
@app.route('/delete', methods=['DELETE'])
@token_required_void
def delete():
    url = f"{dbm_url}/delete/PLAYER"
    logging.debug("Session token: " + request.headers["Authorization"].split(" ")[1])
    session_token= (request.headers["Authorization"].split(" ")[1])
    response = requests.delete(url+f"{session_token}", timeout=10,verify=False)
    return send_response(response.json(), response.status_code)

# Esempio di utilizzo
if __name__ == '__main__':
    app.run()

from flask import Flask

from shared.auth_middleware import *

app = Flask(__name__)

print(SECRET_KEY)
app.config['SECRET_KEY'] = SECRET_KEY

@app.route('/logout', methods=['DELETE'])
@admin_required
def logout():
    url = f"https://db-manager:5000/logout"
    response = requests.delete(url,  timeout=3, headers=request.headers,verify=False)
    return send_response(response.json(), response.status_code)


@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']
    url = f"https://db-manager:5000/login/ADMIN"
    data = {
        "username": username,
        "password": password
    }
    response = requests.post(url,  timeout=3, json=data,verify=False)
    return send_response(response.json(), response.status_code)


@app.route('/register', methods=['POST'])
def register():
    logging.info(f"Registering new user {request}")
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    url = f"https://db-manager:5000/register/ADMIN"
    data = {
        "username": username,
        "password": password,
        "email": email
    }
    response = requests.post(url,  timeout=3, data=data,verify=False)
    return send_response(response.json(), response.status_code)


# Esempio di utilizzo
if __name__ == '__main__':
    app.run()

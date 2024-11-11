from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/gacha/roll', methods=['POST'])
def roll_gacha():
    # Codice per effettuare un roll di un gacha item
    pass

@app.route('/gacha/inventory/<user_id>', methods=['GET'])
def get_user_inventory(user_id):
    # Codice per recuperare l'inventario gacha di un utente
    pass

@app.route('/gacha/inventory', methods=['POST'])
def add_to_inventory():
    # Codice per aggiungere un gacha all'inventario di un utente
    pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)

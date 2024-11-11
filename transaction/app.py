from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/transaction/make_payment', methods=['POST'])
def make_payment():
    # Codice per effettuare un pagamento (ad esempio, acquisto di gacha)
    pass

@app.route('/transaction/auction_lock', methods=['POST'])
def auction_lock():
    # Codice per bloccare i fondi durante un’asta
    pass

@app.route('/transaction/auction_lock/<username>/<auction_id>', methods=['DELETE'])
def remove_auction_lock(username, auction_id):
    # Codice per rimuovere il blocco dei fondi di un’asta
    pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

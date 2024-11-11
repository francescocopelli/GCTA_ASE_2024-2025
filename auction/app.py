from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/auctions/all', methods=['GET'])
def get_all_auctions():
    # Codice per recuperare tutte le aste attive o scadute
    pass

@app.route('/auctions/add', methods=['POST'])
def add_auction():
    # Codice per aggiungere una nuova asta
    pass

@app.route('/auctions/end', methods=['POST'])
def end_auction():
    # Codice per terminare un'asta
    pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)

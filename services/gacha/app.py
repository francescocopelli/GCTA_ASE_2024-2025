from flask import Flask, request, jsonify, make_response
import sqlite3
import random
import base64

app = Flask(__name__)
DATABASE = './gacha.db/gacha.db'


# Helper function to connect to the database
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@app.post('/add')
def add():
    # Extract gacha item details from request JSON
    # data to be extracted are:
    # name, rarity, status, image (not required), description

    # the image should be transformed to be saved as blob type in the db

    # this is a multipart request, so we need to use request.files to extract the image

    name = request.form.get('name')
    rarity = request.form.get('rarity')
    status = request.form.get('status')
    description = request.form.get('description')

    image = request.files.get('image')

    # return jsonify({"message": list(request.form.keys()),"filino":list(request.files.keys())}),400

    image = request.files.get('image').read()

    if not image:
        return jsonify({'error': 'Missing image data'}), 408

    # Check for required fields
    if not all([name, rarity, status]):
        return jsonify({'error': 'Missing data to add gacha item'}), 400

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Add the gacha item to the database
    cursor.execute(
        "INSERT INTO GachaItems (name, rarity, status, image, description) VALUES (?, ?, ?, ?, ?)",
        (name, rarity, status, image, description)
    )

    conn.commit()
    conn.close()

    if cursor.lastrowid:
        return jsonify({'message': 'Gacha item added successfully'}), 201
    return jsonify({'error': 'Failed to add gacha item'}), 500


# Endpoint to perform a gacha roll for a random item
@app.route('/roll', methods=['POST'])
def roll_gacha():
    # Extract roll details from request JSON
    data = request.get_json()
    username = data.get('username')
    roll_cost = data.get('roll_cost')

    # Check for required fields
    if not all([username, roll_cost]):
        return jsonify({'error': 'Missing data for gacha roll'}), 400

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the user has sufficient funds for the roll
    cursor.execute("SELECT currency_balance FROM PLAYER WHERE username = ?", (username,))
    user = cursor.fetchone()

    if user and user['currency_balance'] >= roll_cost:
        # Deduct the roll cost from user's balance
        new_balance = user['currency_balance'] - roll_cost
        cursor.execute("UPDATE PLAYER SET currency_balance = ? WHERE username = ?", (new_balance, username))

        # Perform the gacha roll by selecting a random item based on rarity
        cursor.execute("SELECT * FROM GachaItems WHERE status = 'available'")
        items = cursor.fetchall()

        if not items:
            conn.close()
            return jsonify({'error': 'No available gacha items'}), 404

        # Select a random item
        gacha_item = random.choice(items)
        conn.commit()
        conn.close()

        return jsonify({
            'message': 'Gacha roll successful',
            'gacha_id': gacha_item['gacha_id'],
            'name': gacha_item['name'],
            'rarity': gacha_item['rarity'],
            'new_balance': new_balance
        }), 200
    else:
        conn.close()
        return jsonify({'error': 'Insufficient funds for gacha roll'}), 403


# Endpoint to retrieve a user's gacha inventory
@app.route('/inventory/<user_id>', methods=['GET'])
def get_user_inventory(user_id):
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Retrieve all gacha items owned by the user
    cursor.execute("""
        SELECT GachaItems.gacha_id, GachaItems.name, GachaItems.rarity
        FROM UserGachaInventory
        JOIN GachaItems ON UserGachaInventory.gacha_id = GachaItems.gacha_id
        WHERE UserGachaInventory.user_id = ?
    """, (user_id,))

    inventory = cursor.fetchall()
    conn.close()

    # If inventory is empty, return 404
    if not inventory:
        return jsonify({'error': 'No gacha items found for user'}), 404

    # Format inventory for JSON response
    inventory_list = [dict(item) for item in inventory]
    return jsonify({'inventory': inventory_list}), 200


# Endpoint to add a gacha item to a user's inventory
@app.route('/inventory', methods=['POST'])
def add_to_inventory():
    # Extract inventory details from request JSON
    data = request.get_json()
    username = data.get('username')
    gacha_id = data.get('gacha_id')

    # Check for required fields
    if not all([username, gacha_id]):
        return jsonify({'error': 'Missing data to add to inventory'}), 400

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Retrieve the user_id from the username
    cursor.execute("SELECT user_id FROM PLAYER WHERE username = ?", (username,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return jsonify({'error': 'User not found'}), 404

    user_id = user['user_id']

    # Check if the gacha item exists and is available
    cursor.execute("SELECT * FROM GachaItems WHERE gacha_id = ? AND status = 'available'", (gacha_id,))
    gacha_item = cursor.fetchone()

    if not gacha_item:
        conn.close()
        return jsonify({'error': 'Gacha item not found or not available'}), 404

    # Add gacha item to user's inventory
    cursor.execute(
        "INSERT INTO UserGachaInventory (user_id, gacha_id, acquired_date) VALUES (?, ?, datetime('now'))",
        (user_id, gacha_id)
    )
    conn.commit()
    conn.close()

    return jsonify({'message': "Gacha item successfully added to user's inventory"}), 201


@app.get("/all")
def get_all():
    conn = get_db_connection()
    cursor = conn.cursor()



    cursor.execute("SELECT * FROM GachaItems")
    rows = cursor.fetchall()

    conn.close()

    if not rows:
        return jsonify({'error': 'No gacha items found'}), 404

    items = []
    for x in rows:
        items.append({
            "gacha_id": x['gacha_id'],
            "name": x['name'],
            "rarity": x['rarity'],
            "status": x['status'],
            "description": x['description'],
            "image": base64.b64encode(x['image']).decode('utf-8') if x['image'] else None
        })

    return jsonify({"message":items}), 202

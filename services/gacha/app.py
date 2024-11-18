import logging
import os

import requests
from flask import Flask, request, jsonify
import sqlite3
import random
import base64
from shared.auth_middleware import *

app = Flask(__name__)
SECRET_KEY = os.environ.get('SECRET_KEY') or 'this is a secret'
print(SECRET_KEY)
app.config['SECRET_KEY'] = SECRET_KEY
DATABASE = './gacha.db/gacha.db'
logging.basicConfig(level=logging.DEBUG)


# Helper function to connect to the database
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@app.post('/add')
@admin_required
def add():
    name = request.form.get('name')
    rarity = request.form.get('rarity')
    status = request.form.get('status')
    description = request.form.get('description')
    image = request.files.get('image')
    if image:
        image = image.read()

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
@app.route('/inventory/<user_id>', methods=['GET'])
@admin_required
def get_user_inventory(user_id):
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Retrieve all gacha items owned by the user
    cursor.execute("""
        SELECT GachaItems.*, UserGachaInventory.acquired_date, UserGachaInventory.locked
        FROM UserGachaInventory
        JOIN GachaItems ON UserGachaInventory.gacha_id = GachaItems.gacha_id
        WHERE UserGachaInventory.user_id = ?
    """, (user_id,))

    inventory = cursor.fetchall()
    conn.close()

    # If inventory is empty, return 404
    if not inventory:
        return jsonify({'error': 'No gacha items found for user'}), 400

    # Format inventory for JSON response
    inventory_list = []
    for x in inventory:
        inventory_list.append({
            "gacha_id": x['gacha_id'],
            "name": x['name'],
            "rarity": x['rarity'],
            "status": x['status'],
            "description": x['description'],
            "acquired_date": x['acquired_date'],
            "locked": x['status'] == 'locked',
            "image": base64.b64encode(x['image']).decode('utf-8') if x['image'] else None
        })

    return jsonify({'inventory': inventory_list}), 200


@app.route('/roll', methods=['POST'])
@token_required
def roll_gacha():
    # Extract roll details from request JSON
    data = request.get_json()
    user_id = data.get('user_id')
    roll_cost = 5

    # Check for required fields
    if not all([user_id, roll_cost]):
        return jsonify({'error': 'Missing data for gacha roll'}), 400

    if type(roll_cost) != int:
        roll_cost = int(roll_cost)

    if roll_cost <= 0:
        return jsonify({'error': 'Invalid roll cost'}), 400

    # Check if the user has sufficient funds for the roll
    # ask user service for user balance
    user = requests.get('http://user_player:5000/get_user/' + str(user_id))
    if user.status_code != 200:
        return jsonify({'error': 'User not found'}), 408
    user = user.json()
    if user and user['currency_balance'] <= roll_cost:
        return jsonify({'error': 'Insufficient funds for gacha roll'}), 403

    # Update the user's currency balance to user service
    response = requests.put('http://user_player:5000/update_balance/PLAYER',
                            json={'user_id': user_id, 'amount': roll_cost, 'type': 'roll_purchase'})

    if response.status_code != 200:
        return jsonify({'error': 'Failed to update user balance'}), 500
    else:
        # add transaction to db
        data = {'user_id': user_id, 'amount': roll_cost, 'type': 'roll_purchase'}
        response = requests.post('http://transaction:5000/add_transaction', json=data)
        if response.status_code != 200:
            requests.put('http://user_player:5000/update_balance/PLAYER',
                         json={'user_id': user_id, 'new_balance': user['currency_balance']})
            return jsonify({'error': 'Failed to add transaction'}), 500

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Perform the gacha roll by selecting a random item based on rarity
    cursor.execute("SELECT * FROM GachaItems WHERE status = 'available'")
    items = cursor.fetchall()

    if not items:
        conn.close()
        return jsonify({'error': 'No available gacha items'}), 408

    # Select a random item
    gacha_item = random.choice(items)
    conn.commit()
    conn.close()

    if not gacha_item:
        return jsonify({'error': 'Failed to perform gacha roll'}), 500

    # Add the gacha item to the user's inventory
    response = requests.post('http://gacha:5000/inventory/add',
                             json={'user_id': user_id, 'gacha_id': gacha_item['gacha_id']})
    if response.status_code != 200:
        return jsonify({'error': 'Failed to add gacha item to inventory'}), 500

    return jsonify({
        'message': 'Gacha roll successful',
        'gacha_id': gacha_item['gacha_id'],
        'name': gacha_item['name'],
        'rarity': gacha_item['rarity'],
    }), 200
# Endpoint to retrieve a user's gacha inventory


# Endpoint to add a gacha item to a user's inventory
@app.route('/inventory/add', methods=['POST'])
@admin_required
def add_to_inventory():
    # Extract inventory details from request JSON
    data = request.get_json()
    user_id = data.get('user_id')
    gacha_id = data.get('gacha_id')

    # Check for required fields
    if not all([user_id, gacha_id]):
        return jsonify({'error': 'Missing data to add gacha to inventory'}), 400

    user = requests.get('http://user_player:5000/get_user/' + user_id)

    if user.status_code != 200:
        return jsonify({'error': 'User not found'}), 408

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Add gacha item to user's inventory if it exists and is available
    cursor.execute("""
        INSERT INTO UserGachaInventory (user_id, gacha_id, acquired_date)
        SELECT ?, gacha_id, datetime('now')
        FROM GachaItems
        WHERE gacha_id = ? AND status = 'available'
    """, (user_id, gacha_id))

    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'error': 'Gacha item not found or not available'}), 408

    conn.commit()
    conn.close()
    return jsonify({'message': "Gacha item successfully added to user's inventory"}), 200


@app.get("/all")
@token_required
def get_all():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM GachaItems LIMIT 10")
    rows = cursor.fetchall()

    conn.close()

    if not rows:
        return jsonify({'error': 'No gacha items found'}), 408

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

    return jsonify({"message": items}), 202


# update gacha item
@app.route('/update', methods=['PUT'])
@admin_required
def update_gacha_item():
    # Extract gacha item details from request JSON
    gacha_id = request.form.get('gacha_id')
    name = request.form.get('name')
    rarity = request.form.get('rarity')
    status = request.form.get('status')
    description = request.form.get('description')
    image = request.files.get('image')

    # Check for required fields
    if not all([gacha_id, name, rarity, status]):
        return jsonify({'error': 'Missing data to update gacha item'}), 400

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the gacha item exists
    cursor.execute("SELECT * FROM GachaItems WHERE gacha_id = ?", (gacha_id,))
    gacha_item = cursor.fetchone()

    if not description:
        description = gacha_item['description']
    if image:
        image = image.read()

    if not gacha_item:
        conn.close()
        return jsonify({'error': 'Gacha item not found'}), 408

    # Update the gacha item details
    if image:
        cursor.execute(
            "UPDATE GachaItems SET name = ?, rarity = ?, status = ?, image = ?, description = ? WHERE gacha_id = ?",
            (name, rarity, status, image, description, gacha_id)
        )
    else:
        cursor.execute(
            "UPDATE GachaItems SET name = ?, rarity = ?, status = ?, description = ? WHERE gacha_id = ?",
            (name, rarity, status, description, gacha_id)
        )
    conn.commit()
    conn.close()

    if cursor.rowcount:
        return jsonify({'message': 'Gacha item updated successfully'}), 200
    return jsonify({'error': 'Failed to update gacha item'}), 500


# retrieve information about a specific gacha item
@app.route('/get/<gacha_id>')
@token_required
def get_gacha_item(gacha_id):
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Retrieve the gacha item details
    cursor.execute("SELECT * FROM GachaItems WHERE gacha_id = ?", (gacha_id,))
    gacha_item = cursor.fetchone()
    conn.close()

    logging.debug("Gacha item: %s", gacha_item)

    if not gacha_item:
        return jsonify({'error': 'Gacha item not found'}), 408

    return jsonify({
        'gacha_id': gacha_item['gacha_id'],
        'name': gacha_item['name'],
        'rarity': gacha_item['rarity'],
        'status': gacha_item['status'],
        'description': gacha_item['description'],
        'image': base64.b64encode(gacha_item['image']).decode('utf-8') if gacha_item['image'] else None
    }), 200


# get detail of a specific gacha of a specific user
@app.get('/get/<user_id>/<gacha_id>')
@token_required
def get_user_gacha_item(user_id, gacha_id):
    res = requests.get('http://user_player:5000/get_user/' + user_id)
    if res.status_code != 200:
        return jsonify({'error': 'User not found'}), 408

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Retrieve the user's gacha item details
    cursor.execute("""
        SELECT GachaItems.*, UserGachaInventory.acquired_date, UserGachaInventory.locked
        FROM UserGachaInventory
        JOIN GachaItems ON UserGachaInventory.gacha_id = GachaItems.gacha_id
        WHERE UserGachaInventory.user_id = ? AND UserGachaInventory.gacha_id = ?
    """, (user_id, gacha_id))
    gacha_item = cursor.fetchone()
    conn.close()

    if not gacha_item:
        return jsonify({'error': 'Gacha item not found in user inventory'}), 408

    return jsonify({
        'gacha_id': gacha_item['gacha_id'],
        'name': gacha_item['name'],
        'rarity': gacha_item['rarity'],
        'status': gacha_item['status'],
        'description': gacha_item['description'],
        'acquired_date': gacha_item['acquired_date'],
        'locked': gacha_item['status'] == 'locked',
        'image': base64.b64encode(gacha_item['image']).decode('utf-8') if gacha_item['image'] else None
    }), 200


@app.get('/is_gacha_unlocked/<user_id>/<gacha_id>')
@admin_required
def is_gacha_unlocked(user_id, gacha_id):
    if not all([user_id, gacha_id]):
        return jsonify({'error': 'Missing data to check gacha item'}), 400
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the gacha item is unlocked for the user
    cursor.execute("""
        SELECT * FROM UserGachaInventory
        WHERE user_id = ? AND gacha_id = ? AND locked = 'unlocked'
    """, (user_id, gacha_id))
    gacha_item = cursor.fetchone()
    conn.close()

    if not gacha_item:
        return jsonify({'message': 'Gacha item is locked'}), 403

    return jsonify({'message': 'Gacha item is unlocked'}), 200

@app.route("/update_gacha_status", methods=['PUT'])
@admin_required
def update_gacha_status():
    user_id = request.json['user_id']
    gacha_id = request.json['gacha_id']
    status = request.json['status']

    if not all ([user_id, gacha_id, status]):
        return jsonify({'error': 'Missing data to update gacha status'}), 400

    res = requests.get('http://user_player:5000/get_user/' + user_id)
    if res.status_code != 200:
        return jsonify({'error': 'User not found'}), 409

    res = requests.get('http://gacha:5000/get/' + gacha_id)
    if res.status_code != 200:
        return jsonify({'error': 'Gacha item not found'}), 408

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE UserGachaInventory SET locked = ? WHERE user_id = ? AND gacha_id = ?", (status, user_id, gacha_id))

    conn.commit()
    conn.close()
    if cursor.rowcount:
        return jsonify({'message': 'Gacha status updated successfully'}), 200
    return jsonify({'error': 'Failed to update gacha status'}), 500


@app.route('/update_gacha_owner', methods=['PUT'])
@admin_required
def update_gacha_owner():
    buyer_id = request.json['buyer_id']
    seller_id = request.json['seller_id']
    gacha_id = request.json['gacha_id']
    # need to unlock the gacha
    status = request.json['status']

    if not all([buyer_id, seller_id, gacha_id, status]):
        return jsonify({'error': 'Missing data to update gacha owner'}), 400

    res = requests.get(f'http://user_player:5000/get_user/{buyer_id}')
    if res.status_code != 200:
        return jsonify({'error': 'Buyer not found'}), 408
    logging.debug("Buyer found")

    res = requests.get(f'http://gacha:5000/get/{seller_id}/{gacha_id}')
    if res.status_code != 200:
        return jsonify({'error': 'Gacha item not found'}), 408

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""UPDATE UserGachaInventory SET locked = ?, user_id=?
                   WHERE user_id = ? AND gacha_id = ?""", (status, buyer_id, seller_id, gacha_id))

    conn.commit()
    conn.close()

    if cursor.rowcount:
        return jsonify({'message': 'Gacha owner updated successfully'}), 200
    return jsonify({'error': 'Failed to update gacha owner'}), 502
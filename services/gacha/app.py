import base64
import sqlite3

from flask import Flask

from shared.auth_middleware import *

app = Flask(__name__)

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
    # if not check_header(): return send_response({'error': 'Admin authorization required'}, 401)

    name = request.form.get('name')
    rarity = request.form.get('rarity')
    status = request.form.get('status')
    description = request.form.get('description')
    image = request.files.get('image')
    if image:
        image = image.read()

    # Check for required fields
    if not all([name, rarity, status]):
        logging.debug("Missing data to add gacha item: name=%s, rarity=%s, status=%s", name, rarity, status)
        return send_response({'error': 'Missing data to add gacha item'}, 400)

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Add the gacha item to the database
        cursor.execute(
            "INSERT INTO GachaItems (name, rarity, status, image, description) VALUES (?, ?, ?, ?, ?)",
            (name, rarity, status, image, description)
        )
        conn.commit()
        if cursor.lastrowid:
            logging.debug("Gacha item added successfully with id=%s", cursor.lastrowid)
            return send_response({'message': 'Gacha item added successfully', 'gacha_id': cursor.lastrowid}, 201)
        else:
            logging.error("Failed to add gacha item: lastrowid is None")
            return send_response({'error': 'Failed to add gacha item'}, 500)
    except sqlite3.Error as e:
        logging.error("Database error: %s", e)
        return send_response({'error': 'Database error'}, 500)
    finally:
        conn.close()


# Endpoint to retrieve a user's gacha inventory
@app.route('/inventory/<user_id>', methods=['GET'])
@token_required_void
def get_user_inventory(user_id):
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Retrieve all gacha items owned by the user
    cursor.execute("""
        SELECT GachaItems.gacha_id, GachaItems.name, GachaItems.rarity, GachaItems.status, GachaItems.description,
        UserGachaInventory.acquired_date, UserGachaInventory.locked
        FROM UserGachaInventory
        JOIN GachaItems ON UserGachaInventory.gacha_id = GachaItems.gacha_id
        WHERE UserGachaInventory.user_id = ?
    """, (user_id,))

    inventory = cursor.fetchall()
    conn.close()

    # If inventory is empty, return 404
    if not inventory:
        logging.debug("No gacha items found for user_id=%s", user_id)
        return send_response({'error': 'No gacha items found for user'}, 404)

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
            # "image": base64.b64encode(x['image']).decode('utf-8') if x['image'] else None
        })

    logging.debug("User inventory retrieved successfully for user_id=%s", user_id)
    return send_response({'inventory': inventory_list}, 200)


@app.route('/roll', methods=['POST'])
@login_required_ret
def roll_gacha(user):
    # Extract roll details from request JSON
    user_id = user['user_id']
    roll_cost = 5

    if check_header() or jwt.decode(request.headers.get("Authorization").split(" ")[1], app.config['SECRET_KEY'],
                                    algorithms=["HS256"])['user_type'] == 'ADMIN':
        return send_response({'error': 'Admins cannot roll gacha'}, 403)

    # Check for required fields
    if not all([user_id, roll_cost]):
        logging.debug("Missing data for gacha roll: user_id=%s, roll_cost=%s", user_id, roll_cost)
        return send_response({'error': 'Missing data for gacha roll'}, 400)

    # Check if the user has sufficient funds for the roll
    if user['currency_balance'] < roll_cost:
        logging.debug("Insufficient funds for gacha roll: user_id=%s, balance=%s, roll_cost=%s", user_id,
                      user['currency_balance'], roll_cost)
        return send_response({'error': 'Insufficient funds for gacha roll'}, 403)

    # Update the user's currency balance
    response = requests.put('https://user_player:5000/update_balance/PLAYER',  timeout=10, headers=generate_session_token_system(),
                            json={'user_id': user_id, 'amount': roll_cost, 'type': 'roll_purchase'},verify=False)

    if response.status_code != 200:
        logging.debug("Failed to update user balance: user_id=%s, roll_cost=%s", user_id, roll_cost)
        return send_response({'error': 'Failed to update user balance'}, 500)

    # Add transaction to db
    data = {'user_id': user_id, 'amount': roll_cost, 'type': 'roll_purchase'}
    response = requests.post('https://transaction:5000/add_transaction', json=data, timeout=10, 
                             headers=generate_session_token_system(),verify=False)
    if response.status_code != 200:
        logging.debug("Failed to add transaction: user_id=%s, roll_cost=%s", user_id, roll_cost)
        return send_response({'error': 'Failed to add transaction'}, 500)

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Perform the gacha roll by selecting a random item based on rarity
    cursor.execute("SELECT * FROM GachaItems WHERE status = 'available' ORDER BY RANDOM() LIMIT 1")
    gacha_item = cursor.fetchone()

    # Select a random item
    conn.commit()
    conn.close()

    if not gacha_item:
        logging.debug("Failed to perform gacha roll")
        return send_response({'error': 'Failed to perform gacha roll'}, 500)

    # Add the gacha item to the user's inventory
    response = requests.post('https://gacha:5000/inventory/add', headers=generate_session_token_system(), timeout=10, 
                             json={'user_id': user_id, 'gacha_id': gacha_item['gacha_id']},verify=False)
    if response.status_code != 201:
        logging.debug("Failed to add gacha item to inventory: user_id=%s, gacha_id=%s", user_id, gacha_item['gacha_id'])
        return send_response({'error': 'Failed to add gacha item to inventory'}, 500)

    logging.debug("Gacha roll successful: user_id=%s, gacha_id=%s, name=%s, rarity=%s", user_id, gacha_item['gacha_id'],
                  gacha_item['name'], gacha_item['rarity'])
    return send_response({
        'message': 'Gacha roll successful',
        'gacha_id': gacha_item['gacha_id'],
        'name': gacha_item['name'],
        'rarity': gacha_item['rarity'],
    }, 200)


# Endpoint to add a gacha item to a user's inventory
@app.route('/inventory/add', methods=['POST'])
@admin_required
def add_to_inventory():
    # Extract inventory details from request JSON
    data = request.get_json()
    user_id = str(data.get('user_id'))
    gacha_id = data.get('gacha_id')

    # Check for required fields
    if not all([user_id, gacha_id]):
        logging.debug("Missing data to add gacha to inventory: user_id=%s, gacha_id=%s", user_id, gacha_id)
        return send_response({'error': 'Missing data to add gacha to inventory'}, 400)

    user = requests.get('https://user_player:5000/get_user/' + user_id, timeout=10,  headers=generate_session_token_system(),verify=False)

    if user.status_code != 200:
        logging.debug("User not found: user_id=%s", user_id)
        return send_response({'error': 'User not found'}, 404)

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
        logging.debug("Gacha item not found or not available: gacha_id=%s", gacha_id)
        return send_response({'error': 'Gacha item not found or not available'}, 404)

    conn.commit()
    conn.close()
    logging.debug("Gacha item successfully added to user's inventory: user_id=%s, gacha_id=%s", user_id, gacha_id)
    return send_response({'message': "Gacha item successfully added to user's inventory"}, 201)


@app.get("/all")
def get_all():
    conn = get_db_connection()
    cursor = conn.cursor()

    # write another execute cursor to get all the gacha items with an arbitrary offset limit taken from request if present otherwise use a default one
    cursor.execute("SELECT * FROM GachaItems LIMIT 10 OFFSET ?", (request.args.get('offset') or 0,))
    rows = cursor.fetchall()

    conn.close()

    if not rows:
        logging.debug("No gacha items found")
        return send_response({'error': 'No gacha items found'}, 404)

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

    logging.debug("Gacha items retrieved successfully")
    return send_response({"message": items}, 200)


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
        logging.debug("Missing data to update gacha item: gacha_id=%s, name=%s, rarity=%s, status=%s", gacha_id, name,
                      rarity, status)
        return send_response({'error': 'Missing data to update gacha item'}, 400)

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the gacha item exists
    cursor.execute("SELECT * FROM GachaItems WHERE gacha_id = ?", (gacha_id,))
    gacha_item = cursor.fetchone()

    if not gacha_item:
        conn.close()
        logging.debug("Gacha item not found: gacha_id=%s", gacha_id)
        return send_response({'error': 'Gacha item not found'}, 404)

    if not description:
        description = gacha_item['description']
    if image:
        image = image.read()
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
        logging.debug("Gacha item updated successfully: gacha_id=%s", gacha_id)
        return send_response({'message': 'Gacha item updated successfully'}, 200)
    logging.debug("Failed to update gacha item: gacha_id=%s", gacha_id)
    return send_response({'error': 'Failed to update gacha item'}, 500)


# retrieve information about a specific gacha item
@app.route('/get/<gacha_id>')
def get_gacha_item(gacha_id):
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Retrieve the gacha item details
    cursor.execute("SELECT * FROM GachaItems WHERE gacha_id = ?", (gacha_id,))
    gacha_item = cursor.fetchone()
    conn.close()

    if not gacha_item:
        logging.debug("Gacha item not found: gacha_id=%s", gacha_id)
        return send_response({'error': 'Gacha item not found'}, 404)

    logging.debug("Gacha item retrieved successfully: gacha_id=%s", gacha_id)
    return send_response({
        'gacha_id': gacha_item['gacha_id'],
        'name': gacha_item['name'],
        'rarity': gacha_item['rarity'],
        'status': gacha_item['status'],
        'description': gacha_item['description'],
        'image': base64.b64encode(gacha_item['image']).decode('utf-8') if gacha_item['image'] else None
    }, 200)


# get detail of a specific gacha of a specific user
@app.get('/get/<user_id>/<gacha_id>')
@token_required_void
def get_user_gacha_item(user_id, gacha_id):
    logging.debug("User ID: %s", user_id)
    logging.debug("JWT Dec User ID: %s", jwt.decode(request.headers.get("Authorization").split(" ")[1], app.config['SECRET_KEY'],
                                                    algorithms=["HS256"])['user_id'])
    if jwt.decode(request.headers.get("Authorization").split(" ")[1], app.config['SECRET_KEY'],
                  algorithms=["HS256"])['user_type'] == 'PLAYER' and str(jwt.decode(
        request.headers.get("Authorization").split(" ")[1], app.config['SECRET_KEY'], algorithms=["HS256"])['user_id']) != str(user_id):
        return send_response({'error': 'You are not authorized to view this page'}, 403)
    res = requests.get('https://user_player:5000/get_user/' + str(user_id),  timeout=10, headers=generate_session_token_system(),verify=False)
    if res.status_code != 200:
        logging.debug("User not found: user_id=%s", user_id)
        return send_response({'error': 'User not found'}, 404)

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
        logging.debug("Gacha item not found in user inventory: user_id=%s, gacha_id=%s", user_id, gacha_id)
        return send_response({'error': 'Gacha item not found in user inventory'}, 404)

    logging.debug("Gacha item retrieved successfully: user_id=%s, gacha_id=%s", user_id, gacha_id)
    return send_response({
        'gacha_id': gacha_item['gacha_id'],
        'name': gacha_item['name'],
        'rarity': gacha_item['rarity'],
        'status': gacha_item['status'],
        'description': gacha_item['description'],
        'acquired_date': gacha_item['acquired_date'],
        'locked': gacha_item['status'] == 'locked',
        'image': base64.b64encode(gacha_item['image']).decode('utf-8') if gacha_item['image'] else None
    }, 200)


@app.get('/is_gacha_unlocked/<user_id>/<gacha_id>')
@admin_required
def is_gacha_unlocked(user_id, gacha_id):
    if not all([user_id, gacha_id]):
        logging.debug("Missing data to check gacha item: user_id=%s, gacha_id=%s", user_id, gacha_id)
        return send_response({'error': 'Missing data to check gacha item'}, 400)

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
        logging.debug("Gacha item is locked: user_id=%s, gacha_id=%s", user_id, gacha_id)
        return send_response({'message': 'Gacha item is locked'}, 403)

    logging.debug("Gacha item is unlocked: user_id=%s, gacha_id=%s", user_id, gacha_id)
    return send_response({'message': 'Gacha item is unlocked'}, 200)

# Hidden from the API documentation
@app.route("/update_gacha_status", methods=['PUT'])
@admin_required
def update_gacha_status():
    user_id = str(request.json['user_id'])
    gacha_id = str(request.json['gacha_id'])
    status = request.json['status']

    if not all([user_id, gacha_id, status]):
        logging.debug("Missing data to update gacha status: user_id=%s, gacha_id=%s, status=%s", user_id, gacha_id,
                      status)
        return send_response({'error': 'Missing data to update gacha status'}, 400)

    res = requests.get('https://user_player:5000/get_user/' + user_id,  timeout=10, headers=request.headers,verify=False)
    if res.status_code != 200:
        logging.debug("User not found: user_id=%s", user_id)
        return send_response({'error': 'User not found'}, 409)

    res = requests.get('https://gacha:5000/get/' + gacha_id,  timeout=10, headers=request.headers,verify=False)
    if res.status_code != 200:
        logging.debug("Gacha item not found: gacha_id=%s", gacha_id)
        return send_response({'error': 'Gacha item not found'}, 408)

    conn = get_db_connection()
    cursor = conn.cursor()

    # cursor.execute("UPDATE UserGachaInventory SET locked = ? WHERE user_id = ? AND gacha_id = ? LIMIT 1",
    #                (status, user_id, gacha_id))
    not_status = "unlocked" if status == "locked" else "locked"

    cursor.execute(
        "UPDATE UserGachaInventory SET locked = ? WHERE user_id = ? AND gacha_id = ? AND locked= ? AND inventory_id = (SELECT inventory_id FROM UserGachaInventory WHERE user_id = ? AND gacha_id = ? AND locked=? ORDER BY RANDOM() LIMIT 1)",
        (status, user_id, gacha_id, not_status, user_id, gacha_id, not_status))

    conn.commit()
    conn.close()
    if cursor.rowcount:
        logging.debug("Gacha status updated successfully: user_id=%s, gacha_id=%s, status=%s", user_id, gacha_id,
                      status)
        return send_response({'message': 'Gacha status updated successfully'}, 200)
    logging.debug("Failed to update gacha status: user_id=%s, gacha_id=%s, status=%s", user_id, gacha_id, status)
    return send_response({'error': 'Failed to update gacha status'}, 500)


# Hidden from the API documentation
@app.route('/update_gacha_owner', methods=['PUT'])
@admin_required
def update_gacha_owner():
    buyer_id = request.json['buyer_id']
    seller_id = request.json['seller_id']
    gacha_id = request.json['gacha_id']
    status = request.json['status']

    if not all([buyer_id, seller_id, gacha_id, status]):
        logging.debug("Missing data to update gacha owner: buyer_id=%s, seller_id=%s, gacha_id=%s, status=%s", buyer_id,
                      seller_id, gacha_id, status)
        return send_response({'error': 'Missing data to update gacha owner'}, 400)

    res = requests.get(f'https://user_player:5000/get_user/{buyer_id}', timeout=10,  headers=request.headers,verify=False)
    if res.status_code != 200:
        logging.debug("Buyer not found: buyer_id=%s", buyer_id)
        return send_response({'error': 'Buyer not found'}, 404)
    logging.debug("Buyer found: buyer_id=%s", buyer_id)

    res = requests.get(f'https://gacha:5000/get/{seller_id}/{gacha_id}',  timeout=10, headers=request.headers,verify=False)
    if res.status_code != 200:
        logging.debug("Gacha item not found: seller_id=%s, gacha_id=%s", seller_id, gacha_id)
        return send_response({'error': 'Gacha item not found'}, 404)
    logging.debug("Gacha item found: seller_id=%s, gacha_id=%s", seller_id, gacha_id)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""UPDATE UserGachaInventory SET locked = ?, user_id=? 
                        WHERE user_id = ? AND gacha_id = ?""", (status, buyer_id, seller_id, gacha_id))

    conn.commit()
    conn.close()

    if cursor.rowcount:
        logging.debug("Gacha owner updated successfully: buyer_id=%s, seller_id=%s, gacha_id=%s, status=%s", buyer_id,
                      seller_id, gacha_id, status)
        return send_response({'message': 'Gacha owner updated successfully'}, 200)
    logging.debug("Failed to update gacha owner: buyer_id=%s, seller_id=%s, gacha_id=%s, status=%s", buyer_id,
                  seller_id, gacha_id, status)
    return send_response({'error': 'Failed to update gacha owner'}, 500)

def exist_auction(gacha_id):
    req = requests.get('https://auction:5000/get_gacha_auctions?gacha_id=' + gacha_id,  timeout=10, headers=generate_session_token_system(),verify=False)
    return req.status_code == 200

@app.route('/delete/<gacha_id>', methods=['DELETE'])
@admin_required
def delete_gacha_item(gacha_id):
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the gacha item exists
    cursor.execute("SELECT * FROM GachaItems WHERE gacha_id = ?", (gacha_id,))
    gacha_item = cursor.fetchone()

    if not gacha_item:
        conn.close()
        logging.debug("Gacha item not found: gacha_id=%s", gacha_id)
        return send_response({'error': 'Gacha item not found'}, 404)

    cursor.execute("SELECT * FROM UserGachaInventory WHERE gacha_id = ?", (gacha_id,))
    cursor.fetchall()
    one_is_locked = False
    for x in cursor.fetchall():
        if x['locked'] == 'locked':
            one_is_locked = True
            break
    if cursor.rowcount and one_is_locked:
        # get the highest bid from auction table
        req = requests.get('https://auction:5000/highest_bid?gacha_id=' + gacha_id, timeout=10, 
                           headers=generate_session_token_system(),verify=False)
        if req.status_code != 200 and exist_auction(gacha_id):
            return send_response({'error': 'Failed to get highest bid'}, 500)
        bid = req.json()['highest_bid']
        user_id = req.json()['buyer_id']
        # undo the auction
        response = requests.put(f"https://user_player:5000/update_balance/PLAYER",
                                headers=generate_session_token_system(), timeout=10, 
                                json={"user_id": user_id, "amount": bid, "type": "credit"},verify=False)
        if response.status_code != 200:
            return send_response({"error": "Failed to update balance"}, 500)
        cursor.execute("UPDATE UserGachaInventory SET locked='unlocked' WHERE gacha_id = ?", (gacha_id,))

    req = requests.delete('https://auction:5000/delete?gacha_id=' + gacha_id,  timeout=10, headers=generate_session_token_system(),verify=False)
    if req.status_code != 200 and exist_auction(gacha_id):
        return send_response({'error': 'Failed to delete auction'}, 500)

    # Delete the gacha item
    cursor.execute("DELETE FROM UserGachaInventory WHERE gacha_id = ?", (gacha_id,))
    cursor.execute("DELETE FROM GachaItems WHERE gacha_id = ?", (gacha_id,))
    conn.commit()
    conn.close()

    if cursor.rowcount:
        logging.debug("Gacha item deleted successfully: gacha_id=%s", gacha_id)
        return send_response({'message': 'Gacha item deleted successfully'}, 200)
    logging.debug("Failed to delete gacha item: gacha_id=%s", gacha_id)
    return send_response({'error': 'Failed to delete gacha item'}, 500)

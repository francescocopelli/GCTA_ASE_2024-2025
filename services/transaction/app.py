import uuid
import os
from flask import Flask

# Use MOCKUP flag to toggle between mock and real implementations
mockup = os.getenv("MOCKUP", "0") == "1"

if mockup:
    from auth_middleware import *
else:
    from shared.auth_middleware import *

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Placeholder for mock implementation
gigio = None

app.config['SECRET_KEY'] = SECRET_KEY

DATABASE = "transactions"
DB_HOST = "transactions_db"

@app.route("/add_transaction", methods=["POST"])
@admin_required
def add_transaction():
    """
    Add a new transaction to the database.

    This endpoint handles POST requests to add a new transaction. The transaction type is derived based on the service
    path in the request URL. The transaction details are then inserted into the Transactions table in the database.

    Returns:
        Response: JSON response with a success message and HTTP status code 200.

    Request Body (JSON):
        user_id (str): The ID of the user making the transaction.
        type (str): The type of the transaction (only used if the path contains "auction").
        amount (float): The amount of the transaction.

    Example:
        POST /add_transaction
        {
            "user_id": "12345",
            "type": "bid",
            "amount": 100.0
        }

    Response:
        {
            "message": "Transaction added successfully"
        }
    """
    data = request.get_json()
    transaction_id = str(uuid.uuid4())
    logging.debug(f"Adding transaction: {data}")

    transaction_type = "unknown"
    if "roll_purchase" in data['type']:
        transaction_type = "roll_purchase"
    elif "auction_credit" in data['type']:
        transaction_type = "auction_credit"
    elif "auction_debit" in data['type']:
        transaction_type = "auction_debit"
    elif "top_up" in data['type']:
        transaction_type = "top_up"

    if mockup:
        # Mock implementation
        return send_response(
            gigio("add_transaction", json={
                "transaction_id": transaction_id,
                "user_id": data["user_id"],
                "type": transaction_type,
                "amount": data["amount"],
            }),
            200
        )
        
    try:
        conn = get_db_connection(DB_HOST, DATABASE)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "INSERT INTO Transactions (transaction_id, user_id, transaction_type, amount) VALUES (%s,%s,%s,%s)",
            (transaction_id, str(data["user_id"]), transaction_type, data["amount"]),
        )

        # Log the derived transaction type
        logging.debug(f"Derived transaction type: {transaction_type}")
        conn.commit()
        if cursor.rowcount == 0:
            return send_response({"error": "Failed to add transaction"}, 500)
        return send_response({"message": "Transaction added successfully"}, 200)
    except Exception as e:
        return manage_errors(e)
    finally:
        release_db_connection(conn, cursor)


@app.route("/get_transaction", methods=["GET"])
@login_required_void
def get_transaction():
    """
    Retrieve a transaction by its ID.

    This endpoint expects a GET request with a 'transaction_id' parameter.
    It queries the database for a transaction with the given ID and returns
    the transaction details in JSON format if found.

    Returns:
        Response: A JSON response containing the transaction details with a 200 status code
                  if the transaction is found.
                  A JSON response with an error message and a 400 status code if the
                  'transaction_id' parameter is missing.
                  A JSON response with an error message and a 404 status code if the
                  transaction is not found.
    """
    transaction_id = request.args.get("transaction_id")
    if not transaction_id:
        return send_response({"error": "Missing transaction_id parameter"}, 400)
    
    if mockup:
        # Mock implementation
        return send_response(
            gigio("get_transaction", transaction_id=transaction_id),
            200
        )
        
    try:
        conn = get_db_connection(DB_HOST, DATABASE)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM Transactions WHERE transaction_id =%s", (transaction_id,)
        )
        transaction = cursor.fetchone()

        if transaction:
            return send_response(dict(transaction), 200)
        return send_response({"error": "Transaction not found"}, 404)

    except Exception as e:
        return manage_errors(e)
    finally:
        release_db_connection(conn, cursor)


@app.route("/get_user_transactions", methods=["GET"])
@login_required_ret
def get_my_transactions(user):
    
    if mockup:
        # Mock implementation
        return send_response(
            gigio("get_user_transactions", user_id=user['user_id']),
            200
        )
    if decode_session_token(request.headers["Authorization"].split(" ")[1])['user_type'] == 'ADMIN':
        return send_response({"error": "You don't have a transaction history (as an ADMIN)"}, 403)
    user_id = str(user['user_id'])
    req = requests.get(f"https://localhost:5000/get_user_transactions/{user_id}",  timeout=30, verify=False, 
                       headers=generate_session_token_system())
    return send_response(req.json(), req.status_code)


@app.route("/get_user_transactions/<user_id>", methods=["GET"])
@admin_required
def get_user_transactions(user_id):
    """
    Endpoint to retrieve transactions for a specific user.

    This endpoint handles GET requests to fetch all transactions associated with a given user ID.
    The user ID must be provided as a query parameter.

    Returns:
        Response: JSON response containing a list of transactions if found, or an error message if no transactions are found or if the user_id parameter is missing.

    Query Parameters:
        user_id (str): The ID of the user whose transactions are to be retrieved.

    Responses:
        200: A JSON array of transactions for the specified user.
        400: A JSON error message indicating that the user_id parameter is missing.
        404: A JSON error message indicating that no transactions were found for the specified user.
    """
    if not user_id:
        return send_response({"error": "Missing user_id parameter"}, 400)
    
    if mockup:
        # Mock implementation
        return send_response(
            gigio("get_user_transactions", user_id=user_id),
            200
        )
        
    try:
        conn = get_db_connection(DB_HOST, DATABASE)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Transactions WHERE user_id =%s", (user_id,))
        transactions = cursor.fetchall()


        if transactions:
            return send_response([dict(transaction) for transaction in transactions], 200)
        return send_response({"error": "No transactions found for the user"}, 404)

    except Exception as e:
        return manage_errors(e)
    finally:
        release_db_connection(conn, cursor)

@app.get("/all")
@login_required_void
def get_all_transactions():
    """
    Retrieve all transactions from the database.

    This endpoint queries the database for all transactions and returns the results as a JSON array.

    Returns:
        Response: A JSON response containing all transactions in the database with a 200 status code.
    """
    
    user = decode_session_token(request.headers["Authorization"].split(" ")[1])
    is_admin = not user['user_type'] == 'PLAYER'
    
    if mockup:
        # Mock implementation
        return send_response(
            gigio("all"),
            200
        )

    try:
        conn = get_db_connection(DB_HOST, DATABASE)
        cursor = conn.cursor(dictionary=True)
        if not is_admin:
            cursor.execute("SELECT * FROM Transactions WHERE user_id =%s", (str(user['user_id']),))
        else:
            cursor.execute("SELECT * FROM Transactions")
        transactions = cursor.fetchall()

        if not transactions:
            return send_response({"error": "No transactions found"}, 404)
        return send_response([dict(transaction) for transaction in transactions], 200)

    except Exception as e:
        return manage_errors(e)
    finally:
        release_db_connection(conn, cursor)

if __name__ == "__main__":
    app.run()

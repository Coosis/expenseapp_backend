from flask import Flask, request, jsonify
import json
import jwt
import sqlite3
import Authentication

app = Flask(__name__)

@app.route('/register', methods=['POST'])
def register(username, password):
    """
    code 409 if user exists.
    code 200 if user is registered successfully.
    """
    conn = sqlite3.connect('E:/expense_tracker.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user WHERE name = ?', (username,))
    user = cursor.fetchone()
    if user:
        conn.close()
        return jsonify({'error': 'User already exists'}), 409
    
    cursor.execute('INSERT INTO user (name, password) VALUES (?, ?)', (username, password))
    conn.commit()
    conn.close()

    return jsonify({'message': 'User registered successfully'}), 200

def delete_user(username):
    """
    delete a user identified by their username.
    """
    conn = sqlite3.connect('E:/expense_tracker.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM user WHERE name = ?', (username,))
    conn.commit()
    conn.close()

@app.route('/login', methods=['POST'])
def login():
    """
    code 401 if username or password is incorrect
    code 200 if user is logged in successfully
    """
    username = request.json['username']
    password = request.json['password']

    code, msg = _login(username, password)
    if code == 200:
        return jsonify({'token': msg}), 200
    return jsonify({'error': msg}), code

def _login(username, password):
    """
    code 401 if username or password is incorrect
    code 200 if user is logged in successfully
    """
    if(not username or not password):
        return (400, 'Missing username or password')
    conn = sqlite3.connect('E:/expense_tracker.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user WHERE name = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    if user:
        return (200, Authentication.create_token(user[0], user[1]))
    return (401, 'Invalid credentials')

@app.route('/add_expense', methods=['POST'])
@Authentication.token_required
def add_expense(payload):
    user_id = payload['user_id']
    _type = request.json['type']
    amount = request.json['amount']
    code, msg = _add_expense(user_id, _type, amount)
    if code != 200:
        return jsonify({'error': msg}), code
    return jsonify({'message': 'Expense added successfully'}), 200

def _add_expense(user_id, _type, amount):
    conn = sqlite3.connect('E:/expense_tracker.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO expense (user_id, type, amount) VALUES (?, ?, ?)', (user_id, _type, amount))
    conn.commit()
    conn.close()

    return (200, 'Expense added successfully')

# delete an expense
def delete_expense(expense_id):
    
    conn = sqlite3.connect('E:/expense_tracker.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM expense WHERE id = ?', (expense_id,))
    conn.commit()
    conn.close()

    return (200, 'Expense deleted successfully')

@app.route('/get_expenses', methods=['GET'])
@Authentication.token_required
def get_expenses(payload):
    """
    get all expenses for a user
    an expense is a tuple of (id, user_id, type, amount)
    code 200 if expenses are returned successfully
    """
    user_id = payload['user_id']
    conn = sqlite3.connect('E:/expense_tracker.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM expense WHERE user_id = ?', (user_id,))
    expenses = cursor.fetchall()
    conn.close()

    return jsonify({'expenses': expenses}), 200

app.run()
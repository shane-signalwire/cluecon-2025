#!/usr/bin/env python3
"""
Max Electric Customer Portal
A web application for customers to view their account balance and information
"""

import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import secrets
import ssl
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generate a random secret key

# Configure logging
import logging
from logging.handlers import RotatingFileHandler
import os

if not app.debug:
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    # Set up file handler with rotation
    file_handler = RotatingFileHandler('logs/max_electric.log', maxBytes=10240000, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    
    app.logger.setLevel(logging.INFO)
    app.logger.info('Max Electric Payment Demo startup')

# Database configuration
DATABASE = 'customer.db'

# SignalWire configuration
SIGNALWIRE_CALL_TOKEN = os.environ.get('SIGNALWIRE_CALL_TOKEN')
SIGNALWIRE_CALL_DESTINATION = os.environ.get('SIGNALWIRE_CALL_DESTINATION')

def get_db_connection():
    """Get database connection with row factory"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with customer table if it doesn't exist"""
    conn = get_db_connection()
    
    # Create customer table if it doesn't exist
    conn.execute('''
        CREATE TABLE IF NOT EXISTS customer (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_number TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            pin TEXT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            balance REAL DEFAULT 0.0
        )
    ''')
    
    # Check if we need to add new columns to existing table
    cursor = conn.execute("PRAGMA table_info(customer)")
    columns = [column[1] for column in cursor.fetchall()]
    
    # Check if we have any data, if not, populate with sample data
    cursor = conn.execute('SELECT COUNT(*) FROM customer')
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Hash the default password "signalwire_rocks" for all users
        default_password_hash = generate_password_hash("signalwire_rocks")
        default_pin = "0803"
        
        # Insert sample data with usernames, hashed passwords, and PINs
        sample_customers = [
            ('12345', 'johnsmith', default_password_hash, default_pin, 'John', 'Smith', '5551234567', '123 Main Street', 100.0),
            ('12557', 'jimsmith', default_password_hash, default_pin, 'Jim', 'Smith', '5551234567', '120 Grove Circle', 0.0),
            ('20000', 'alicej', default_password_hash, default_pin, 'Alice', 'Johnson', '5559876543', '456 Elm Street', 250.0),
            ('20001', 'bobwilliams', default_password_hash, default_pin, 'Bob', 'Williams', '5558765432', '789 Oak Avenue', 300.0),
            ('20002', 'charlieb', default_password_hash, default_pin, 'Charlie', 'Brown', '5557654321', '101 Pine Lane', 150.0),
            ('20003', 'davidw', default_password_hash, default_pin, 'David', 'Wilson', '5556543210', '202 Maple Drive', 400.0),
            ('20004', 'evedavis', default_password_hash, default_pin, 'Eve', 'Davis', '5555432109', '303 Birch Boulevard', 500.0),
            ('20005', 'frankmiller', default_password_hash, default_pin, 'Frank', 'Miller', '5554321098', '404 Cedar Court', 350.0),
            ('20006', 'gracem', default_password_hash, default_pin, 'Grace', 'Moore', '5553210987', '505 Spruce Circle', 275.0),
            ('20007', 'hanktaylor', default_password_hash, default_pin, 'Hank', 'Taylor', '5552109876', '606 Willow Way', 425.0),
            ('20008', 'ivyanderson', default_password_hash, default_pin, 'Ivy', 'Anderson', '5551098765', '707 Aspen Road', 600.0),
            ('20009', 'jackthomas', default_password_hash, default_pin, 'Jack', 'Thomas', '5550987654', '808 Cherry Street', 700.0),
        ]
        
        for customer in sample_customers:
            conn.execute('''
                INSERT INTO customer (account_number, username, password_hash, pin, first_name, last_name, phone, address, balance)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', customer)
    else:
        # If data exists but new columns are missing, update existing records
        cursor = conn.execute("SELECT id, first_name, last_name FROM customer WHERE username IS NULL")
        customers_to_update = cursor.fetchall()
        
        if customers_to_update:
            default_password_hash = generate_password_hash("signalwire_rocks")
            default_pin = "1234"
            
            for customer in customers_to_update:
                username = f"{customer['first_name'].lower()}{customer['last_name'].lower()}"
                # Handle potential duplicates by adding ID
                username = f"{username}{customer['id']}"
                
                conn.execute('''
                    UPDATE customer 
                    SET username = ?, password_hash = ?, pin = ?
                    WHERE id = ?
                ''', (username, default_password_hash, default_pin, customer['id']))
    
    conn.commit()
    conn.close()

def login_required(f):
    """Decorator to require login for certain routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'customer_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Customer login page"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Log the login attempt
        app.logger.info(f"Login attempt for username: {username}")
        
        conn = get_db_connection()
        customer = conn.execute('''
            SELECT * FROM customer 
            WHERE username = ?
        ''', (username,)).fetchone()
        conn.close()
        
        if customer and check_password_hash(customer['password_hash'], password):
            session['customer_id'] = customer['id']
            session['customer_name'] = f"{customer['first_name']} {customer['last_name']}"
            session['account_number'] = customer['account_number']
            session['username'] = customer['username']
            session['pin'] = customer['pin']  # Store PIN for DTMF authentication if needed
            
            app.logger.info(f"Successful login for user: {username}")
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            app.logger.warning(f"Failed login attempt for username: {username}")
            flash('Invalid username or password. Please try again.', 'error')
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """Customer dashboard"""
    conn = get_db_connection()
    customer = conn.execute('''
        SELECT * FROM customer WHERE id = ?
    ''', (session['customer_id'],)).fetchone()
    conn.close()
    
    if customer:
        # Convert to dict and ensure balance is a float
        customer_dict = dict(customer)
        customer_dict['balance'] = float(customer_dict['balance']) if customer_dict['balance'] else 0.0
        print(f"SIGNALWIRE_CALL_TOKEN: {SIGNALWIRE_CALL_TOKEN}")
        print(f"SIGNALWIRE_CALL_DESTINATION: {SIGNALWIRE_CALL_DESTINATION}")
        return render_template('dashboard.html', customer=customer_dict, signalwire_call_token=SIGNALWIRE_CALL_TOKEN, signalwire_call_destination=SIGNALWIRE_CALL_DESTINATION)
    else:
        flash('Customer not found.', 'error')
        return redirect(url_for('login'))

@app.route('/api/balance')
@login_required
def api_balance():
    """API endpoint to get current balance"""
    conn = get_db_connection()
    customer = conn.execute('''
        SELECT balance FROM customer WHERE id = ?
    ''', (session['customer_id'],)).fetchone()
    conn.close()
    
    if customer:
        balance = float(customer['balance']) if customer['balance'] else 0.0
        return jsonify({'balance': balance})
    else:
        return jsonify({'error': 'Customer not found'}), 404

@app.route('/logout')
def logout():
    """Logout user"""
    app.logger.info(f"User logged out: {session.get('username', 'unknown')}")
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/admin/users')
def admin_users():
    """Admin endpoint to view all users (Demo purposes only)"""
    conn = get_db_connection()
    customers = conn.execute('''
        SELECT account_number, username, first_name, last_name, pin, balance 
        FROM customer 
        ORDER BY account_number
    ''').fetchall()
    conn.close()
    
    return jsonify({
        'users': [dict(customer) for customer in customers],
        'password_hint': 'All users have password: signalwire_rocks',
        'pin_hint': 'All users have PIN: 1234'
    })

@app.route('/api/customer', methods=['GET'])
def get_customer_data():
    """API endpoint for DataMap tool to retrieve customer data"""
    account_number = request.args.get('account_number')
    
    if not account_number:
        app.logger.error("Missing account_number parameter in customer data request")
        return jsonify({
            'error': 'Missing account_number parameter'
        }), 400
    
    app.logger.info(f"Customer data request for account: {account_number}")
    
    try:
        conn = get_db_connection()
        customer = conn.execute('''
            SELECT account_number, first_name, last_name, phone, address, balance, pin 
            FROM customer 
            WHERE account_number = ?
        ''', (account_number,)).fetchone()
        conn.close()
        
        if customer:
            customer_data = dict(customer)
            app.logger.info(f"Found customer data for account {account_number}: {customer_data['first_name']} {customer_data['last_name']}")
            return jsonify(customer_data)
        else:
            app.logger.warning(f"No customer found for account number: {account_number}")
            return jsonify({
                'error': f'No customer found with account number {account_number}'
            }), 404
            
    except sqlite3.Error as e:
        app.logger.error(f"Database error retrieving customer data: {e}")
        return jsonify({
            'error': 'Database error occurred'
        }), 500
    except Exception as e:
        app.logger.error(f"Unexpected error retrieving customer data: {e}")
        return jsonify({
            'error': 'Internal server error'
        }), 500


@app.route('/call-support')
def call_support():
    """Click-to-call support page"""
    return render_template('call_support.html', signalwire_call_token=SIGNALWIRE_CALL_TOKEN, signalwire_call_destination=SIGNALWIRE_CALL_DESTINATION)

## Mock Payment Processor ##
@app.route('/payment-processor', methods=['POST'])
def payment_processor():
    """
    Process the payment from the SignalWire Pay Verb
    Example payload:
    {
      'transaction_id': '7ac325f5-b0a4-4a25-bc91-4a4fa9de33fd', 
      'method': 'credit-card', 
      'cardnumber': '4242424242424242', 
      'cvv': '123', 
      'postal_code': '44755', 
      'chargeAmount': '100', 
      'token_type': 'reusable', 
      'expiry_month': '12', 
      'expiry_year': '30', 
      'currency_code': 'usd'
    }
    """
    
    try:
        account_number = request.args.get('account_number')
        payment_amount = request.json['chargeAmount']
        
        # Add validation
        if not account_number:
            app.logger.error("Missing account_number parameter")
            return Response("Missing account_number parameter", status=400)
        if not payment_amount:
            app.logger.error("Missing payment amount")
            return Response("Missing payment amount", status=400)
            
    except Exception as e:
        app.logger.error(f"Parameter parsing error: {e}")
        return Response("Required parameters are missing, transaction failed", status=400)

    try:        
        db = sqlite3.connect("customer.db")
        db.row_factory = sqlite3.Row
        cursor = db.cursor()

        app.logger.info(f"Updating balance for account {account_number} by ${payment_amount}")
        
        # Check if account exists first
        cursor.execute("SELECT balance FROM customer WHERE account_number = ?", (account_number,))
        customer = cursor.fetchone()
        
        if not customer:
            app.logger.error(f"Account {account_number} not found")
            db.close()
            return Response("Account not found", status=404)
        
        old_balance = customer['balance']
        
        # Update the balance
        cursor.execute(
            "UPDATE customer SET balance = balance - ? WHERE account_number = ?",
            (payment_amount, account_number)
        )
        
        # Check if the update actually affected any rows
        if cursor.rowcount == 0:
            app.logger.error(f"No rows updated for account {account_number}")
            db.rollback()
            db.close()
            return Response("Failed to update account balance", status=400)
        
        # Get the new balance for logging
        cursor.execute("SELECT balance FROM customer WHERE account_number = ?", (account_number,))
        new_balance = cursor.fetchone()['balance']
        
        db.commit()
        db.close()
        
        app.logger.info(f"Payment successful - Account {account_number}: ${old_balance} -> ${new_balance}")

    except sqlite3.Error as e:
        app.logger.error(f"Database error during payment processing: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()
        return Response("Database error occurred", status=500)
    except Exception as e:
        app.logger.error(f"Unexpected error during payment processing: {e}")
        if 'db' in locals():
            db.close()
        return Response("The Transaction failed", status=500)

    return Response("The Transaction was successful", status=200)

## Error Handlers ##
@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    return render_template('500.html'), 500

@app.route('/agent', methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/agent/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def agent(path=""):
    # Target service URL - include the path if provided
    if path:
        target_url = f'http://localhost:3000/agent/{path}'
    else:
        target_url = f'http://localhost:3000/agent'
    
    # Forward the request
    resp = requests.request(
        method=request.method,
        url=target_url,
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        data=request.get_data(),
        params=request.args,
        allow_redirects=False
    )
    
    # Return response
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_headers]
    
    response = Response(resp.content, resp.status_code, headers)
    return response

if __name__ == '__main__':
    # Initialize database
    #TODO: Remove this and have a set up script that does this.
    init_db()
    
    app.logger.info("Starting server with HTTPS on port 8080...")
    app.logger.info("Access your app at: https://localhost:8080")
    
    # Run the application with HTTPS
    app.run(host='0.0.0.0', port=8080) 

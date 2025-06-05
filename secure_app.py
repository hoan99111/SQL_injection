#!/usr/bin/env python
"""
secure_app.py - A secure version of the Flask web application using prepared statements
to prevent SQL injection vulnerabilities
"""
from flask import Flask, request, jsonify, render_template_string
import psycopg2
import time
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Database connection parameters
DB_PARAMS = {
    "host": "localhost",
    "database": "demo_sqli",
    "user": "postgres",
    "password": "123456",  # Change this to your PostgreSQL password
    "port": "5432"
}

# HTML template for the web interface
TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Secure SQL Demo</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
        h1 { color: #333; }
        .container { display: flex; flex-wrap: wrap; gap: 20px; }
        .form-container { 
            flex: 1; 
            min-width: 300px; 
            padding: 20px; 
            border: 1px solid #ddd; 
            border-radius: 5px; 
        }
        label { display: block; margin-bottom: 5px; }
        input[type=text], select { width: 100%; padding: 8px; margin-bottom: 10px; border: 1px solid #ddd; border-radius: 3px; }
        input[type=submit] { background-color: #4CAF50; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; }
        input[type=submit]:hover { background-color: #45a049; }
        .result { margin-top: 20px; padding: 15px; background-color: #f9f9f9; border-left: 5px solid #4CAF50; }
        .error { color: red; border-left: 5px solid #ff0000; background-color: #fff0f0; padding: 15px; margin-top: 20px; }
        .info { background-color: #e7f3fe; border-left: 5px solid #2196F3; padding: 15px; margin: 20px 0; }
        .secure-badge { background-color: #4CAF50; color: white; padding: 3px 8px; border-radius: 3px; font-size: 12px; }
    </style>
</head>
<body>
    <h1>SQL Query Demo <span class="secure-badge">Secured</span></h1>
    <div class="info">
        <p>This page demonstrates secure database access using prepared statements and parameterized queries.</p>
        <p><strong>Note:</strong> All inputs are properly sanitized against SQL injection attacks.</p>
    </div>
    
    <div class="container">
        <div class="form-container">
            <h2>User Lookup by ID</h2>
            <form action="/user" method="GET">
                <label for="id">User ID:</label>
                <input type="text" id="id" name="id" placeholder="Enter user ID (e.g., 1)">
                <input type="submit" value="Submit">
            </form>
        </div>
        
        <div class="form-container">
            <h2>User Search by Username</h2>
            <form action="/search" method="GET">
                <label for="username">Username:</label>
                <input type="text" id="username" name="username" placeholder="Enter username (e.g., admin)">
                <input type="submit" value="Search">
            </form>
        </div>
        
        <div class="form-container">
            <h2>Advanced Query</h2>
            <form action="/advanced" method="GET">
                <label for="column">Sort by:</label>
                <select id="column" name="column">
                    <option value="id">ID</option>
                    <option value="username">Username</option>
                    <option value="email">Email</option>
                </select>
                <label for="order">Order:</label>
                <select id="order" name="order">
                    <option value="asc">Ascending</option>
                    <option value="desc">Descending</option>
                </select>
                <input type="submit" value="Query">
            </form>
        </div>
    </div>
    
    {% if result %}
    <div class="result">
        <h3>Results:</h3>
        <pre>{{ result | safe }}</pre>
    </div>
    {% endif %}
    
    {% if error %}
    <div class="error">
        <h3>Error:</h3>
        <pre>{{ error }}</pre>
    </div>
    {% endif %}
</body>
</html>
'''

def get_db_connection():
    """Create and return a new database connection"""
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise

@app.route('/')
def index():
    """Render the main page with all forms"""
    return render_template_string(TEMPLATE)

@app.route('/user')
def get_user():
    """
    Secure endpoint that accepts a user ID parameter and returns user information
    Uses prepared statements to prevent SQL injection
    """
    user_id = request.args.get('id', '')

    if not user_id:
        return render_template_string(TEMPLATE, error="No user ID provided")

    try:
        # Use parameterized query for security
        query = "SELECT id, username, email FROM users WHERE id = %s"

        # Connect to the database
        conn = get_db_connection()
        cur = conn.cursor()

        # Execute with parameter - this is a prepared statement
        cur.execute(query, (user_id,))

        # Fetch results
        users = cur.fetchall()

        # Format results as HTML
        result = ""
        if users:
            for user in users:
                result += f"ID: {user[0]}, Username: {user[1]}, Email: {user[2]}<br>"
        else:
            result = "No user found"

        cur.close()
        conn.close()

        return render_template_string(TEMPLATE, result=result)

    except Exception as e:
        logger.error(f"Error in get_user: {e}")
        # Return a generic error message for security
        return render_template_string(TEMPLATE,
            error="An error occurred while processing your request. Please check your input.")

@app.route('/search')
def search_user():
    """
    Secure user search by username with prepared statements
    """
    username = request.args.get('username', '')

    if not username:
        return render_template_string(TEMPLATE, error="No username provided")

    try:
        # Secure parameterized query with LIKE
        query = "SELECT id, username, email FROM users WHERE username LIKE %s"

        # Connect to the database
        conn = get_db_connection()
        cur = conn.cursor()

        # Execute with parameter including wildcard
        # Note: We add wildcards here in the code, not in the user input
        cur.execute(query, (f"%{username}%",))

        # Fetch results
        users = cur.fetchall()

        # Format results as HTML
        result = ""
        if users:
            for user in users:
                result += f"ID: {user[0]}, Username: {user[1]}, Email: {user[2]}<br>"
        else:
            result = "No users found matching that username"

        cur.close()
        conn.close()

        return render_template_string(TEMPLATE, result=result)

    except Exception as e:
        logger.error(f"Error in search_user: {e}")
        return render_template_string(TEMPLATE,
            error="An error occurred while searching for users. Please check your input.")

@app.route('/advanced')
def advanced_query():
    """
    Secure advanced query with validated params and prepared statements
    """
    # Get parameters with defaults
    column = request.args.get('column', 'id')
    order = request.args.get('order', 'asc')

    # Validate column parameter (whitelist approach)
    allowed_columns = ['id', 'username', 'email']
    if column not in allowed_columns:
        return render_template_string(TEMPLATE,
            error="Invalid column specified. Allowed values: id, username, email")

    # Validate order parameter (whitelist approach)
    allowed_orders = ['asc', 'desc']
    if order not in allowed_orders:
        return render_template_string(TEMPLATE,
            error="Invalid order specified. Allowed values: asc, desc")

    try:
        # Special handling for dynamic column names
        # In PostgreSQL, we can safely use the %s placeholder for table/column names
        # by using psycopg2's sql module
        from psycopg2 import sql

        query = sql.SQL("SELECT id, username, email FROM users ORDER BY {} {}").format(
            sql.Identifier(column),
            sql.SQL(order.upper())
        )

        # Connect to the database
        conn = get_db_connection()
        cur = conn.cursor()

        # Execute the query
        cur.execute(query)

        # Fetch results
        users = cur.fetchall()

        # Format results as HTML
        result = f"Showing all users ordered by {column} {order}:<br><br>"
        if users:
            for user in users:
                result += f"ID: {user[0]}, Username: {user[1]}, Email: {user[2]}<br>"
        else:
            result = "No users found"

        cur.close()
        conn.close()

        return render_template_string(TEMPLATE, result=result)

    except Exception as e:
        logger.error(f"Error in advanced_query: {e}")
        return render_template_string(TEMPLATE,
            error="An error occurred while executing the advanced query.")

@app.errorhandler(404)
def page_not_found(e):
    return render_template_string(TEMPLATE, error="Page not found. Please use one of the forms above."), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {e}")
    return render_template_string(TEMPLATE,
        error="An internal server error occurred. Please try again later."), 500

if __name__ == '__main__':
    logger.info("Starting secure SQL demo application")
    app.run(debug=True, port=5000)

#!/usr/bin/env python
"""
app.py - A deliberately vulnerable Flask web application for SQL injection demonstration
"""
from flask import Flask, request, jsonify, render_template_string
import psycopg2
import time

app = Flask(__name__)

# Database connection parameters
DB_PARAMS = {
    "host": "localhost",
    "database": "demo_sqli",
    "user": "postgres",
    "password": "ducanh",  # Change this to your PostgreSQL password
    "port": "5432"
}

# HTML template for the login form
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>SQL Injection Demo</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
        h1 { color: #333; }
        form { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; max-width: 500px; }
        label { display: block; margin-bottom: 5px; }
        input[type=text] { width: 100%; padding: 8px; margin-bottom: 10px; border: 1px solid #ddd; border-radius: 3px; }
        input[type=submit] { background-color: #4CAF50; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; }
        input[type=submit]:hover { background-color: #45a049; }
        .result { margin-top: 20px; padding: 15px; background-color: #f9f9f9; border-left: 5px solid #4CAF50; }
        .error { color: red; }
    </style>
</head>
<body>
    <h1>SQL Injection Vulnerability Demo</h1>
    <div class="info">
        <p>This page demonstrates a vulnerable endpoint susceptible to SQL injection.</p>
        <p><strong>Note:</strong> This is for educational purposes only.</p>
    </div>
    
    <form action="/user" method="GET">
        <h2>User Lookup</h2>
        <label for="id">User ID:</label>
        <input type="text" id="id" name="id" placeholder="Enter user ID (e.g., 1)">
        <input type="submit" value="Submit">
    </form>
    
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

@app.route('/')
def index():
    """Render the main page with the login form"""
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/user')
def get_user():
    """
    Vulnerable endpoint that accepts a user ID parameter and returns user information
    This endpoint is deliberately vulnerable to SQL injection
    """
    user_id = request.args.get('id', '')

    if not user_id:
        return render_template_string(LOGIN_TEMPLATE, error="No user ID provided")

    try:
        # Vulnerable SQL query - String concatenation without proper parameterization
        query = f"SELECT CAST(id AS VARCHAR), username, email FROM users WHERE id = {user_id}"

        # Connect to the database
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()

        # Execute the vulnerable query
        cur.execute(query)

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

        return render_template_string(LOGIN_TEMPLATE, result=result)

    except Exception as e:
        # Return the error message (gives additional information for error-based SQLi)
        return render_template_string(LOGIN_TEMPLATE, error=str(e))

@app.route('/secure-user')
def get_user_secure():
    """
    Secure endpoint for comparison that uses proper parameterized queries
    This endpoint is protected against SQL injection
    """
    user_id = request.args.get('id', '')

    if not user_id:
        return render_template_string(LOGIN_TEMPLATE, error="No user ID provided")

    try:
        # Secure SQL query using parameterized query
        query = "SELECT id, username, email FROM users WHERE id = %s"

        # Connect to the database
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()

        # Execute the secure query with parameters
        cur.execute(query, (user_id,))

        # Fetch and format results
        users = cur.fetchall()

        result = ""
        if users:
            for user in users:
                result += f"ID: {user[0]}, Username: {user[1]}, Email: {user[2]}<br>"
        else:
            result = "No user found"

        cur.close()
        conn.close()

        return render_template_string(LOGIN_TEMPLATE, result=result)

    except Exception as e:
        return render_template_string(LOGIN_TEMPLATE, error=str(e))

if __name__ == '__main__':
    app.run(debug=True, port=5000)



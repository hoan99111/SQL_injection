# Secure SQL Application Demonstration Guide

This guide provides step-by-step instructions for demonstrating SQL injection prevention techniques using the secure version of the application.

## Prerequisites

1. PostgreSQL installed and running
2. Python 3.x with required packages installed (`pip install -r requirements.txt`)
3. Database setup completed (`python setup_db.py`)

## Setup Instructions

1. First, install the required Python packages:

```bash
pip install -r requirements.txt
```

2. Set up the demo database (only needs to be done once):

```bash
python setup_db.py
```

3. Start the secure Flask application:

```bash
python secure_app.py
```

The secure Flask server will run on `http://localhost:5000`.

## Security Features Demonstration

### 1. Prepared Statements

The secure application uses prepared statements to protect against SQL injection attacks. The key security principle is separating SQL code from user input data.

**To demonstrate:**

1. Open browser to `http://localhost:5000`
2. Enter a user ID (e.g., "1") in the User Lookup form
3. Observe that the application returns the expected user data
4. Try entering SQL injection payloads like `1 OR 1=1` or `1'; DROP TABLE users; --`
5. Notice that these are treated as literal strings, not executable SQL

**Key code to highlight:**
```python
# Secure parameterized query
query = "SELECT id, username, email FROM users WHERE id = %s"
cur.execute(query, (user_id,))
```

### 2. Input Validation for Dynamic Queries

For cases where dynamic elements (like column names) are needed, the secure app implements:
- Whitelisting allowed values
- Using PostgreSQL's SQL module for safe identifier handling

**To demonstrate:**

1. Open browser to `http://localhost:5000`
2. Use the Advanced Query form to sort users by different columns
3. Try changing the URL parameter to an invalid column (e.g., `?column=password`)
4. Notice the application rejects invalid input rather than executing it

**Key code to highlight:**
```python
# Validate column parameter (whitelist approach)
allowed_columns = ['id', 'username', 'email']
if column not in allowed_columns:
    return render_template_string(TEMPLATE, error="Invalid column specified")

# Using SQL module for safe dynamic SQL
from psycopg2 import sql
query = sql.SQL("SELECT id, username, email FROM users ORDER BY {} {}").format(
    sql.Identifier(column),
    sql.SQL(order.upper())
)
```

### 3. Secure LIKE Query Handling

The secure application safely handles pattern matching using LIKE queries without risking SQL injection.

**To demonstrate:**

1. Open browser to `http://localhost:5000`
2. Enter a partial username in the User Search form (e.g., "ad" to find "admin")
3. Try entering SQL injection payloads like `ad%' OR 1=1; --`
4. Notice the application searches for the literal string instead of executing the SQL

**Key code to highlight:**
```python
# Secure parameterized LIKE query
query = "SELECT id, username, email FROM users WHERE username LIKE %s"
cur.execute(query, (f"%{username}%",))
```

### 4. Error Handling and Information Security

The secure application implements proper error handling to avoid leaking sensitive information.

**To demonstrate:**

1. Open browser to `http://localhost:5000` 
2. Try entering invalid inputs that might cause errors
3. Notice that generic error messages are shown instead of detailed SQL errors
4. Highlight that error details are logged server-side but not exposed to users

**Key code to highlight:**
```python
try:
    # Database operations...
except Exception as e:
    logger.error(f"Error in get_user: {e}")
    # Return a generic error message for security
    return render_template_string(TEMPLATE, 
        error="An error occurred while processing your request. Please check your input.")
```

## Comparison with Vulnerable Application

To compare the secure application with the vulnerable version:

1. Run the vulnerable application: `python app.py`
2. Try the same SQL injection payloads on the vulnerable endpoint
3. Observe how the vulnerable app exposes data and error messages
4. Compare with the secure app's resistance to the same attacks

## Security Best Practices Implemented

1. **Prepared Statements**: All database operations use parameterized queries
2. **Input Validation**: Whitelist validation for dynamic elements like column names
3. **Error Handling**: Generic error messages that don't leak database information
4. **Logging**: Proper error logging for monitoring and debugging
5. **Dynamic SQL Security**: Safe handling of dynamic SQL elements using proper escaping

## Additional Testing Recommendations

For a thorough security assessment, try the following:

1. Use the `test_sqli.py` script with various payloads to verify the application's security
2. Try different SQL injection techniques (UNION-based, error-based, time-based) against both apps
3. Verify that all user inputs are properly validated and sanitized

Remember that the purpose of this secure application is educational - to demonstrate proper security practices for preventing SQL injection vulnerabilities.

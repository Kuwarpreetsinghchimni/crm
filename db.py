"""
Database management helper for Customer_Management_System.
Handles connection pooling, query execution, and database schema initialization.
"""

import os
import mysql.connector
from mysql.connector import Error
from config import Config

def get_db_connection(use_database=True):
    """
    Establish and return a connection to MySQL.
    If use_database is False, connects to the MySQL server without selecting a specific database.
    """
    connection_params = {
        "host": Config.MYSQL_HOST,
        "port": Config.MYSQL_PORT,
        "user": Config.MYSQL_USER,
        "password": Config.MYSQL_PASSWORD,
    }
    if use_database:
        connection_params["database"] = Config.MYSQL_DATABASE

    try:
        connection = mysql.connector.connect(**connection_params)
        return connection
    except Error as e:
        # Provide helpful, friendly guidance if connection fails
        print(f"[DB Error] Unable to connect to MySQL: {e}")
        return None

def init_db(schema_path="schema.sql"):
    """
    Initializes the database and tables defined in schema.sql.
    Safe: Creates 'crm_db' if it does not exist, and creates tables with IF NOT EXISTS.
    Does not touch or modify any other existing databases.
    """
    if not os.path.isabs(schema_path):
        schema_path = os.path.join(os.path.dirname(__file__), schema_path)

    if not os.path.exists(schema_path):
        return False, f"Schema file not found at: {schema_path}"

    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    # Split commands by semicolon (ignoring comments/empty blocks)
    raw_statements = schema_sql.split(";")
    
    # Connect without specific database to create database if needed
    conn = get_db_connection(use_database=False)
    if not conn:
        return False, "Failed to connect to MySQL server. Please ensure MySQL is running."

    cursor = None
    try:
        cursor = conn.cursor()
        for stmt in raw_statements:
            cleaned_stmt = stmt.strip()
            if cleaned_stmt:
                cursor.execute(cleaned_stmt)
        conn.commit()
        return True, "Database 'crm_db' and tables initialized successfully."
    except Error as err:
        return False, f"Error initializing database: {err}"
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def query_one(sql, params=None):
    """
    Execute a SELECT query and return a single record as a dict, or None.
    Uses parameterized queries to prevent SQL injection.
    """
    conn = get_db_connection()
    if not conn:
        return None

    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        result = cursor.fetchone()
        return result
    except Error as e:
        print(f"[DB Query Error]: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def query_all(sql, params=None):
    """
    Execute a SELECT query and return all matching records as a list of dicts.
    Uses parameterized queries to prevent SQL injection.
    """
    conn = get_db_connection()
    if not conn:
        return []

    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        results = cursor.fetchall()
        return results
    except Error as e:
        print(f"[DB Query Error]: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def execute_commit(sql, params=None):
    """
    Execute an INSERT, UPDATE, or DELETE query.
    Returns (success: bool, last_row_id or error_message).
    Uses parameterized queries to prevent SQL injection.
    """
    conn = get_db_connection()
    if not conn:
        return False, "Database connection unavailable"

    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        conn.commit()
        last_id = cursor.lastrowid
        row_count = cursor.rowcount
        return True, last_id if last_id else row_count
    except Error as e:
        print(f"[DB Execute Error]: {e}")
        return False, str(e)
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    print("Testing database initialization...")
    ok, message = init_db()
    print(f"Result: {ok} -> {message}")

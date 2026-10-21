# GrandStay Hotel Room Management System
# Database Connection Manager & Query Helpers

import os
import pymysql
from pymysql.cursors import DictCursor
from contextlib import contextmanager
from config import Config

def get_raw_connection(include_db=True):
    """
    Establish a connection to the MySQL server using configured credentials.
    If include_db is False, connects to the server without selecting a specific database.
    """
    connect_kwargs = {
        'host': Config.MYSQL_HOST,
        'port': Config.MYSQL_PORT,
        'user': Config.MYSQL_USER,
        'password': Config.MYSQL_PASSWORD,
        'charset': Config.MYSQL_CHARSET,
        'cursorclass': DictCursor,
        'autocommit': False,
        'connect_timeout': 5
    }
    if include_db:
        connect_kwargs['database'] = Config.MYSQL_DB
        
    return pymysql.connect(**connect_kwargs)

@contextmanager
def get_db():
    """
    Context manager for database operations.
    Automatically commits successful transactions and rolls back on errors.
    Always cleans up the connection.
    """
    conn = None
    try:
        conn = get_raw_connection(include_db=True)
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        raise e
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass

def test_connection():
    """
    Test the MySQL connection.
    Returns (True, "Connected successfully") or (False, "Error message")
    """
    try:
        conn = get_raw_connection(include_db=True)
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 AS test_val")
            res = cursor.fetchone()
        conn.close()
        if res and res.get('test_val') == 1:
            return True, "Connected to MySQL successfully."
        return False, "Connected, but unexpected test query result."
    except pymysql.err.OperationalError as e:
        code, msg = e.args if len(e.args) >= 2 else (0, str(e))
        if code == 1049: # Unknown database
            return False, f"Database '{Config.MYSQL_DB}' does not exist yet. Please import database/schema.sql."
        elif code == 1045: # Access denied
            return False, f"Access denied for user '{Config.MYSQL_USER}'. Please verify password in .env."
        elif code == 2003: # Can't connect to MySQL server
            return False, f"Cannot connect to MySQL server at {Config.MYSQL_HOST}:{Config.MYSQL_PORT}. Is MySQL service running?"
        return False, f"MySQL Operational Error ({code}): {msg}"
    except Exception as e:
        return False, f"Connection failed: {str(e)}"

def query_all(sql, params=None):
    """Execute a SELECT query and return all matching rows as dictionaries."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, params or ())
            return cursor.fetchall()

def query_one(sql, params=None):
    """Execute a SELECT query and return a single row as a dictionary, or None."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, params or ())
            return cursor.fetchone()

def execute(sql, params=None):
    """
    Execute an INSERT, UPDATE, or DELETE query.
    Returns (lastrowid, rowcount).
    """
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, params or ())
            return cursor.lastrowid, cursor.rowcount

def init_db(schema_path=None):
    """
    Helper function to initialize the database and tables from schema.sql.
    Useful for first-time automated setup or reset demonstrations.
    """
    if schema_path is None:
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        
    if not os.path.exists(schema_path):
        return False, f"Schema file not found at {schema_path}"

    try:
        # First connect without database to ensure database exists
        server_conn = get_raw_connection(include_db=False)
        with server_conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{Config.MYSQL_DB}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        server_conn.commit()
        server_conn.close()

        # Now connect to the database and run statements
        with open(schema_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()

        db_conn = get_raw_connection(include_db=True)
        # Split statements by semicolon (ignoring comments/empty lines)
        statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip()]
        
        with db_conn.cursor() as cursor:
            for stmt in statements:
                # Skip comments
                clean_stmt = "\n".join([line for line in stmt.splitlines() if not line.strip().startswith('--')])
                if clean_stmt.strip():
                    cursor.execute(clean_stmt)
        db_conn.commit()
        db_conn.close()
        return True, "Database initialized and schema imported successfully!"
    except Exception as e:
        return False, f"Failed to initialize database: {str(e)}"

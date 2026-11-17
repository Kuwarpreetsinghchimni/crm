"""Database helpers supporting local MySQL and hosted PostgreSQL."""
import os
import mysql.connector
from mysql.connector import Error as MySQLError
from config import Config


def _using_postgres():
    return bool(Config.DATABASE_URL) and Config.DB_TYPE != "mysql"


def get_db_connection(use_database=True):
    """Connect to Render Postgres when DATABASE_URL is set, else local MySQL."""
    if _using_postgres():
        try:
            import psycopg
            from psycopg.rows import dict_row
            url = Config.DATABASE_URL
            if url.startswith("postgres://"):
                url = "postgresql://" + url[len("postgres://"):]
            return psycopg.connect(url, connect_timeout=10, row_factory=dict_row)
        except Exception as e:
            print(f"[DB Error] Unable to connect to PostgreSQL: {e}")
            return None

    params = {"host": Config.MYSQL_HOST, "port": Config.MYSQL_PORT,
              "user": Config.MYSQL_USER, "password": Config.MYSQL_PASSWORD}
    if use_database:
        params["database"] = Config.MYSQL_DATABASE

    # Remote hosted MySQL services such as TiDB require TLS. Certificate and
    # hostname verification can be enabled with MYSQL_SSL_VERIFY=true.
    remote_mysql = Config.MYSQL_HOST not in ("127.0.0.1", "localhost")
    if Config.MYSQL_SSL_CA:
        params["ssl_ca"] = Config.MYSQL_SSL_CA
    if Config.MYSQL_SSL_VERIFY or remote_mysql:
        params["ssl_verify_cert"] = True
        params["ssl_verify_identity"] = True
    try:
        return mysql.connector.connect(**params)
    except MySQLError as e:
        print(f"[DB Error] Unable to connect to MySQL: {e}")
        return None


def _cursor(conn):
    return conn.cursor() if _using_postgres() else conn.cursor(dictionary=True)


def _close(conn, cursor=None):
    if cursor:
        cursor.close()
    if conn:
        conn.close()


def init_db(schema_path=None):
    """Initialize the configured database using the matching schema file."""
    if schema_path is None:
        schema_path = "schema_postgres.sql" if _using_postgres() else "schema.sql"
    if not os.path.isabs(schema_path):
        schema_path = os.path.join(os.path.dirname(__file__), schema_path)
    if not os.path.exists(schema_path):
        return False, f"Schema file not found at: {schema_path}"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = get_db_connection(use_database=False if not _using_postgres() else True)
    if not conn:
        return False, "Failed to connect to the configured database."
    cursor = None
    try:
        cursor = conn.cursor()
        for stmt in schema_sql.split(";"):
            if stmt.strip():
                cursor.execute(stmt.strip())
        conn.commit()
        name = "Render PostgreSQL" if _using_postgres() else Config.MYSQL_DATABASE
        return True, f"Database '{name}' and tables initialized successfully."
    except Exception as err:
        conn.rollback()
        return False, f"Error initializing database: {err}"
    finally:
        _close(conn, cursor)


def query_one(sql, params=None):
    conn = get_db_connection()
    if not conn:
        return None
    cursor = None
    try:
        cursor = _cursor(conn)
        cursor.execute(sql, params or ())
        return cursor.fetchone()
    except Exception as e:
        print(f"[DB Query Error]: {e}")
        return None
    finally:
        _close(conn, cursor)


def query_all(sql, params=None):
    conn = get_db_connection()
    if not conn:
        return []
    cursor = None
    try:
        cursor = _cursor(conn)
        cursor.execute(sql, params or ())
        return cursor.fetchall()
    except Exception as e:
        print(f"[DB Query Error]: {e}")
        return []
    finally:
        _close(conn, cursor)


def execute_commit(sql, params=None):
    conn = get_db_connection()
    if not conn:
        return False, "Database connection unavailable"
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        conn.commit()
        last_id = getattr(cursor, "lastrowid", None)
        return True, last_id if last_id else cursor.rowcount
    except Exception as e:
        conn.rollback()
        print(f"[DB Execute Error]: {e}")
        return False, str(e)
    finally:
        _close(conn, cursor)


if __name__ == "__main__":
    print("Testing database initialization...")
    ok, message = init_db()
    print(f"Result: {ok} -> {message}")

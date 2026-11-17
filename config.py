import os
from dotenv import load_dotenv

# Load environment variables from local .env if present
load_dotenv()

class Config:
    """Application configuration for local development."""
    SECRET_KEY = os.getenv("SECRET_KEY", "sidak-crm-secret-key-local-only")

    # Local MySQL Database Configuration
    # Safe default: host is 127.0.0.1, user is root, password is empty (Enter on prompt)
    MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "crm_db")
    # Render Postgres URL; when set it takes precedence over local MySQL.
    DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

    # Set DB_TYPE=mysql on Render to use a hosted MySQL-compatible database.
    DB_TYPE = os.getenv("DB_TYPE", "").strip().lower()
    MYSQL_SSL_CA = os.getenv("MYSQL_SSL_CA", "").strip()
    MYSQL_SSL_VERIFY = os.getenv("MYSQL_SSL_VERIFY", "").strip().lower() in ("1", "true", "yes")

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

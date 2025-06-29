
from contextlib import contextmanager
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

# Build connection string for pymssql
def get_connection_string():
    server = os.getenv("SQL_SERVER")
    username = os.getenv("SQL_USERNAME")
    password = os.getenv("SQL_PASSWORD")
    database = os.getenv("SQL_DATABASE")

    # print("Server:", os.getenv("SQL_SERVER"))
    # print("Username:", os.getenv("SQL_USERNAME"))
    # print("Password:", os.getenv("SQL_PASSWORD"))
    # print("Database:", os.getenv("SQL_DATABASE"))


    if not all([server, username, password, database]):
        raise ValueError("❌ One or more environment variables are missing!")

    return f"mssql+pymssql://{username}:{password}@{server}:1433/{database}"

# Create SQLAlchemy engine
def get_engine():
    conn_str = get_connection_string()
    return create_engine(conn_str)

# Context manager for connection
@contextmanager
def connection_():
    engine = get_engine()
    conn = engine.connect()
    try:
        yield conn
    finally:
        conn.close()


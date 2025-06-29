
# from contextlib import contextmanager
# import pyodbc
# import os
# from dotenv import load_dotenv
# load_dotenv()
# def get_connection():
   
#     # conn_str = f'''
#     #     DRIVER={os.getenv("driver")};
#     #     SERVER={os.getenv("server")};
#     #     DATABASE={os.getenv("database")};
#     #     UID={os.getenv("username")};
#     #     PWD={os.getenv("password_")};
#     #     Encrypt=yes;
#     #     TrustServerCertificate=no;
#     #     Connection Timeout=30;
#     # '''
#     conn_str = os.getenv("AzureSQLConnectionString")

#     if not conn_str:
#         raise ValueError("Connection string not found in environment variables!")

#     # Optional: fix driver string format if needed
#     conn_str = conn_str.replace("Driver={ODBC Driver 18 for SQL Server}", "DRIVER={ODBC Driver 18 for SQL Server}")
#     return pyodbc.connect(conn_str)



# @contextmanager
# def connection_():
#     conn = get_connection()
#     try:
#         yield conn
#     finally:
#         conn.close()
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


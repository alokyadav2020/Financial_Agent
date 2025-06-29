
from contextlib import contextmanager
import pyodbc
import os
from dotenv import load_dotenv
load_dotenv()
def get_connection():
   
    # conn_str = f'''
    #     DRIVER={os.getenv("driver")};
    #     SERVER={os.getenv("server")};
    #     DATABASE={os.getenv("database")};
    #     UID={os.getenv("username")};
    #     PWD={os.getenv("password_")};
    #     Encrypt=yes;
    #     TrustServerCertificate=no;
    #     Connection Timeout=30;
    # '''
    conn_str = os.getenv("AzureSQLConnectionString")

    if not conn_str:
        raise ValueError("Connection string not found in environment variables!")

    # Optional: fix driver string format if needed
    conn_str = conn_str.replace("Driver={ODBC Driver 18 for SQL Server}", "DRIVER={ODBC Driver 18 for SQL Server}")
    return pyodbc.connect(conn_str)



@contextmanager
def connection_():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()

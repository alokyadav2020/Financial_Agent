
from contextlib import contextmanager
import pyodbc
import os

def get_connection():
   
    # 
    conn_str = os.getenv("AZURE_SQL_CONNECTION_STRING")

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

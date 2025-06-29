
from contextlib import contextmanager
import pyodbc
import os

def get_connection():
   
    conn_str = f'''
        DRIVER={os.getenv("driver")};
        SERVER={os.getenv("server")};
        DATABASE={os.getenv("database")};
        UID={os.getenv("username")};
        PWD={os.getenv("password")};
        Encrypt=yes;
        TrustServerCertificate=no;
        Connection Timeout=30;
    '''
    return pyodbc.connect(conn_str)



@contextmanager
def connection_():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()

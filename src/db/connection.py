import streamlit as st
from contextlib import contextmanager
import pyodbc

def get_connection():
    config = st.secrets["azure_sql"]
    conn_str = f'''
        DRIVER={config["driver"]};
        SERVER={config["server"]};
        DATABASE={config["database"]};
        UID={config["username"]};
        PWD={config["password"]};
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

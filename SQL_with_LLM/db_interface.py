import sqlite3
import pandas as pd



def query_db(query):
    conn = sqlite3.connect('Chinook.db')
    
    try:
        result = pd.read_sql(query,conn)
        conn.close()
        return result
    except Exception as e:
        conn.close()
        print(e)

    return None
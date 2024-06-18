import sqlite3
import pandas as pd
import streamlit as st

def get_db_description():
    data = ''
    try:
        with open('Chinook_db_description.txt','r') as file:
            data= file.readlines()

        text = " ".join(data)
        return text
    except Exception as e:
        print("No db description file found")
        return None
    
def get_data_from_db(sql_query):
    print("getting data from db")
    try:
        conn = sqlite3.connect('Chinook.db')
        df = pd.read_sql(sql_query,conn)
        #print(df.head())
        conn.close()
        return df
    except Exception as e:
        st.error(e)
        conn.close()
        return None
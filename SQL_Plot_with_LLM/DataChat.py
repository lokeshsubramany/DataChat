import streamlit as st

from io import StringIO
import pandas as pd
import time
import PIL
from LLM_interface_OpenAI import *


#st.title("Chat with your data")
st.header('Chat with your data', divider='rainbow')

if 'responses' not in st.session_state:
    st.session_state.responses = []

# with st.sidebar:
#     st.write("### Session state")
#     st.session_state

file_data = None

# Define a function to handle file uploads
def handle_file_upload(uploaded_file):
    if uploaded_file is not None:
        try:
            if uploaded_file.type == 'text/plain':
                # Read text files
                stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
                string_data = stringio.read()
                return string_data, "text"
            elif uploaded_file.type == 'text/csv':
                # Read CSV files
                csv_data = pd.read_csv(uploaded_file)                
                return csv_data, "csv"
            else:
                return f"Unsupported file type: {uploaded_file.type}", "error"
        except Exception as e:
            return f"Error processing file: {e}", "error"
    
    return None, None

def clear_data():    
    st.session_state.responses = []
    
#@st.cache_resource(ttl=1000,show_spinner=False)
def handle_user_input():
    try:
        with st.spinner("Querying model"):
            if st.session_state.functionality == "Analyze a file":
                if st.session_state.Uploaded_file is None:
                    st.error("Please provide a file")
                    return None
                #response = handle_file_to_llm(st.session_state["user_input"],file_data)
                response = analyze_file_data(st.session_state["user_input"],file_data)
            elif st.session_state.functionality == "Ask a database":
                response = analyze_db_data(st.session_state['user_input'])
                print(type(response))
            else:
                response = send_to_llm(st.session_state['user_input'])

        st.session_state.responses.append((st.session_state["user_input"], response))  
    except Exception as e:
        st.error(e)
    
with st.container():
    col1, col2 = st.columns([0.9, 0.1])
    with col1:
        user_input = st.chat_input(key='user_input',on_submit= handle_user_input)
    with col2:  
        submit_button = st.button(label='Clear',on_click= clear_data)
    


    functionality = st.radio(label='What would you like to do?',\
                             options=['Ask a question','Analyze a file','Ask a database'],\
                                horizontal=True,key='functionality')
    #st.write("You selected:",functionality)

    uploaded_file = st.file_uploader("Load your file for analysis", type=['txt', 'csv'],key='Uploaded_file') 
    with st.expander("Uploaded Sample"):                        

        if uploaded_file:
            with st.spinner("Uploading file..."):
                file_data, file_type = handle_file_upload(uploaded_file)
                time.sleep(1)

            st.markdown("File Content sample")        
            if file_type == "text":
                st.text(file_data[:500])
            elif file_type == "csv":
                st.dataframe(file_data.head(10))
            elif file_type == "error":
                st.error(file_data)

with st.container(height=768):
    # Display chat history in reverse chronological order
    for user_input, response in reversed(st.session_state.responses):
        st.markdown(f"**You:** {user_input}")
        #print(type(response))
        if isinstance(response, str):
            st.markdown(f":rainbow[**Assistant:**] {response}")
            st.markdown("------------------------------------------")
        elif isinstance(response, PIL.Image.Image):
            st.markdown(":rainbow[**Assistant:**]")
            st.image(response)
            st.markdown("------------------------------------------")
        elif isinstance(response, pd.DataFrame):
            st.markdown(":rainbow[**Assistant:**]")
            st.dataframe(response)
            st.markdown("------------------------------------------")
        # elif isinstance(response, PIL.PngImagePlugin.PngImageFile):
        #     st.markdown("**Assistant Image:**")
        #     st.image(response)
        else:
            st.markdown(":rainbow[**Assistant:**]")
            st.image(response)
            st.markdown("------------------------------------------")
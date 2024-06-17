import streamlit as st
import PIL
import io
from chat_functions import *

# Use the full page instead of a narrow central column
st.set_page_config(layout="wide",menu_items={
         'Get Help': 'https://www.extremelycoolapp.com/help',
         'Report a bug': "https://www.extremelycoolapp.com/bug",
         'About': "# This is a header. This is an *extremely* cool app!"
     })

# Streamlit app layout
st.title("Chat with your data")

if 'responses' not in st.session_state:
    st.session_state.responses = []

def clear_text():
    st.session_state["user_input"] = ""
    

# Create a form for user input and submission
with st.form(key='chat_form'):
    # Create two columns: one for the chat interface and one for the uploaded file data
    col1, col2 = st.columns([1, 1])
    #user_input = st.text_area("You:", height=100)  # Set height to make it 3 lines
    #st.session_state["user_input"] = ""
    user_input = st.text_input("You:",key='user_input')  # Set height to make it 3 lines
    
    # Create columns for the buttons
    col1, col2 = st.columns([0.95, 0.05])
    with col1:
        submit_button = st.form_submit_button(label='Send')
    with col2:
        clear_button = st.form_submit_button(label='Clear',on_click=clear_text)


#Two column layout for the uploaded data and chat history
col1,col2 = st.columns([1, 3],gap='large')
file_data = None

with col1:
# File uploader outside the form
    uploaded_file = st.file_uploader("Upload File", type=['txt', 'csv'])
    if uploaded_file:
        file_data, file_type = handle_file_upload(uploaded_file)
        st.markdown("#### File Content")
        
        if file_type == "text":
            st.text(file_data)
        elif file_type == "csv":
            st.dataframe(file_data)
        elif file_type == "error":
            st.error(file_data)

    # Handle button actions
    if submit_button and user_input:
        response = handle_user_input(user_input,file_data)
        st.session_state.responses.append((user_input, response))        
        st.rerun()

    if clear_button:
        st.session_state.responses = []        
        st.rerun()

with col2:
    # Display chat history in reverse chronological order
    for user_input, response in reversed(st.session_state.responses):
        st.markdown(f"**You:** {user_input}")
        #print(type(response))
        if isinstance(response, str):
            st.markdown(f"**Assistant:** {response}")
            st.markdown("------------------------------------------")
        elif isinstance(response, PIL.Image.Image):
            st.markdown("**Assistant:**")
            st.image(response)
            st.markdown("------------------------------------------")
        # elif isinstance(response, PIL.PngImagePlugin.PngImageFile):
        #     st.markdown("**Assistant Image:**")
        #     st.image(response)
        else:
            st.markdown("**Assistant:**")
            st.image(response)
            st.markdown("------------------------------------------")


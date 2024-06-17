#from LLM_interface_huggingface import *
from LLM_interface_OpenAI import *

# Define a function to handle user input and generate a response
def handle_user_input(user_input,file_data):       
    # Generate a text response
    output = send_to_llm(user_input,file_data) 
    return output  
    
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
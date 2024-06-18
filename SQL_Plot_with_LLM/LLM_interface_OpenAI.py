
from PIL import Image
import openai
from openai import OpenAI
from dotenv import load_dotenv, dotenv_values 
from PIL import Image
from io import BytesIO,StringIO
import time
from db_interface import *
import os
import streamlit as st
  

def send_file_to_llm(user_query,file_data):

    """
    Handles interaction with the OpenAI API to process a file and generate a response based on the user query.

    Parameters:
    - user_query (str): The query provided by the user for which the response is to be generated.
    - file_data (DataFrame): The file data to be uploaded and processed.

    Returns:
    - str: The response text from the assistant if no image is generated.
    - Image: The generated image if the response includes an image file.
    """

    load_dotenv()
    client = OpenAI()
    
    print("The data type of the file data is ", type(file_data))

    # Upload a file with an "assistants" purpose
    try:
        file = client.files.create(
            file=BytesIO(file_data.to_csv(index=False).encode('utf-8')),
            purpose='assistants'
        )
        print(file)
    except Exception as e:
        print(f"Error uploading file: {e}")
        return

    # Create an assistant using the file ID
    try:
        assistant = client.beta.assistants.create(
            instructions="You are a data analyst. When asked questions, write and run code to answer the question.",
            model="gpt-3.5-turbo",
            tools=[{"type": "code_interpreter"}],
            tool_resources={
                "code_interpreter": {
                    "file_ids": [file.id]
                }
            }
        )
    except Exception as e:
        print(f"Error creating assistant: {e}")
        return

    try:
        thread = client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": user_query,
                    "attachments": [
                        {
                            "file_id": file.id,
                            "tools": [{"type": "code_interpreter"}]
                        }
                    ]
                }
            ]
        )
    except Exception as e:
        print(f"Error creating thread: {e}")
        return

    try:
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id
        )
    except Exception as e:
        print(f"Error creating run: {e}")
        return

    max_retries = 30
    retries = 0

    while retries < max_retries:
        try:
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            print(f"Current run status: {run.status}")
            if run.status == "completed":
                print("Run complete")
                break
            elif run.status == "failed":
                print("Run failed")
                return
        except Exception as e:
            print(f"Error retrieving run status: {e}")
            return

        retries += 1
        time.sleep(10)

    if retries == max_retries:
        print("Run status check timed out")
        return
        
    try:
        messages = client.beta.threads.messages.list(thread_id=thread.id)
    except Exception as e:
        print(f"Error retrieving messages: {e}")
        return

    image_file_id = ""
    response_text=''
      
    for message in messages:
        print(message.content)
        response_text += f"{message}\n"
        if isinstance(message.content[0], openai.types.beta.threads.image_file_content_block.ImageFileContentBlock):
            image_file_id = message.content[0].image_file.file_id
            print('Found image file')

    if not image_file_id:
         for message in messages:
             return f"{message.content[0].text.value}"
                  
    
    try:
        image_data = client.files.content(image_file_id)
        image_data_bytes = image_data.read()
        print("Image has been generated")
        return Image.open(BytesIO(image_data_bytes))
    
    except Exception as e:
        print(f"Error retrieving image: {e}")
        return response_text

#@st.cache_resource(ttl=1000)
def send_to_llm(user_query):
    """
    Main function to interact with the LLM. Determines whether a file is provided and routes the request accordingly.

    Parameters:
    - user_query (str): The query provided by the user.
    - file_data (DataFrame or None): The file data to be processed. If None, only the query is processed.

    Returns:
    - str: The response text from the assistant if no image is generated.
    - Image: The generated image if the response includes an image file.
    """

    load_dotenv()
   
    # Define the LLM
    client = OpenAI()

    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful data analyst.\
                 Use only the information provided in the text to answer the question."},
                {"role": "user", "content": user_query}
            ]
        )
        response = completion.choices[0].message.content
    except Exception as e:
        print(f"Error in chat completion: {e}")
        return

    print(response)
    return response


def get_sql_prompt(user_query,db_description):
    schema_template = "Here is the schema of a database. "+db_description\
    +"\n Write a SQL query to answer the following question. Provide only the SQL and nothing else\n"\
    +"Use explicit column names in the SQL. Ensure there are no ambiguous column names."

    user_request = schema_template+user_query
    return user_request

def get_code_prompt_for_plotting(user_query,df):
    request = "Here is a sample dataframe\n "+ df.head(10).to_string() \
    + "\n Provide only Python code to answer the question and nothing else. "\
    + "Assume that the data is available in a dataframe df, and use only data from the sample provided. "\
    + "Don't include any data in the code. Ensure you import all required libraries "\
    + "Any plots should have a size of 10,5 and a dpi of 300. \
      Use seaborn to generate the plots and use the viridis colormap if it isn't specified in the question.\
     Save the image as a png in the current directory with the name plot_image.png\
        Question: "
    request += user_query
    return request

def execute_code(code,data):
    try:
        #df = data
        exec(code,{'df':data})
        print(os.getcwd())
    except Exception as e:
        print(e)

def get_code_and_generate_plot(user_query,data):
    filepath = os.path.join(os.getcwd(),"plot_image.png")
    
    print(filepath)
    #Delete any existing image file
    if os.path.isfile("plot_image.png"):        
        os.remove(filepath)

    code_request = get_code_prompt_for_plotting(user_query,data.head(10))

    code = send_to_llm(code_request)[10:-3]
    
    execute_code(code, data)

    try:
        
        img = Image.open(filepath)
        #os.remove(filepath)
        return img
    except:
        print("Image file not found")
        return code

def plot_or_not(user_query):
    #Check if it's a plotting request or data analysis request
    response = send_to_llm("Does the following user query have any instructions to generate an image of a plot. \
                           Respond Yes or No. Do not add any other text. User query:"+user_query)
    print('Plot or not result is ',response)
    return response

def analyze_db_data(user_query):

    db_description = get_db_description()
    sql_request = get_sql_prompt(user_query,db_description)

    sql_query = send_to_llm(sql_request)[7:-3]

    data = get_data_from_db(sql_query)
    print(data.head())

    is_plot = plot_or_not(user_query)
    if is_plot == "Yes":
        response = get_code_and_generate_plot(user_query,data)
    else:
        response = send_file_to_llm(user_query,data)
    return response

    
def analyze_file_data(user_query,file_data):
    
    decision = plot_or_not(user_query)
    
    if decision == "No":
        response = send_file_to_llm(user_query,file_data)
        
        return response
    else:
        print("The data type of the file data is ", type(file_data))
        response = get_code_and_generate_plot(user_query,file_data)
        return response

    
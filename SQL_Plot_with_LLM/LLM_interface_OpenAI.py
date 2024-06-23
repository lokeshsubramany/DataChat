
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
            #model="gpt-4o",
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful data analyst who is an expert in SQL, \
                 python and in creating static visualizations.\
                 Use only the information provided in the text to answer the question. Respond in a fun upbeat tone."},
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
    +"\n Write a SQL query to gather data to answer the following question. Provide only the SQL and nothing else\n"\
    +"Use explicit column names in the SQL. Only use columns and tables present in the text.\
        Ensure there are no ambiguous column names."

    user_request = schema_template+user_query
    return user_request

def get_prompt_to_fix_db_error(sql_query, error):
    fix_sql_query_prompt = "You are an expert at writing SQL. Here is the schema and description of the database"\
        + get_db_description() + " This is a SQL query and the error associated with the query.\n \
            SQL and error: " + sql_query + '\n' + error \
        + "Fix the error and return only SQL"
        
    return fix_sql_query_prompt

def get_code_prompt_for_plotting(user_query,cols):
    print("\nIn get_code_prompt_for_plotting ")
    request = """
    You are an expert at writing python code. You are give the columns of a dataframe.
    Provide only Python code to create a plot to answer the question and nothing else. Do not add any notes.
    Do not create or initialize a new dataframe. Use provided data. Import all necessary libraries. 
    Any plots should have a size of 10,6 and a dpi of 300. Use matplotlib or seaborn and the viridis colormap to generate the plots. 
    Save the image as a png in the current directory with the name plot_image.png. 
    Check for potential errors in the code and correct them. Use seaborn for heatmap, matplotlib for pie chart.
    Here's an example

    Question:Here are the columns of the dataframe Genre,TotalSales. Create a bar chart to show the total sales for each music genre
    Response:
    import matplotlib.pyplot as plt
    from matplotlib import rcParams

    # Set figure size and DPI
    rcParams['figure.figsize'] = 10,6
    rcParams['figure.dpi'] = 300

    # Group by Genre and sum TotalSales
    genre_grouped = df.groupby('Genre')['TotalSales'].sum()

    # Create bar chart
    plt.bar(genre_grouped.index, genre_grouped.values)

    plt.xlabel('Genre')
    plt.ylabel('Total Sales')
    plt.title('Total Sales per Music Genre')

    # Save plot as png
    plt.savefig('plot_image.png')
    
    Now, answer the question below
    Question: 
    Here are the columns of the dataframe """+ cols + ". "+user_query+ "\n"
    #print(request)
    return request

def get_prompt_to_fix_python_error(code, error):
    print("\n In get_prompt_to_fix_python_error")

    fix_python_error_prompt = """
    You are an expert at writing python code. Here's the code and error associated with the code.
    Fix the error and return only the python code. Do not add any other characters.
    Here's an example
    Code and error:
        import seaborn as sns
        import matplotlib.pyplot as plt

        #Set figure size and DPI
        rcParams['figure.figsize'] = 10,5 rcParams['figure.dpi'] = 300

        #Pivot table to rearrange data
        pivot_table = df.pivot_table(values='Popularity', index='Country', columns='Genre')

        #Create heatmap
        sns.heatmap(pivot_table, cmap='viridis')

        #Add labels and title
        plt.xlabel('Genre') plt.ylabel('Country') plt.title('Heatmap of Genre Popularity by Country')

        #Save plot as png
        plt.savefig('plot_image.png')

        In execute_code Error executing code name 'rcParams' is not defined
        Response:                
        import seaborn as sns
        import matplotlib.pyplot as plt
        from matplotlib import pyplot

        # Set figure size and DPI
        pyplot.rcParams['figure.figsize'] = 10,5
        pyplot.rcParams['figure.dpi'] = 300

        # Pivot table to rearrange data
        pivot_table = df.pivot_table(values='Popularity', index='Country', columns='Genre')

        # Create heatmap
        sns.heatmap(pivot_table, cmap='viridis')

        # Add labels and title
        plt.xlabel('Genre')
        plt.ylabel('Country')
        plt.title('Heatmap of Genre Popularity by Country')

        # Save plot as png
        plt.savefig('plot_image.png')
        
        Now, answer the following
        Code and Error:
    """ + code + '\n' + error
    

def execute_code(code,data,exec_count = 0):
    print("\n In execute code, with count = ", exec_count)

    filepath = os.path.join(os.getcwd(),"plot_image.png")    
    print(filepath)

    #Delete any existing image file
    if os.path.isfile("plot_image.png"):        
        os.remove(filepath)

    try:
        #df = data
        exec(code,{'df':data})
        print(os.getcwd())
    except Exception as e:
        if exec_count < 1:
            exec_count +=1
            print("Error executing code ",e)
            error = getattr(e,'message',repr(e))

            fix_python_error_prompt = get_prompt_to_fix_python_error(code, error) 
            print("Fix error prompt is ", fix_python_error_prompt)       
            code = send_to_llm(fix_python_error_prompt)[10:-3]

            return_obj = execute_code(code, data, exec_count)
        return return_obj

    try:        
        img = Image.open(filepath)
        #os.remove(filepath)
        return img
    except:
        print("Image file not found")
        return code

def get_code_and_generate_plot(user_query,data):    

    code_request = get_code_prompt_for_plotting(user_query,",".join(data.columns))

    code = send_to_llm(code_request)[10:-3]
    print("Received code is ", code)
    response = execute_code(code, data)    
    return response

def plot_or_not(user_query):
    #Check if it's a plotting request or data analysis request
    plot_or_not_prompt ="""
    You are an expert at understanding language. Is there an intent to create a 
    plot in the user query? Respond True or False only. Do not add any other text
    or characters. Here are some examples
    User query: Create a pie plot of the top 10 artists
    Response: True

    User query: Create a heatmap of the popularity of the genre by country
    Response: True

    User query: Who are the top 10 artists by sales
    Response: False

    Now answer the following user query
    User query:
    """
    response = send_to_llm(plot_or_not_prompt+user_query)
    print('Plot or not result is ',response)
    return response

def analyze_db_data(user_query):

    db_description = get_db_description()
    sql_request = get_sql_prompt(user_query,db_description)

    sql_query = send_to_llm(sql_request)[7:-3]

    data = get_data_from_db(sql_query)
    print("Here's the data",data.head())

    is_plot = plot_or_not(user_query)
    if is_plot == "True":
        response = get_code_and_generate_plot(user_query,data)
        return response
    #else:
        #response = send_file_to_llm(user_query,data)
    return data

    
def analyze_file_data(user_query,file_data):
    
    decision = plot_or_not(user_query)
    
    if decision == "No":
        response = send_file_to_llm(user_query,file_data)        
        return response
    else:
        print("The data type of the file data is ", type(file_data))
        response = get_code_and_generate_plot(user_query,file_data)
        return response

    
from LLM_interface_OpenAI import *
from db_interface import *

with open('Chinook_db_description.txt','r') as file:
    data= file.readlines()

db_description_text = " ".join(data)

schema_template = "Here is the schema of a database. "+db_description_text\
    +"\n Write a SQL query to answer the following question. \
        Check for ambiguous column names and  correct the issue.\
        Provide only the SQL and nothing else\n"
# user_query = "How much did each customer spend in total in descending order"
# user_request = schema_template+user_query

# Define a function to handle user input and generate a response
def handle_user_input(user_input,file_data):       
    # Generate a text response
    output = send_to_llm(schema_template+user_input) 
    output = output.split(';')[0][7:]

    result = query_db(output)
    print(result.head())
    print(type(result))

    return output,result
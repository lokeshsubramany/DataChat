from db_interface import *
from chroma_management import *

def get_plot_or_not_prompt():
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
    return plot_or_not_prompt

def get_sql_prompt(user_query, db_description):
    print("Function: get_sql_prompt")
    schema_template = "Here is the schema of a database. "+db_description\
    +"\n Write a SQL query to gather data to answer the following question. Provide only the SQL and nothing else\n"\
    +"Use explicit column names in the SQL. Only use columns and tables present in the text.\
        Ensure there are no ambiguous column names."

    user_request = schema_template + user_query
    return user_request

def get_prompt_to_fix_db_error(sql_query, error):
    print("Function: get_prompt_to_fix_db_error")
    fix_sql_query_prompt = "You are an expert at writing SQL. Here is the schema and description of the database"\
        + get_db_description() + " This is a SQL query and the error associated with the query.\n \
            SQL and error: " + sql_query + '\n' + error \
        + "Fix the error and return only SQL"
        
    return fix_sql_query_prompt

def get_code_prompt_for_plotting(user_query, cols):
    print("Function: get_code_prompt_for_plotting")
    request = """
    You are an expert at writing python code. You are give the columns of a dataframe.
    Provide only Python code to create a plot to answer the question and nothing else. Do not add any notes.
    Do not create or initialize a new dataframe. Use provided data. Import all necessary libraries. 
    Any plots should have a size of 10,6 and a dpi of 300. Use matplotlib or seaborn and the viridis colormap to generate the plots. 
    Save the image as a png in the current directory with the name plot_image.png. 
    Check for potential errors in the code and correct them. Use seaborn for heatmap, matplotlib for pie chart.
    Here's an example  
    """ 

    RAG_examples = chroma_query(user_query)
    if RAG_examples:
        request += RAG_examples
    
    #print("After adding examples from RAG: ", request)

    request = request + """ Now, answer the question below
    Question: 
    Here are the columns of the dataframe """+cols + ". " + user_query + "\n"
    #print(request)
    return request

def get_prompt_to_fix_python_error(code, error):
    print("Function: get_prompt_to_fix_python_error")
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

    return fix_python_error_prompt
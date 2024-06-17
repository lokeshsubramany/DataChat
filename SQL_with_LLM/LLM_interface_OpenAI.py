
from PIL import Image
import openai
from openai import OpenAI
from dotenv import load_dotenv, dotenv_values 
from PIL import Image
from io import BytesIO,StringIO
import time
import datetime
import pandas as pd


def handle_file_to_llm(user_query,file_data):

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
                {"role": "system", "content": "You are a helpful data analyst"},
                {"role": "user", "content": user_query}
            ]
        )
        response = completion.choices[0].message.content
    except Exception as e:
        print(f"Error in chat completion: {e}")
        return

    print(response)
    return response




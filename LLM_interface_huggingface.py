
from PIL import Image
from langchain_community.llms import HuggingFaceEndpoint

huggingfacehub_api_token='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'



def send_to_llm(user_query):

    # Define the LLM
    #llm = HuggingFaceEndpoint(repo_id='tiiuae/falcon-7b-instruct', huggingfacehub_api_token=huggingfacehub_api_token)
    llm = HuggingFaceEndpoint(repo_id='defog/sqlcoder-7b-2', huggingfacehub_api_token=huggingfacehub_api_token)

    # Predict the words following the text in question    
    response = llm.invoke(user_query)

    #print(response)
    return response


# Define a function to handle user input and generate a response
def handle_user_input(user_input):
    # Example logic: return text or image based on input
    if "image" in user_input.lower():
        # Generate an image response
        img = Image.new('RGB', (100, 100), color=(73, 109, 137))
        return img
    else:
        # Generate a text response
        output = send_to_llm(user_input) 
        return f"{output}"
    
# Define a function to handle file uploads
def handle_file_upload(uploaded_file):
    if uploaded_file is not None:
        # Example logic: process the uploaded file
        try:
            image = Image.open(uploaded_file)
            return image
        except Exception as e:
            return f"Error processing file: {e}"
    return None
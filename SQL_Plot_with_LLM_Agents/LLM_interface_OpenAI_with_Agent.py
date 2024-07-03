from PIL import Image
import openai
from openai import OpenAI, ChatOpenAI
from dotenv import load_dotenv, dotenv_values 
from PIL import Image
from io import BytesIO,StringIO
import time
from db_interface import *
from prompt_templates import *
from langchain.agents import create_react_agent, AgentExecutor
import langchain
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
from langchain.agents import load_tools
from langchain import hub
from langchain.tools import tool
from langchain_experimental.tools.python.tool import PythonREPLTool

class db_python_agent():
    prompt = hub.pull("hwchase17/react")


def analyze_db_data(user_input):



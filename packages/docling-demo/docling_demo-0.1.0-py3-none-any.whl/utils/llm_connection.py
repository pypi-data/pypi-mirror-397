from langchain_openai import AzureChatOpenAI
from openai import AzureOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

def llm_connection_instance():
    return AzureChatOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_OPENAI_CHAT_MODEL")
    )

def slm_connection_instance():
    return AzureOpenAI(
        api_key=os.getenv("AZURE_SLM_API_KEY"),
        api_version=os.getenv("AZURE_SLM_VESION"),
        azure_endpoint=os.getenv("AZURE_SLM_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_SLM_MODEL")
    )
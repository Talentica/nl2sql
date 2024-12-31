import os
from langchain_openai import AzureOpenAIEmbeddings
from langchain_openai import AzureChatOpenAI
from src.llm.llm_interface import LLMInterface

class AzureOpenAILLM(LLMInterface):
    """Azure Open AI Model"""
    
    @staticmethod
    def get_chat_model():
        return AzureChatOpenAI(
            openai_api_version=os.environ["AZURE_OPENAI_CHAT_API_VERSION"],
            azure_deployment=os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"],
            temperature=0,
            model=os.environ["AZURE_OPENAI_CHAT_MODEL_NAME"],
            verbose=True
        )

    @staticmethod
    def get_embedding_model():
        return AzureOpenAIEmbeddings(
            azure_deployment=os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"],
            openai_api_version=os.environ["AZURE_OPENAI_EMBEDDING_API_VERSION"],
            model=os.environ["AZURE_OPENAI_EMBEDDING_MODEL_NAME"]
        )
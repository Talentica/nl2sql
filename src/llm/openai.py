import os
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from src.llm.llm_interface import LLMInterface

class OpenAILLM(LLMInterface):
    """Azure Open AI Model"""
    
    @staticmethod
    def get_chat_model():
        return ChatOpenAI(
            temperature=0,
            model=os.environ["OPENAI_CHAT_MODEL_NAME"],
            verbose=True
        )

    @staticmethod
    def get_embedding_model():
        return OpenAIEmbeddings(model=os.environ["OPENAI_EMBEDDING_MODEL_NAME"])
from langchain_openai.chat_models.base import BaseChatOpenAI
from langchain_openai.embeddings.base import OpenAIEmbeddings
from src.llm.openai import OpenAILLM

class LLMProvider():
    @staticmethod
    def get_chat_model() -> BaseChatOpenAI:
        """Get chat LLM model."""
        return OpenAILLM.get_chat_model()

    @staticmethod
    def get_embedding_model() -> OpenAIEmbeddings:
        """Get embedding LLM model."""
        return OpenAILLM.get_embedding_model()
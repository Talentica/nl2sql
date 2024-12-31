from langchain_openai.chat_models.base import BaseChatOpenAI
from langchain_openai.embeddings.base import OpenAIEmbeddings

class LLMInterface:
    @staticmethod
    def get_chat_model() -> BaseChatOpenAI:
        """Get chat LLM model."""
        pass

    @staticmethod
    def get_embedding_model() -> OpenAIEmbeddings:
        """Get embedding LLM model."""
        pass
import os
from enum import Enum
from typing import Any
from src.llm.llm_provider import LLMProvider
from src.vector_store.QdrantHandler import QdrantHandler
from src.vector_store.FAISSHandler import FAISSHandler
from src.vector_store.AzureSearchHandler import AzureSearchHandler


class VectorDBProvider(Enum):
    QDRANT_LOCAL = "qdrant_local"
    QDRANT_CLOUD = "qdrant_cloud"
    FAISS_LOCAL = "faiss_local"
    AZURE_SEARCH = "azure_search"


class VectorStoreFactory:
    """Factory to create vector store instances based on environment configuration."""

    @staticmethod
    def get_vector_store(index_name_or_path: str) -> Any:
        """
        Returns a vector store instance based on the environment configuration.

        Args:
            index_name_or_path (str): The name or path(in case of FAISS local) of the vector index.

        Returns:
            Any: An instance of the vector store handler.

        Raises:
            ValueError: If required environment variables are missing or invalid.
        """
        embeddings = LLMProvider.get_embedding_model()

        vector_db_provider = get_env_var("VECTOR_DB_PROVIDER", required=True)

        try:
            provider = VectorDBProvider(vector_db_provider)
        except ValueError:
            raise ValueError(
                f"Invalid VECTOR_DB_PROVIDER: {vector_db_provider}. "
                f"Valid options are {[provider.value for provider in VectorDBProvider]}"
            )

        handler_mapping = {
            VectorDBProvider.QDRANT_LOCAL: VectorStoreFactory._create_qdrant_local,
            VectorDBProvider.QDRANT_CLOUD: VectorStoreFactory._create_qdrant_cloud,
            VectorDBProvider.FAISS_LOCAL: VectorStoreFactory._create_faiss_local,
            VectorDBProvider.AZURE_SEARCH: VectorStoreFactory._create_azure_search,
        }

        if provider not in handler_mapping:
            raise ValueError(
                f"Unhandled provider: {provider}. This should never happen."
            )

        return handler_mapping[provider](index_name_or_path, embeddings)

    @staticmethod
    def _create_qdrant_local(vector_index_name: str, embeddings: Any) -> QdrantHandler:
        qdrant_local_db_path = get_env_var("QDRANT_LOCAL_VECTOR_DB_PATH", required=True)
        return QdrantHandler(
            collection_name=vector_index_name,
            embeddings=embeddings,
            storage_type="local",
            qdrant_path=qdrant_local_db_path,
        )

    @staticmethod
    def _create_qdrant_cloud(vector_index_name: str, embeddings: Any) -> QdrantHandler:
        qdrant_url = get_env_var("QDRANT_CLOUD_URL", required=True)
        qdrant_api_key = get_env_var("QDRANT_CLOUD_API_KEY", required=True)
        return QdrantHandler(
            collection_name=vector_index_name,
            embeddings=embeddings,
            storage_type="cloud",
            url=qdrant_url,
            api_key=qdrant_api_key,
        )

    @staticmethod
    def _create_faiss_local(vector_index_path: str, embeddings: Any) -> FAISSHandler:
        return FAISSHandler(local_vector_path=vector_index_path, embeddings=embeddings)

    @staticmethod
    def _create_azure_search(
        vector_index_name: str, embeddings: Any
    ) -> AzureSearchHandler:
        vector_store_address = get_env_var("AZURE_VECTOR_STORE_URL", required=True)
        vector_store_password = get_env_var(
            "AZURE_VECTOR_STORE_PASSWORD", required=True
        )
        return AzureSearchHandler(
            vector_store_address,
            vector_store_password,
            vector_index_name,
            embeddings,
        )


def get_env_var(key: str, required: bool = False) -> str:
    """
    Retrieve an environment variable.
    """
    value = os.environ.get(key)
    if required and not value:
        raise ValueError(f"Environment variable '{key}' is required but not set.")
    return value
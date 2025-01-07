import os
from src.llm.llm_provider import LLMProvider
from src.vector_store.QdrantHandler import QdrantHandler


class VectorStoreFactory:
    """Factory to create vector store instances based on environment configuration."""

    @staticmethod
    def get_vector_store():
        embeddings = LLMProvider.get_embedding_model()

        qdrant_collection_name = os.environ.get("QDRANT_VECTOR_COLLECTION_NAME")
        if not qdrant_collection_name:
            raise ValueError(
                "Environment variable 'QDRANT_VECTOR_COLLECTION_NAME' is required for Qdrant Vector Store."
            )

        qdrant_vector_store_type = os.environ.get("QDRANT_VECTOR_STORE_TYPE")

        if qdrant_vector_store_type == "local":
            qdrant_local_db_path = os.environ.get("QDRANT_LOCAL_VECTOR_DB_PATH")
            if not qdrant_local_db_path:
                raise ValueError(
                    "Environment variable 'QDRANT_LOCAL_VECTOR_DB_PATH' is required for Qdrant Disk Vector Store."
                )
            return QdrantHandler(
                collection_name=qdrant_collection_name,
                embeddings=embeddings,
                storage_type="local",
                qdrant_path=qdrant_local_db_path,
            )

        elif qdrant_vector_store_type == "cloud":
            qdrant_url = os.environ.get("QDRANT_CLOUD_URL")
            qdrant_api_key = os.environ.get("QDRANT_CLOUD_API_KEY")
            if not qdrant_url:
                raise ValueError(
                    "Environment variable 'QDRANT_CLOUD_URL' is required for Qdrant Cloud Vector Store."
                )
            return QdrantHandler(
                collection_name=qdrant_collection_name,
                embeddings=embeddings,
                storage_type="cloud",
                url=qdrant_url,
                api_key=qdrant_api_key,
            )

        else:
            raise ValueError(
                f"Invalid storage_type: {qdrant_vector_store_type}. Valid options are 'local' or 'cloud'."
            )

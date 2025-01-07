import os
from langchain_openai.embeddings.base import OpenAIEmbeddings
from src.vector_store.QdrantDiskHandler import QdrantDiskHandler


class VectorStoreFactory:
    """Factory to create vector store instances based on environment configuration."""

    @staticmethod
    def get_vector_store():
        embeddings = OpenAIEmbeddings()
        qdrant_local_db_path = os.environ.get("QDRANT_LOCAL_VECTOR_DB_PATH")
        qdrant_collection_name = os.environ.get("QDRANT_VECTOR_COLLECTION_NAME")

        if not (qdrant_local_db_path and qdrant_collection_name):
            raise ValueError(
                "Environment variables 'QDRANT_LOCAL_VECTOR_DB_PATH' and 'QDRANT_VECTOR_COLLECTION_NAME' are required for Qdrant Disk Vector Store."
            )
        return QdrantDiskHandler(
            collection_name=qdrant_collection_name,
            path=qdrant_local_db_path,
            embeddings=embeddings,
        )

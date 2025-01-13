# vector_store_service/vector_store_service.py
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams
from langchain_openai.embeddings.base import OpenAIEmbeddings
from qdrant_client.http.models import Distance
from langchain_core.documents import Document
from src.vector_store.BaseVectorStoreHandler import BaseVectorStoreHandler


class QdrantLocalHandler(BaseVectorStoreHandler):
    """Handler for Qdrant vector store."""

    def __init__(
        self,
        collection_name: str,
        embeddings: OpenAIEmbeddings,
        storage_type: str,
        qdrant_path: str,
    ):
        """
        Initialize the Qdrant Handler.

        Args:
            storage_type (str): Specifies the Qdrant storage type.
                                Options:
                                - "local": Use Qdrant in on-disk mode.
                                - "cloud": Use Qdrant Cloud.
            collection_name (str): The name of the Qdrant collection to operate on.
            embeddings (OpenAIEmbeddings): The embedding model to generate vector embeddings.

        """
        self.storage_type = storage_type
        self.collection_name = collection_name
        self.embeddings = embeddings
        self.qdrant_path = qdrant_path

    def _get_client(self):
        """
        Initialize the Qdrant client.
        """
        return QdrantClient(path=self.qdrant_path)

    def create_index(self):
        client = self._get_client()
        client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=3072, distance=Distance.COSINE),
        )
        del client
        print(f"Collection '{self.collection_name}' created successfully.")

    def index_exists(self):
        """
        Check if index already exist.
        """
        try:
            client = self._get_client()
            client.get_collection(collection_name=self.collection_name)
            del client
            return True
        except Exception:
            return False

    def store_documents(self, documents):
        # Generate embeddings for documents
        texts = [doc.page_content for doc in documents]
        vectors = [self.embeddings.embed_query(text) for text in texts]

        # Create points
        points = [
            PointStruct(
                id=i,
                vector=vector,
                payload={"content": doc.page_content, "metadata": doc.metadata},
            )
            for i, (vector, doc) in enumerate(zip(vectors, documents))
        ]

        # Upsert points into the collection
        client = self._get_client()
        client.upsert(collection_name=self.collection_name, points=points)
        del client

    def delete_index(self):
        client = self._get_client()
        client.delete_collection(self.collection_name)
        print(f"Deleted Qdrant collection: {self.collection_name}")
        del client

    def retrieve_documents(self, query, k):
        query_vector = self.embeddings.embed_query(query)
        client = self._get_client()
        results = client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=k,
        )
        del client

        # Convert search results to langchain document format
        documents = [
            Document(
                page_content=hit.payload["content"], metadata=hit.payload["metadata"]
            )
            for hit in results
        ]
        return documents

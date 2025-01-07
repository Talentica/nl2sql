# vector_store_service/vector_store_service.py
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams
from langchain_openai.embeddings.base import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client.http.models import Distance
from langchain_core.documents import Document
from src.vector_store.BaseVectorStoreHandler import BaseVectorStoreHandler


class QdrantHandler(BaseVectorStoreHandler):
    """Handler for Qdrant vector store."""

    def __init__(
        self,
        collection_name: str,
        embeddings: OpenAIEmbeddings,
        storage_type: str,
        **kwargs,
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
            kwargs: Additional configuration parameters based on the storage type.

        Keyword Args:
            For "local" storage_type:
                - qdrant_path (str): The file system path for Qdrant on-disk storage.
                Example: "./qdrant_data".

            For "cloud" storage_type:
                - url (str): The URL of the On-premise server deployment or Qdrant Cloud instance.
                Example: "https://<your-qdrant-cloud-instance-url>".
                - api_key (str): The API key for authenticating with Qdrant Cloud.

        Raises:
            ValueError: If invalid `storage_type` is provided or required arguments for the chosen
                        storage type are missing.
        """
        self.storage_type = storage_type
        self.collection_name = collection_name
        self.embeddings = embeddings

        self.client = self._initialize_client(**kwargs)

        self._create_collection()

    def _initialize_client(self, **kwargs):
        """
        Initialize the Qdrant client based on the provided storage type.
        """
        if self.storage_type == "local":
            qdrant_path = kwargs.get("qdrant_path", None)
            if not qdrant_path:
                raise ValueError(
                    "qdrant_path is required for local quadrant disk storage."
                )
            return QdrantClient(path=qdrant_path)

        elif self.storage_type == "cloud":
            url = kwargs.get("url", None)
            api_key = kwargs.get("api_key", None)
            if not url:
                raise ValueError(
                    "url is required for On-premise server deployment or Qdrant Cloud."
                )
            return QdrantClient(url=url, api_key=api_key)

        else:
            raise ValueError(
                f"Invalid storage_type: {self.storage_type}. Valid options are 'local' or 'cloud'."
            )

    def recreate_index(self):
        self._create_collection()

    def is_index_exist(self):
        """
        Check if index already exist.
        """
        try:
            self.client.get_collection(collection_name=self.collection_name)
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
        self.client.upsert(collection_name=self.collection_name, points=points)

    def delete_index(self):
        self.client.delete_collection(self.collection_name)
        print(f"Deleted Qdrant collection: {self.collection_name}")

    def retrieve_documents(self, query, k):
        query_vector = self.embeddings.embed_query(query)
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=k,
        )

        # Convert search results to langchain document format
        documents = [
            Document(
                page_content=hit.payload["content"], metadata=hit.payload["metadata"]
            )
            for hit in results
        ]
        return documents

    def _create_collection(self):
        """
        Create a new collection in Qdrant if it doesn't already exist.
        """
        if not self.is_index_exist():
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=3072, distance=Distance.COSINE),
            )
            print(f"Collection '{self.collection_name}' created successfully.")

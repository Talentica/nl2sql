import os
import uuid
from langchain_community.document_loaders import DirectoryLoader
from src.vector_store.VectorStoreFactory import VectorStoreFactory


class VectorStoreService:
    """Unified service to manage vector store operations."""

    def __init__(self, vector_index_name):
        self.handler = VectorStoreFactory.get_vector_store(vector_index_name)

    def store_documents(self, doc_dir_path: str):
        documents = self._get_documents(doc_dir_path)
        self.handler.store_documents(documents)

    def delete_index(self):
        self.handler.delete_index()

    def retrieve_documents(self, query: str, k: int):
        return self.handler.retrieve_documents(query, k)

    def _get_documents(self, doc_dir_path: str):
        """Loads documents from a directory."""
        if not os.path.isabs(doc_dir_path):
            # Convert relative path to absolute path relative to the root directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.join(script_dir, "..", "..")
            doc_dir_path = os.path.abspath(os.path.join(project_root, doc_dir_path))

        loader = DirectoryLoader(doc_dir_path)
        documents = loader.load()

        for doc in documents:
            doc.id = str(uuid.uuid4())
            doc.metadata["id"] = doc.id

        return documents

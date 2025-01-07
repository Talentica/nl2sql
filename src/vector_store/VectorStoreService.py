import os
from src.vector_store.VectorStoreFactory import VectorStoreFactory
from langchain_community.document_loaders import DirectoryLoader


class VectorStoreService:
    """Unified service to manage vector store operations."""

    def __init__(self):
        self.handler = VectorStoreFactory.get_vector_store()

    def store_documents(self, doc_dir: str):
        documents = self._get_documents(doc_dir)
        self.handler.store_documents(documents)

    def delete_index(self):
        self.handler.delete_index()

    def retrieve_documents(self, query: str, k: int):
        return self.handler.retrieve_documents(query, k)

    def _get_documents(self, dir_name: str):
        """Loads documents from a directory."""
        current_file_path = os.path.abspath(__file__)
        main_dir = os.path.dirname(current_file_path)
        sub_folder_path = os.path.join(main_dir, "..", "data", dir_name)
        doc_dir_abs_path = os.path.abspath(sub_folder_path)

        loader = DirectoryLoader(doc_dir_abs_path)
        return loader.load()

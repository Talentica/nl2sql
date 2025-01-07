from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential
from langchain_community.vectorstores.azuresearch import AzureSearch
from src.vector_store.BaseVectorStoreHandler import BaseVectorStoreHandler


class AzureSearchHandler(BaseVectorStoreHandler):
    """Handler for AzureSearch operations."""

    def __init__(
        self, vector_store_address, vector_store_password, azure_index_name, embeddings
    ):
        self.vector_store_address = vector_store_address
        self.vector_store_password = vector_store_password
        self.azure_index_name = azure_index_name
        self.embeddings = embeddings
        self.vector_store = self._get_azure_vector_store()

    def store_documents(self, documents):
        self.vector_store.add_documents(documents=documents)

    def recreate_index(self):
        self.vector_store = self._get_azure_vector_store()

    def is_index_exist(self):
        client = SearchIndexClient(
            self.vector_store_address, AzureKeyCredential(self.vector_store_password)
        )
        try:
            client.get_index()
            return True
        except Exception:
            return False

    def delete_index(self):
        client = SearchIndexClient(
            self.vector_store_address, AzureKeyCredential(self.vector_store_password)
        )
        client.delete_index(self.azure_index_name)
        print(f"Deleted Azure index: {self.azure_index_name}")

    def retrieve_documents(self, query, k):
        return self.vector_store.similarity_search(
            query=query, k=k, search_type="similarity"
        )

    def _get_azure_vector_store(self):
        return AzureSearch(
            azure_search_endpoint=self.vector_store_address,
            azure_search_key=self.vector_store_password,
            index_name=self.azure_index_name,
            embedding_function=self.embeddings.embed_query,
            additional_search_client_options={"retry_total": 4},
        )

from langchain_core.documents import Document


class BaseVectorStoreHandler:
    """Base class for vector store handlers."""

    def create_index(self):
        """Create the vector index. Initializes or resets the index to a new state."""
        raise NotImplementedError

    def index_exists(self) -> bool:
        """
        Check if the vector index exists.
            Returns:
                bool: True if the index exists, False otherwise.
        """
        raise NotImplementedError

    def store_documents(self, documents: list[Document]):
        """
        Store documents in the vector index.
            Args:
                documents (list[Document]): A list of documents to be stored. Each document should
                                  include the content and metadata to be indexed.
        """
        raise NotImplementedError

    def delete_index(self):
        """
        Delete the vector index. Removes all stored data and the index itself.
        """
        raise NotImplementedError

    def retrieve_documents(self, query: str, k: int) -> list[Document]:
        """
        Retrieve documents from the vector index based on a query.
            Args:
                query (str): The input query to search for similar documents.
                k (int): The number of top results to retrieve.
            Returns:
                list[Document]: A list of retrieved documents, including their content and metadata.
        """
        raise NotImplementedError

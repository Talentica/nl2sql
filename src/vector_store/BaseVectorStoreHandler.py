class BaseVectorStoreHandler:
    """Base class for vector store handlers."""

    def store_documents(self, documents):
        raise NotImplementedError

    def delete_index(self):
        raise NotImplementedError

    def retrieve_documents(self, query, k):
        raise NotImplementedError

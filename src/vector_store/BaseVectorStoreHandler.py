class BaseVectorStoreHandler:
    """Base class for vector store handlers."""

    def recreate_index(self):
        raise NotImplementedError

    def is_index_exist(self):
        raise NotImplementedError

    def store_documents(self, documents):
        raise NotImplementedError

    def delete_index(self):
        raise NotImplementedError

    def retrieve_documents(self, query, k):
        raise NotImplementedError

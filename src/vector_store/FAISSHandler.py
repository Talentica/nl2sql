import os
import faiss
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from src.vector_store.BaseVectorStoreHandler import BaseVectorStoreHandler


class FAISSHandler(BaseVectorStoreHandler):
    """Handler for FAISS operations."""

    def __init__(self, index_name, embeddings, faiss_path):
        self.index_name = index_name
        self.embeddings = embeddings
        self.faiss_db_path = faiss_path
        self.vector_store = self._get_FAISS_db()

    def store_documents(self, documents):
        self.vector_store.add_documents(documents)
        self.vector_store.save_local(
            folder_path=self.faiss_db_path, index_name=self.index_name
        )

    def create_index(self):
        index = faiss.IndexFlatL2(len(self.embeddings.embed_query("hello world")))
        self.vector_store = FAISS(
            embedding_function=self.embeddings,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
        )

    def index_exists(self):
        if os.path.exists(self.faiss_db_path):
            faiss_file = "{0}/{1}.faiss".format(self.faiss_db_path, self.index_name)
            pkl_file = "{0}/{1}.pkl".format(self.faiss_db_path, self.index_name)
            return os.path.isfile(faiss_file) and os.path.isfile(pkl_file)
        return False

    def delete_index(self):
        faiss_file = "{0}/{1}.faiss".format(self.faiss_db_path, self.index_name)
        pkl_file = "{0}/{1}.pkl".format(self.faiss_db_path, self.index_name)
        self._delete_file(faiss_file)
        self._delete_file(pkl_file)
        print(f"Deleted FAISS vector store index: {self.index_name}")

    def retrieve_documents(self, query, k):
        retriever = self.vector_store.as_retriever(
            search_type="similarity", search_kwargs={"k": k}
        )
        return retriever.invoke(query)

    def _get_FAISS_db(self):
        if self.index_exists():
            return FAISS.load_local(
                folder_path=self.faiss_db_path,
                embeddings=self.embeddings,
                index_name=self.index_name,
                allow_dangerous_deserialization=True,
            )
        return None

    def _delete_file(self, file_path):
        """
        Deletes a file from disk storage given its relative or absolute path.
        """
        try:
            # Check if the file exists
            if os.path.isfile(file_path):
                os.remove(file_path)
                return True
            else:
                print(f"File '{file_path}' does not exist.")
                return False
        except Exception as e:
            print(f"An error occurred while trying to delete the file: {e}")
            return False

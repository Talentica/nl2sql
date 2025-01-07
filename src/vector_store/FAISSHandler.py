import os
import faiss
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from src.vector_store.BaseVectorStoreHandler import BaseVectorStoreHandler


class FAISSHandler(BaseVectorStoreHandler):
    """Handler for FAISS operations."""

    def __init__(self, index_name, embeddings):
        self.index_name = index_name
        self.embeddings = embeddings
        self.faiss_db_path = os.environ.get("FAISS_LOCAL_VECTOR_DB_PATH")
        if not self.faiss_db_path:
            raise ValueError(
                "FAISS_LOCAL_VECTOR_DB_PATH is required for local FAISS disk storage."
            )

    def store_documents(self, documents):
        vector_store = self._get_FAISS_db()
        vector_store.add_documents(documents)
        vector_store.save_local(
            folder_path=self.faiss_db_path, index_name=self.index_name
        )

    def delete_index(self):
        if os.path.exists(self.faiss_db_path):
            self._delete_file(
                file_path="{0}/{1}.faiss".format(self.faiss_db_path, self.index_name)
            )
            self._delete_file(
                file_path="{0}/{1}.pkl".format(self.faiss_db_path, self.index_name)
            )
            print(f"Deleted FAISS vector store index: {self.index_name}")

    def retrieve_documents(self, query, k):
        db = FAISS.load_local(
            self.faiss_db_path,
            self.embeddings,
            index_name=self.index_name,
            allow_dangerous_deserialization=True,
        )
        retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": k})
        return retriever.invoke(query)

    def _get_FAISS_db(self):
        try:
            return FAISS.load_local(
                folder_path=self.faiss_db_path,
                embeddings=self.embeddings,
                index_name=self.index_name,
                allow_dangerous_deserialization=True,
            )
        except Exception:
            index = faiss.IndexFlatL2(len(self.embeddings.embed_query("hello world")))
            return FAISS(
                embedding_function=self.embeddings,
                index=index,
                docstore=InMemoryDocstore(),
                index_to_docstore_id={},
            )

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

import os
import shutil
from langchain_community.vectorstores import FAISS
from src.vector_store.BaseVectorStoreHandler import BaseVectorStoreHandler


class FAISSHandler(BaseVectorStoreHandler):
    """Handler for FAISS operations."""

    def __init__(self, local_vector_path, embeddings):
        self.local_vector_path = local_vector_path
        self.embeddings = embeddings

    def store_documents(self, documents):
        self.delete_index()
        db = FAISS.from_documents(documents, self.embeddings)
        db.save_local(self.local_vector_path)

    def delete_index(self):
        if os.path.exists(self.local_vector_path):
            shutil.rmtree(self.local_vector_path)
            print(f"Deleted FAISS vector store at: {self.local_vector_path}")

    def retrieve_documents(self, query, k):
        db = FAISS.load_local(
            self.local_vector_path,
            self.embeddings,
            allow_dangerous_deserialization=True,
        )
        retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": k})
        return retriever.get_relevant_documents(query)

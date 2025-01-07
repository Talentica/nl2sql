import os
import shutil
import faiss
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from src.vector_store.BaseVectorStoreHandler import BaseVectorStoreHandler


class FAISSHandler(BaseVectorStoreHandler):
    """Handler for FAISS operations."""

    def __init__(self, local_vector_path, embeddings):
        self.local_vector_path = local_vector_path
        self.embeddings = embeddings
        self.vector_store = self._create_vector_store()

    def store_documents(self, documents):
        self.vector_store.add_documents(documents)
        self.vector_store.save_local(self.local_vector_path)

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
        return retriever.invoke(query)

    def _create_vector_store(self):
        try:
            return FAISS.load_local(
                self.local_vector_path,
                self.embeddings,
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

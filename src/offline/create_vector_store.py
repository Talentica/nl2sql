"""Module to creat and store vector index for DB Schema"""

import os
import sys
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_openai.embeddings.base import OpenAIEmbeddings
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
import shutil
import uuid

# Add the project root directory to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)
from src.llm.llm_provider import LLMProvider
from src.vector_store.VectorStoreFactory import VectorStoreFactory

load_dotenv(os.path.join(os.getcwd(), ".env"))


def get_documents(doc_dir_path: str):
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


def store_vector_index(doc_dir: str):
    """Load the documents, embed and upload it into the vector store."""
    documents = get_documents(doc_dir)
    vector_store_service.store_documents(documents)

    return 200


if __name__ == "__main__":

    vector_index_name = os.environ.get("DB_SCHEMA_VECTOR_INDEX_NAME")
    vector_store_service = VectorStoreFactory.get_vector_store("vector_index_name")

    db_schema_path = os.environ["DB_SCHEMA_PATH"]

    # Getting the list of schemas available
    db_schema_folders = [
        name
        for name in os.listdir(db_schema_path)
        if os.path.isdir(os.path.join(db_schema_path, name))
    ]
    # Creating and storing vector index for each schema
    for schema in db_schema_folders:
        schema_path = os.path.join(db_schema_path, schema)
        store_vector_index(doc_dir=schema_path)
    print("Vector store created successfully!")

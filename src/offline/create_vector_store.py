import os
import sys
import uuid
import logging
from langchain_community.document_loaders import DirectoryLoader
from dotenv import load_dotenv
from langchain.schema import Document

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Add the project root directory to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

# Load environment variables from .env file
load_dotenv()

from src.vector_store.VectorStoreFactory import VectorStoreFactory
from src.offline.data.examples import query_examples


def get_documents(doc_dir_path: str):
    """Loads and processes documents from a directory."""
    doc_dir_path = (
        os.path.abspath(doc_dir_path)
        if os.path.isabs(doc_dir_path)
        else os.path.join(project_root, doc_dir_path)
    )

    if not os.path.exists(doc_dir_path):
        logging.error(f"Document directory does not exist: {doc_dir_path}")
        raise FileNotFoundError(f"Directory not found: {doc_dir_path}")

    loader = DirectoryLoader(doc_dir_path)
    documents = loader.load()

    for doc in documents:
        doc.id = str(uuid.uuid4())
        doc.metadata["id"] = doc.id

    return documents


def initialize_vector_store(index_name: str):
    """Initializes a vector store client, recreating the index if it exists."""
    if not index_name:
        logging.error("Index name is not provided.")
        raise ValueError("Index name cannot be None or empty.")

    vector_store = VectorStoreFactory.get_vector_store(index_name)
    if vector_store.index_exists():
        vector_store.delete_index()
    vector_store.create_index()
    return vector_store


def create_db_schema_index():
    """Creates a vector index for database schemas."""
    db_schema_path = os.getenv("DB_SCHEMA_PATH")
    db_schema_index_name = os.getenv("DB_SCHEMA_VECTOR_INDEX_NAME")

    if not db_schema_path or not db_schema_index_name:
        logging.error(
            "Environment variables DB_SCHEMA_PATH or DB_SCHEMA_VECTOR_INDEX_NAME are not set."
        )
        raise EnvironmentError("Required environment variables are missing.")

    schema_vector_store = initialize_vector_store(db_schema_index_name)

    db_schema_folders = [
        name
        for name in os.listdir(db_schema_path)
        if os.path.isdir(os.path.join(db_schema_path, name))
    ]

    for schema in db_schema_folders:
        schema_path = os.path.join(db_schema_path, schema)
        documents = get_documents(schema_path)
        schema_vector_store.store_documents(documents)

    logging.info(f"Vector index '{db_schema_index_name}' created successfully!")

    del schema_vector_store


def create_sql_query_index():
    """Creates a vector index for SQL queries."""
    sql_query_index_name = os.getenv("SQL_QUERY_VECTOR_INDEX_NAME")

    if not sql_query_index_name:
        logging.error("Environment variable SQL_QUERY_VECTOR_INDEX_NAME is not set.")
        raise EnvironmentError("SQL_QUERY_VECTOR_INDEX_NAME is required but not set.")

    if not query_examples:
        logging.warning(
            "Query examples not provided. Skipping SQL query index creation."
        )
        return

    query_vector_store = initialize_vector_store(sql_query_index_name)

    documents = [
        Document(
            page_content=item["question"], metadata={"sql_query": item["sql_query"]}
        )
        for item in query_examples
    ]

    query_vector_store.store_documents(documents)
    logging.info(f"Vector index '{sql_query_index_name}' created successfully!")

    del query_vector_store


if __name__ == "__main__":
    try:
        create_db_schema_index()
        create_sql_query_index()
    except Exception as e:
        logging.error(f"An error occurred: {e}")

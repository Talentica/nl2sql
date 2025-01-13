"""Module providing a langchain tool for retrieving relevant schema and example queries."""

import os
import sys
from langchain_core.tools import tool
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

# Add the project root directory to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)
# load environment variables from .env file
load_dotenv()

from src.vector_store.VectorStoreFactory import VectorStoreFactory


@tool
def get_schema_and_sql_information(concised_question: str) -> str:
    """This tool provides relevant database schema information and example queries for the given question."""
    with ThreadPoolExecutor() as executor:
        future_schema = executor.submit(get_db_schema_information, concised_question)
        future_query = executor.submit(get_similar_query, concised_question)

        schema_info = future_schema.result()
        query_info = future_query.result()

    return schema_info + query_info


def get_db_schema_information(concised_question: str) -> str:
    """This tool provides relevant db schema to user question."""

    k = 5
    schema_index_name = os.environ["DB_SCHEMA_VECTOR_INDEX_NAME"]
    documents = fetch_relevant_documents(
        concised_question, k=k, vector_index_name=schema_index_name
    )

    schema_information = "Following are the relevant schema information I found: \n"
    for doc in documents:
        schema_information += doc.page_content + "\n"
    return schema_information


def get_similar_query(concised_question: str) -> str:
    """This tool provides queries similar to user question."""

    k = 4
    query_index_name = os.environ["SQL_QUERY_VECTOR_INDEX_NAME"]
    documents = fetch_relevant_documents(
        concised_question, k=k, vector_index_name=query_index_name
    )
    similar_queries = "Following are the similar queries I found: \n"
    for doc in documents:
        similar_queries += (
            "question: "
            + doc.page_content
            + "\n"
            + "sql_query: "
            + doc.metadata["sql_query"]
            + "\n"
        )
    return similar_queries


def fetch_relevant_documents(concised_question, k: int, vector_index_name: str):

    # Initialize vector index
    vector_store_client = VectorStoreFactory.get_vector_store(vector_index_name)
    documents = vector_store_client.retrieve_documents(concised_question, k)

    return documents


if __name__ == "__main__":

    question = sys.argv[1]
    result = get_schema_and_sql_information.invoke(question)
    print(result)

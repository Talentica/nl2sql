"""Module providing a langchain tool for retrieving relevant schema and example queries."""

import os
from langchain_core.tools import tool
from concurrent.futures import ThreadPoolExecutor
from src.vector_store.VectorStoreFactory import VectorStoreFactory


@tool
def get_schema_and_sql_information(
    user_question: str, k1: int = None, k2: int = None
) -> str:
    """This tool provides relevant database schema information and example queries for the given question."""

    if k1 is None:
        k1 = int(os.environ["NUMBER_OF_DB_SCHEMA"])

    if k2 is None:
        k2 = int(os.environ["NUMBER_OF_SQL_QUERY"])

    with ThreadPoolExecutor() as executor:
        future_schema = executor.submit(get_db_schema_information, user_question, k1)
        future_query = executor.submit(get_similar_query, user_question, k2)

        schema_info = future_schema.result()
        query_info = future_query.result()

    return schema_info + query_info


def get_db_schema_information(user_question: str, k: int) -> str:
    """This tool provides relevant db schema to user question."""

    schema_index_name = os.environ["DB_SCHEMA_VECTOR_INDEX_NAME"]
    documents = fetch_relevant_documents(
        user_question, k=k, vector_index_name=schema_index_name
    )

    schema_information = "Following are the relevant schema information I found: \n"
    for doc in documents:
        schema_information += doc.page_content + "\n"

    return schema_information


def get_similar_query(user_question: str, k: int) -> str:
    """This tool provides queries similar to user question."""

    query_index_name = os.environ["SQL_QUERY_VECTOR_INDEX_NAME"]
    documents = fetch_relevant_documents(
        user_question, k=k, vector_index_name=query_index_name
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


def fetch_relevant_documents(user_question, k: int, vector_index_name: str):

    # Initialize vector index
    vector_store_client = VectorStoreFactory.get_vector_store(vector_index_name)
    documents = vector_store_client.retrieve_documents(user_question, k)

    return documents

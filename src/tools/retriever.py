"""Module providing a langchain tool for retrieving relevant schema and example queries."""

import os
from langchain_core.tools import tool
from concurrent.futures import ThreadPoolExecutor
from src.vector_store.VectorStoreFactory import VectorStoreFactory


def get_schema_and_sql_information(user_question: str) -> tuple[str, str]:
    """This tool provides relevant database schema information and example queries for the given question."""

    k1 = int(_get_env_var("NUMBER_OF_DB_SCHEMA_TO_FETCH", required=True))
    k2 = int(_get_env_var("NUMBER_OF_SQL_QUERY_TO_FETCH", required=True))

    schema_score_threshold = float(
        _get_env_var("DB_SCHEMA_SCORE_THRESHOLD", default_value="0.5")
    )
    sql_query_score_threshold = float(
        _get_env_var("SQL_QUERY_SCORE_THRESHOLD", default_value="0.5")
    )

    with ThreadPoolExecutor() as executor:
        future_schema = executor.submit(
            get_db_schema_information, user_question, k1, schema_score_threshold
        )
        future_query = executor.submit(
            get_similar_query, user_question, k2, sql_query_score_threshold
        )

        schema_info = future_schema.result()
        query_info = future_query.result()

    return schema_info, query_info


@tool
def get_db_schema_information(
    user_question: str, k: int, relevance_score_threshold: float = 0.5
) -> str:
    """This tool provides relevant db schema to user question."""

    schema_index_name = os.environ["DB_SCHEMA_VECTOR_INDEX_NAME"]
    documents = fetch_relevant_documents(
        user_question,
        k=k,
        vector_index_name=schema_index_name,
        score_threshold=relevance_score_threshold,
    )

    schema_information = ""
    for doc in documents:
        schema_information += doc.page_content + "\n"

    return schema_information


def get_similar_query(
    user_question: str, k: int, relevance_score_threshold: float = 0.5
) -> str:
    """This tool provides queries similar to user question."""

    query_index_name = os.environ["SQL_QUERY_VECTOR_INDEX_NAME"]
    documents = fetch_relevant_documents(
        user_question,
        k=k,
        vector_index_name=query_index_name,
        score_threshold=relevance_score_threshold,
    )
    similar_queries = ""
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


def fetch_relevant_documents(
    user_question, k: int, vector_index_name: str, score_threshold: float = 0.5
):

    # Initialize vector index
    vector_store_client = VectorStoreFactory.get_vector_store(vector_index_name)
    documents = vector_store_client.retrieve_documents(
        user_question, k, score_threshold
    )

    return documents


def _get_env_var(key: str, default_value=None, required: bool = False) -> str:
    """
    Retrieve an environment variable.
    """
    value = os.environ.get(key, default_value)
    if required and not value:
        raise ValueError(f"Environment variable '{key}' is required but not set.")
    return value

"""Module providing a langchain tool for relevant schema retriever."""

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
def get_relevant_schema_information(concised_question: str) -> str:
    """This tool provides relevant database schema information for the given question."""
    with ThreadPoolExecutor() as executor:
        future_schema = executor.submit(get_schema_information, concised_question)

        schema_info = future_schema.result()
    return schema_info


def get_schema_information(concised_question: str) -> str:

    k = 5
    vector_index_name = os.environ["DB_SCHEMA_VECTOR_INDEX_NAME"]
    documents = fetch_relevant_documents(
        concised_question, k=k, vector_index_name=vector_index_name
    )

    schema_information = "Following are the relevant schema information I found: \n"
    for doc in documents:
        schema_information = schema_information + doc.page_content + "\n\n"
    return schema_information


def fetch_relevant_documents(concised_question, k: int, vector_index_name: str):

    vector_store_client = VectorStoreFactory.get_vector_store(vector_index_name)
    documents = vector_store_client.retrieve_documents(concised_question, k)

    return documents


if __name__ == "__main__":

    question = sys.argv[1]
    result = get_relevant_schema_information.invoke(question)
    print(result)

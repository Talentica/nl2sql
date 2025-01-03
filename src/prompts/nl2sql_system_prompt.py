import os
from langchain import hub

from langchain_community.vectorstores import FAISS
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from src.llm.llm_provider import LLMProvider

from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import FewShotPromptTemplate
from src.data.examples import query_examples
from langchain_core.prompts import SystemMessagePromptTemplate
from src.constants.datatypes import SQL_DIALECTS

def get_nl2sql_prompt():
    dialect = os.environ['DB_DIALECT']
    prompt_template = hub.pull("langchain-ai/sql-agent-system-prompt")
    prompt_message = prompt_template.format(dialect=SQL_DIALECTS[dialect]['full_name'], top_k=5)
    
    if len(query_examples) > 0:
        few_shot_prompt = get_few_shot_prompt(prompt_message)
        final_prompt = SystemMessagePromptTemplate(prompt=few_shot_prompt)
    else:
        final_prompt = ("system", prompt_message)

    return final_prompt

def get_few_shot_prompt(system_prompt) -> FewShotPromptTemplate:
    
    embeddings = LLMProvider.get_embedding_model()
    example_selector = SemanticSimilarityExampleSelector.from_examples(
        query_examples,
        embeddings,
        FAISS,
        k=5,
        input_keys=["input"]
    )

    example_prompt = PromptTemplate.from_template("Question: {input}\n SQL Query: {sql_query}\n")

    system_prompt = system_prompt + "\n##Query Examples:\n"
    
    return FewShotPromptTemplate(
        example_selector=example_selector,
        example_prompt=example_prompt,
        prefix=system_prompt,
        suffix="",
        input_variables=["input"],
    )

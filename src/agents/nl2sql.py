"""Module providing a langchain agent to answer user queries."""
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.agents import OpenAIFunctionsAgent
from langchain.schema import SystemMessage
# from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain.prompts import MessagesPlaceholder

from src.prompts.nl2sql_system_prompt import get_nl2sql_prompt
from src.llm.llm_provider import LLMProvider

from src.db_connector.sql_server import get_db
from langchain_community.agent_toolkits import SQLDatabaseToolkit

from langchain_community.vectorstores import FAISS
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_openai import OpenAIEmbeddings

from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import FewShotPromptTemplate
from src.data.examples import query_examples

from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, MessagesPlaceholder

def get_nl2sql_agent():
    nl2sql_prompt = get_nl2sql_prompt()
    
    if len(query_examples) > 0:
        few_shot_prompt = get_few_shot_prompt(nl2sql_prompt)
        final_prompt = SystemMessagePromptTemplate(prompt=few_shot_prompt)
    else:
        final_prompt = ("system", nl2sql_prompt)

    prompt = ChatPromptTemplate.from_messages(
        [
            final_prompt,
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad")
        ]
    )

    llm = LLMProvider.get_chat_model()

    db = get_db()

    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    tools = toolkit.get_tools()
    
    agent = create_openai_functions_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=10, max_execution_time=50, stream_runnable=False)

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

"""Module providing a langchain agent to answer user queries."""

from langchain.agents import AgentExecutor, create_openai_functions_agent

# from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain.prompts import MessagesPlaceholder

from src.prompts.nl2sql_system_prompt import get_nl2sql_prompt
from src.llm.llm_provider import LLMProvider

from src.db_connector.sql import get_db
from langchain_community.agent_toolkits import SQLDatabaseToolkit

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def get_nl2sql_agent():
    nl2sql_system_prompt = get_nl2sql_prompt()

    prompt = ChatPromptTemplate.from_messages(
        [
            nl2sql_system_prompt,
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )

    llm = LLMProvider.get_chat_model()

    db = get_db()

    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    tools = toolkit.get_tools()

    agent = create_openai_functions_agent(llm, tools, prompt)
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=10,
        max_execution_time=50,
        stream_runnable=False,
    )

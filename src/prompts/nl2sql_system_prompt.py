from langchain import hub

def get_nl2sql_prompt():
    prompt_template = hub.pull("langchain-ai/sql-agent-system-prompt")
    prompt_message = prompt_template.format(dialect="Microsoft SQL Server (mssql)", top_k=5)
    return prompt_message
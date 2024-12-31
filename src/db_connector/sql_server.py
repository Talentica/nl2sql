import os
from langchain_community.utilities import SQLDatabase

def get_db():
    db_user = os.environ['DB_USER']
    db_password = os.environ['DB_PASSWORD']
    db_host = os.environ['DB_HOST']
    db_name = os.environ['DB_NAME']
    db_connection_string = f"mssql+pyodbc://{db_user}:{db_password}@{db_host}/{db_name}?driver=ODBC+Driver+17+for+SQL+Server"
    
    db = SQLDatabase.from_uri(db_connection_string)

    return db

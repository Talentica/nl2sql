import os
from langchain_community.utilities import SQLDatabase
from src.constants.datatypes import SQL_DIALECTS


def get_db():
    dialect = os.environ["DB_DIALECT"]
    db_user = os.environ["DB_USER"]
    db_password = os.environ["DB_PASSWORD"]
    db_host = os.environ["DB_HOST"]
    db_name = os.environ["DB_NAME"]

    db_connection_string = "{0}+{1}://{2}:{3}@{4}/{5}".format(
        dialect, SQL_DIALECTS[dialect]["driver"], db_user, db_password, db_host, db_name
    )

    db = SQLDatabase.from_uri(db_connection_string)

    return db

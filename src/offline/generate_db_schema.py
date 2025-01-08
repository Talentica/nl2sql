import logging
import sys
import os
import sqlalchemy
from sqlalchemy import create_engine, inspect, text
import urllib.parse
from dotenv import load_dotenv, find_dotenv

# Add the project root directory to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

from src.db_connector.sql import connect_to_database

load_dotenv(os.path.join(os.getcwd(), ".env"))


# Function to get table name
def get_table_name(engine):
    try:
        with engine.connect() as connection:
            result = connection.execute(text("show tables"))
            table_names = [row[0] for row in result]
            return table_names
    except Exception as e:
        print(f"Error retrieving table_names: {e}")
        return []


# Function to retrieve table schema
def get_table_schema(engine, table_name):
    try:
        inspector = inspect(engine)
        columns = inspector.get_columns(table_name)
        primary_keys = inspector.get_pk_constraint(table_name)
        foreign_keys = inspector.get_foreign_keys(table_name)

        schema_details = {
            "columns": [],
            "primary_keys": primary_keys.get("constrained_columns", []),
            "foreign_keys": [],
        }

        for column in columns:
            schema_details["columns"].append(
                {
                    "name": column["name"],
                    "type": str(column["type"]),
                    "nullable": column["nullable"],
                }
            )

        for fk in foreign_keys:
            schema_details["foreign_keys"].append(
                {
                    "column": fk["constrained_columns"],
                    "referred_table": fk["referred_table"],
                    "referred_columns": fk["referred_columns"],
                }
            )

        return schema_details

    except Exception as e:
        print(f"Error retrieving table schema: {e}")
        return None


# Function to retrieve sample rows
def get_sample_rows(engine, table_name, limit=3):
    try:
        with engine.connect() as connection:
            query = text(f"SELECT * FROM {table_name} LIMIT {limit}")
            result = connection.execute(query)
            # Fetch column names
            column_names = result.keys()

            # Fetch rows
            rows = [dict(zip(column_names, row)) for row in result]
            return rows

    except Exception as e:
        print(f"Error retrieving sample rows: {e}")
        return []


# Function to retrieve views
def get_views(engine):
    try:
        inspector = inspect(engine)
        views = inspector.get_view_names()
        return views
    except Exception as e:
        print(f"Error retrieving views: {e}")
        return []


def get_view_details(engine, view_name, sample_row_limit=3):
    try:
        with engine.connect() as connection:
            # Query for view definition
            view_query = text(
                f"""
                SELECT view_definition
                FROM information_schema.views
                WHERE table_name = :view_name
            """
            )
            result = connection.execute(view_query, {"view_name": view_name}).fetchone()

            # Query for columns in the view
            columns_query = text(
                f"""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = :view_name
            """
            )
            columns_result = connection.execute(
                columns_query, {"view_name": view_name}
            ).fetchall()
            # Query for sample rows
            sample_rows_query = text(f"SELECT * FROM {view_name} LIMIT :limit")
            sample_rows_result = connection.execute(
                sample_rows_query, {"limit": sample_row_limit}
            ).fetchall()
            # Fetch rows
            column_name = [row[0] for row in columns_result]
            sample_rows = [dict(zip(column_name, row)) for row in sample_rows_result]

            return {
                "definition": result[0] if result else "No definition available.",
                "columns": (
                    [
                        {"name": row[0], "type": row[1], "nullable": row[2]}
                        for row in columns_result
                    ]
                    if columns_result
                    else []
                ),
                "sample_rows": sample_rows,
            }
    except Exception as e:
        print(f"Error retrieving view details for {view_name}: {e}")
        return {}


# Function to retrieve stored procedures
def get_stored_procedures(engine):
    try:
        with engine.connect() as connection:
            query = text(
                """
                SELECT routine_name
                FROM information_schema.routines
                WHERE routine_type = 'PROCEDURE'
                AND routine_schema NOT IN ('sys', 'information_schema', 'mysql', 'performance_schema')
            """
            )
            result = connection.execute(query)
            procedures = [row[0] for row in result]
            return procedures
    except Exception as e:
        print(f"Error retrieving stored procedures: {e}")
        return []


def get_procedure_details(engine, routine_name):
    try:
        with engine.connect() as connection:

            # Query for parameters
            params_query = text(
                f"""
                SELECT parameter_name, data_type, parameter_mode
                FROM information_schema.parameters
                WHERE specific_name = :routine_name
            """
            )
            params_result = connection.execute(
                params_query, {"routine_name": routine_name}
            ).fetchall()

            return {
                "parameters": (
                    [
                        {"name": row[0], "type": row[1], "mode": row[2]}
                        for row in params_result
                    ]
                    if params_result
                    else []
                ),
            }
    except Exception as e:
        print(f"Error retrieving procedure details for {routine_name}: {e}")
        return {}


# Function to retrieve stored functions
def get_stored_functions(engine):
    try:
        with engine.connect() as connection:
            query = text(
                """
                SELECT routine_name
                FROM information_schema.routines
                WHERE routine_type = 'FUNCTION'
                AND routine_schema NOT IN ('sys', 'information_schema', 'mysql', 'performance_schema')
            """
            )
            result = connection.execute(query)
            functions = [row[0] for row in result]
            return functions
    except Exception as e:
        print(f"Error retrieving stored functions: {e}")
        return []


def get_function_details(engine, routine_name):
    try:
        with engine.connect() as connection:
            # Query for detailed information
            details_query = text(
                f"""
                SELECT data_type
                FROM information_schema.routines
                WHERE routine_name = :routine_name
            """
            )
            result = connection.execute(
                details_query, {"routine_name": routine_name}
            ).fetchone()

            # Query for parameters
            params_query = text(
                f"""
                SELECT parameter_name, data_type, parameter_mode
                FROM information_schema.parameters
                WHERE specific_name = :routine_name
            """
            )
            params_result = connection.execute(
                params_query, {"routine_name": routine_name}
            ).fetchall()

            return {
                "return_type": result[0] if result else "N/A",
                "parameters": (
                    [
                        {"name": row[0], "type": row[1], "mode": row[2]}
                        for row in params_result
                    ]
                    if params_result
                    else []
                ),
            }
    except Exception as e:
        print(f"Error retrieving function details for {routine_name}: {e}")
        return {}


# Function to format table schema as markdown
def format_table_schema_as_markdown(schema, table_name, sample_rows):
    schema_md = f"# Table Schema Documentation\n\n"
    schema_md += f"## Table: `{table_name}`\n\n"

    # Add column definitions
    schema_md += "### Column Definitions\n\n"
    schema_md += "| Column Name | Data Type | Nullable |\n"
    schema_md += "|-------------|-----------|----------|\n"
    for column in schema["columns"]:
        schema_md += f"| {column['name']} | {column['type']} | {'Yes' if column['nullable'] else 'No'} |\n"

    # Add primary key information
    if schema["primary_keys"]:
        schema_md += "\n### Primary Keys\n\n"
        schema_md += f"**Primary Keys**: {', '.join(schema['primary_keys'])}\n\n"

    # Add foreign key information
    if schema["foreign_keys"]:
        schema_md += "### Foreign Keys\n\n"
        for fk in schema["foreign_keys"]:
            schema_md += f"- `{fk['column']}` references `{fk['referred_table']}.{', '.join(fk['referred_columns'])}`\n"

    # Add sample rows
    if sample_rows:
        schema_md += "### Sample Rows\n\n"
        schema_md += "| " + " | ".join(sample_rows[0].keys()) + " |\n"
        schema_md += (
            "| "
            + " | ".join(["-" * len(key) for key in sample_rows[0].keys()])
            + " |\n"
        )
        for row in sample_rows:
            schema_md += (
                "| " + " | ".join(str(value) for value in row.values()) + " |\n"
            )
    return schema_md


# Function to format views as markdown
def format_view_details_as_markdown(view_name, details):
    markdown = f"## View Name: `{view_name}`\n\n"
    if details["columns"]:
        markdown += "### Columns\n"
        markdown += "| Name | Type | Nullable |\n"
        markdown += "|------|------|----------|\n"
        for column in details["columns"]:
            markdown += (
                f"| {column['name']} | {column['type']} | {column['nullable']} |\n"
            )

    # Add sample rows
    if details["sample_rows"]:
        markdown += "### Sample Rows\n\n"
        markdown += "| " + " | ".join(details["sample_rows"][0].keys()) + " |\n"
        markdown += (
            "| "
            + " | ".join(["-" * len(key) for key in details["sample_rows"][0].keys()])
            + " |\n"
        )
        for row in details["sample_rows"]:
            markdown += "| " + " | ".join(str(value) for value in row.values()) + " |\n"
    return markdown


# Function to format views as markdown
def format_procedure_details_as_markdown(procedure_name, details):
    markdown = f"## Procedure Name: `{procedure_name}`\n\n"
    if details["parameters"]:
        markdown += "### Parameters\n"
        markdown += "| Name | Type | Mode |\n"
        markdown += "|------|------|------|\n"
        for param in details["parameters"]:
            markdown += f"| {param['name']} | {param['type']} | {param['mode']} |\n"
    return markdown


# Function to format views as markdown
def format_function_details_as_markdown(function_name, details):
    markdown = f"##Function Name {function_name}`\n\n"
    if details["parameters"]:
        markdown += "### Parameters\n"
        markdown += "| Name | Type | Mode |\n"
        markdown += "|------|------|------|\n"
        for param in details["parameters"]:
            markdown += f"| {param['name']} | {param['type']} | {param['mode']} |\n"
    markdown += f"### Output Type\n{details['return_type']}\n"
    return markdown


# Function to save markdown file
def save_markdown_file(folder_path, file_name, content):
    try:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
        print(f"Markdown file saved at: {file_path}")
    except Exception as e:
        print(f"Error saving markdown file: {e}")


def main():
    engine = connect_to_database()

    table_names = get_table_name(engine)
    for table_name in table_names:
        schema = get_table_schema(engine, table_name)
        sample_rows = get_sample_rows(engine, table_name)

        if schema:
            # Format schema as markdown
            schema_md = format_table_schema_as_markdown(schema, table_name, sample_rows)
            # save md file

            file_name = table_name + str(".md")
            save_markdown_file(os.environ["TABLE_SCHEMA_PATH"], file_name, schema_md)
        else:
            print("Failed to retrieve table schema.")

    view_names = get_views(engine)
    for view in view_names:

        details = get_view_details(engine, view)

        if details:
            # Format schema as markdown
            schema_md = format_view_details_as_markdown(view, details)
            # save md file

            file_name = view + str(".md")
            save_markdown_file(os.environ["VIEW_SCHEMA_PATH"], file_name, schema_md)
        else:
            print("Failed to retrieve views schema.")

    procedure_names = get_stored_procedures(engine)
    for procedure in procedure_names:

        details = get_procedure_details(engine, procedure)

        if details:
            # Format schema as markdown
            schema_md = format_procedure_details_as_markdown(procedure, details)
            # save md file

            file_name = procedure + str(".md")
            save_markdown_file(
                os.environ["PROCEDURE_SCHEMA_PATH"], file_name, schema_md
            )
        else:
            print("Failed to retrieve procedures schema.")

    function_names = get_stored_functions(engine)
    for function in function_names:

        details = get_function_details(engine, function)

        if details:
            # Format schema as markdown
            schema_md = format_function_details_as_markdown(function, details)
            # save md file

            file_name = function + str(".md")
            save_markdown_file(os.environ["FUNCTION_SCHEMA_PATH"], file_name, schema_md)
        else:
            print("Failed to retrieve function schema.")


if __name__ == "__main__":
    main()

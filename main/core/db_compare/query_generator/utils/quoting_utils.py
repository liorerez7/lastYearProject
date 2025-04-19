def quote_table_name(table, db_type: str) -> str:
#TODO : currently mysql query has the shma name at the start of a coulm name
    name = table.name
    schema = table.schema

    if db_type == "mysql":
        if schema:
            return f"`{schema}`.`{name}`"
        return f"`{name}`"

    # Default to PostgreSQL style
    if schema:
        return f'"{schema}"."{name}"'
    return f'"{name}"'
# TODO :
def quote_column_name(column_name: str, db_type: str) -> str:
    """
    Quote column name appropriately.
    """
    if db_type == "mysql":
        return f"`{column_name}`"
    return f'"{column_name}"'
def get_quote_char(db_type: str):
    return '`' if db_type == "mysql" else '"'


def normalize_table_name(name: str, db_type: str):
    return name.lower() if db_type == "postgresql" else name

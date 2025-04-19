def quote_identifier(name: str, db_type: str):
    if db_type == "mysql":
        return f"`{name}`"
    return f'"{name}"'

def get_quote_char(db_type: str):
    return '`' if db_type == "mysql" else '"'

def normalize_table_name(name: str, db_type: str):
    return name.lower() if db_type == "postgresql" else name
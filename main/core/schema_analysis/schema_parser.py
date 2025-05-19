import re

def extract_table_names_from_schema(schema_path: str) -> list[str]:
    table_names = []
    create_table_pattern = re.compile(r'CREATE TABLE\s+(?:IF NOT EXISTS\s+)?[`"]?(\w+)[`"]?', re.IGNORECASE)

    with open(schema_path, 'r', encoding='utf-8') as f:
        content = f.read()
        matches = create_table_pattern.findall(content)
        table_names.extend(matches)

    return table_names

from sqlalchemy import MetaData, Table


def resolve_table_key(metadata: MetaData, name: str):
    # Try exact match first
    if name in metadata.tables:
        return metadata.tables[name]

    # Try unqualified match (e.g. "sakila.address" → "address")
    for key in metadata.tables:
        if key.split(".")[-1] == name:
            return metadata.tables[key]
    return None


def get_primary_key_column(table: Table):
    pk = list(table.primary_key.columns)
    return pk[0].name if pk else None


def get_foreign_key_column(src: Table, dst: Table):
    for fk in src.foreign_keys:
        if fk.column.table.name == dst.name:
            return fk
    return None

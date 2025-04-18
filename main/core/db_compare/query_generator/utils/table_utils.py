def get_quote_char(db_type: str) -> str:
    return "`" if db_type == "mysql" else ""


def normalize_table_name(table_name: str, db_type: str) -> str:
    if db_type == "mysql":
        return table_name.split(".")[-1]
    return table_name


def build_foreign_key_graph(metadata) -> dict:
    graph = {}
    for table_name, table in metadata.tables.items():
        graph[table_name] = []
        for fk in table.foreign_keys:
            ref_table = f"{fk.column.table.schema}.{fk.column.table.name}" if fk.column.table.schema else fk.column.table.name
            graph[table_name].append(ref_table)
    return graph


def find_deep_join_path(graph: dict, limit: int = 4) -> list:
    def dfs(node, path):
        if len(path) == limit:
            return path
        for neighbor in graph.get(node, []):
            if neighbor not in path:
                result = dfs(neighbor, path + [neighbor])
                if result:
                    return result
        return path

    for start in graph:
        path = dfs(start, [start])
        if len(path) >= 2:
            return path
    return []


def resolve_table_key(metadata, table_name: str) -> str:
    # finds the correct table key in metadata
    for k in metadata.tables:
        if k.endswith(f".{table_name}") or k == table_name:
            return k
    raise ValueError(f"❌ Table '{table_name}' not found in metadata.")


def get_foreign_key_column(metadata, from_table: str, to_table: str, db_type: str) -> str:
    from_key = resolve_table_key(metadata, from_table)
    to_key = resolve_table_key(metadata, to_table)
    table = metadata.tables[from_key]

    for fk in table.foreign_keys:
        ref_table = f"{fk.column.table.schema}.{fk.column.table.name}" if fk.column.table.schema else fk.column.table.name
        if ref_table.endswith(f".{to_table}") or ref_table == to_table:
            return fk.parent.name

    raise ValueError(f"No FK from {from_table} to {to_table}")


def get_primary_key_column(metadata, table_name: str, db_type: str) -> str:
    key = resolve_table_key(metadata, table_name)
    table = metadata.tables[key]
    pk = list(table.primary_key.columns)
    if not pk:
        raise ValueError(f"No primary key found for table: {table_name}")
    return pk[0].name

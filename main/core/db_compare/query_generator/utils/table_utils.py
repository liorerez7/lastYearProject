import networkx as nx
from sqlalchemy.schema import MetaData, Table
import random


def build_foreign_key_graph(metadata: MetaData):
    graph = nx.DiGraph()
    for table in metadata.tables.values():
        graph.add_node(table.name)
    for table in metadata.tables.values():
        for fk in table.foreign_keys:
            graph.add_edge(table.name, fk.column.table.name, fk=fk)
    return graph


def build_reverse_foreign_key_graph(metadata: MetaData):
    graph = nx.DiGraph()
    for table in metadata.tables.values():
        graph.add_node(table.name)
    for table in metadata.tables.values():
        for fk in table.foreign_keys:
            source = fk.column.table.name  # the referenced table
            target = table.name  # the table with the FK
            graph.add_edge(source, target, fk=fk)
    return graph


def find_deep_join_path(graph, limit: int = 4):
    for start_node in graph.nodes:
        for end_node in graph.nodes:
            if start_node == end_node:
                continue
            try:
                path = nx.shortest_path(graph, source=start_node, target=end_node)
                if 2 <= len(path) <= limit:
                    return path
            except nx.NetworkXNoPath:
                continue
    return None


def find_reverse_join_path(graph, limit: int = 4):
    leaves = [n for n in graph.nodes if graph.out_degree(n) == 0]
    for start in leaves:
        for target in graph.nodes:
            if start == target:
                continue
            try:
                path = nx.shortest_path(graph, source=start, target=target)
                if 2 <= len(path) <= limit:
                    return path
            except nx.NetworkXNoPath:
                continue
    return None


def get_foreign_key_column(src: Table, dst: Table):
    for fk in src.foreign_keys:
        if fk.column.table.name == dst.name:
            return fk
    return None


def get_primary_key_column(table: Table):
    pk = list(table.primary_key.columns)
    return pk[0].name if pk else None


def quote_identifier(name: str, db_type: str):
    if db_type == "mysql":
        return f"`{name}`"
    return f'"{name}"'


def get_quote_char(db_type: str):
    return '`' if db_type == "mysql" else '"'


def resolve_table_key(metadata: MetaData, name: str):
    return metadata.tables[name] if name in metadata.tables else None


def normalize_table_name(name: str, db_type: str):
    return name.lower() if db_type == "postgresql" else name


def get_groupable_column(self, columns, table):
    for col in columns:
        if col not in table.primary_key.columns:
            return col
    return None


def get_aggregatable_column(self, columns):
    for col in columns:
        if hasattr(col.type, "python_type"):
            try:
                if issubclass(col.type.python_type, (int, float)):
                    return col
            except NotImplementedError:
                continue
    return None


def get_filterable_column(table):
    for col in table.columns:
        if hasattr(col.type, "python_type"):
            try:
                py_type = col.type.python_type
                if py_type in (int, float, str):
                    return col
            except NotImplementedError:
                continue
    return None


def generate_condition(column):
    try:
        py_type = column.type.python_type
    except NotImplementedError:
        return "= 1"

    if py_type == int:
        return f"> {random.randint(1, 10)}"
    elif py_type == float:
        return f"> {round(random.uniform(1.0, 10.0), 2)}"
    elif py_type == str:
        return f"LIKE '%a%'"
    else:
        return "= 1"

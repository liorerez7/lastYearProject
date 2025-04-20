import networkx as nx
from sqlalchemy.schema import MetaData

from typing import Optional


def build_foreign_key_graph(metadata: MetaData):
    graph = nx.DiGraph()
    for table in metadata.tables.values():
        graph.add_node(table.fullname)  # safer with schema

    for table in metadata.tables.values():
        for fk in table.foreign_keys:
            source = table.fullname
            target = fk.column.table.fullname
            graph.add_edge(source, target, fk=fk)
            graph.add_edge(target, source, fk=fk)  # bidirectional
    return graph


def build_reverse_foreign_key_graph(metadata: MetaData):
    graph = nx.DiGraph()
    for table in metadata.tables.values():
        graph.add_node(table.name)
    for table in metadata.tables.values():
        for fk in table.foreign_keys:
            source = fk.column.table.name
            target = table.name
            graph.add_edge(source, target, fk=fk)
    return graph


def find_deep_join_path(
    graph: nx.DiGraph,
    selector: int = 0,
    min_length: int = 2,
    max_length: Optional[int] = None,
    longest: bool = False
):
    nodes = sorted(graph.nodes)
    if not nodes:
        return None

    best_path = None

    if longest:
        # Try all pairs and return the longest valid path
        for start_node in nodes:
            for end_node in nodes:
                if start_node == end_node:
                    continue
                try:
                    path = nx.shortest_path(graph, source=start_node, target=end_node)

                    if len(path) >= min_length:
                        if max_length is None or len(path) <= max_length:
                            if not best_path or len(path) > len(best_path):
                                best_path = path

                except nx.NetworkXNoPath:
                    continue
        return best_path

    # Else: use selector-based logic
    start_index = selector % len(nodes)
    start_node = nodes[start_index]

    for end_node in nodes:
        if start_node == end_node:
            continue
        try:
            path = nx.shortest_path(graph, source=start_node, target=end_node)

            if len(path) >= min_length:
                if max_length is None or len(path) <= max_length:
                    return path

        except nx.NetworkXNoPath:
            continue

    return None


def find_reverse_join_path(graph, selector: int = 0, limit: int = 4):
    leaves = sorted([n for n in graph.nodes if graph.out_degree(n) == 0])
    if not leaves:
        return None

    selected_leaf = leaves[selector % len(leaves)]

    for target in sorted(graph.nodes):
        if selected_leaf == target:
            continue
        try:
            path = nx.shortest_path(graph, source=selected_leaf, target=target)
            if 2 <= len(path) <= limit:
                return path
        except nx.NetworkXNoPath:
            continue
    return None

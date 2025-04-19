from main.core.db_compare.query_generator.base_query_strategy import BaseQueryStrategy
from main.core.db_compare.query_generator.utils.table_utils import (
    build_reverse_foreign_key_graph,
    find_reverse_join_path,
    get_foreign_key_column,
    quote_identifier,
    resolve_table_key,
)
from sqlalchemy.schema import MetaData

class ReverseJoinStrategy(BaseQueryStrategy):
    def generate_query(self, schema_metadata: MetaData, db_type: str) -> str:
        graph = build_reverse_foreign_key_graph(schema_metadata)
        path = find_reverse_join_path(graph, limit=4)

        if not path:
            return "-- No reverse join path found"

        tables = [resolve_table_key(schema_metadata, name) for name in path]
        base_table = quote_identifier(tables[0].name, db_type)
        from_clause = f"FROM {base_table}"
        joins = []

        for i in range(1, len(tables)):
            current = tables[i]
            previous = tables[i - 1]
            fk = get_foreign_key_column(current, previous)
            if not fk:
                continue
            join = (
                f"JOIN {quote_identifier(current.name, db_type)} ON "
                f"{quote_identifier(current.name, db_type)}.{quote_identifier(fk.parent.name, db_type)} = "
                f"{quote_identifier(previous.name, db_type)}.{quote_identifier(fk.column_keys[0], db_type)}"
            )
            joins.append(join)

        select_clause = "SELECT *"
        query = f"{select_clause}\n{from_clause}\n" + "\n".join(joins) + "\nLIMIT 100;"
        return query

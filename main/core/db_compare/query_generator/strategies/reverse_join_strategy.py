from main.core.db_compare.query_generator.strategies.base_query_strategy import BaseQueryStrategy
from main.core.db_compare.query_generator.utils.table_access_utils import resolve_table_key
from main.core.db_compare.query_generator.utils.quoting_utils import quote_table_name
from main.core.db_compare.query_generator.utils.schema_graph_utils import (
    build_reverse_foreign_key_graph,
    find_reverse_join_path
)


class ReverseJoinStrategy(BaseQueryStrategy):
    def generate_query(self, schema_metadata, db_type: str, selector: int = None) -> str:
        selector = self.ensure_selector(selector)
        graph = build_reverse_foreign_key_graph(schema_metadata)
        path = find_reverse_join_path(graph, selector=selector, limit=4)

        if not path:
            return "-- No reverse join path found"

        tables = [resolve_table_key(schema_metadata, name) for name in path]
        base_table = quote_table_name(tables[0].name, db_type)
        joins = []

        for i in range(1, len(tables)):
            curr = tables[i]
            prev = tables[i - 1]
            fk = next((fk for fk in curr.foreign_keys if fk.column.table.name == prev.name), None)
            if fk:
                joins.append(
                    f"JOIN {quote_table_name(curr.name, db_type)} ON "
                    f"{quote_table_name(curr.name, db_type)}.{quote_table_name(fk.parent.name, db_type)} = "
                    f"{quote_table_name(prev.name, db_type)}.{quote_table_name(fk.column_keys[0], db_type)}"
                )

        return f"SELECT *\nFROM {base_table}\n" + "\n".join(joins) + "\nLIMIT 100;"

from main.core.db_compare.query_generator.strategies.base_query_strategy import BaseQueryStrategy
from main.core.db_compare.query_generator.utils.table_access_utils import resolve_table_key
from main.core.db_compare.query_generator.utils.quoting_utils import quote_identifier
from main.core.db_compare.query_generator.utils.schema_graph_utils import (
    build_foreign_key_graph,
    find_deep_join_path
)


class DeepJoinQueryStrategy(BaseQueryStrategy):
    def generate_query(self, schema_metadata, db_type: str, selector: int = None) -> str:
        selector = self.ensure_selector(selector)
        graph = build_foreign_key_graph(schema_metadata)
        path = find_deep_join_path(graph, selector=selector, limit=4)

        if not path:
            return None  # No path found

        tables = [resolve_table_key(schema_metadata, name) for name in path]
        if None in tables:
            return None  # Table resolution failed

        base_table = quote_identifier(tables[0].name, db_type)
        joins = []

        for i in range(1, len(tables)):
            prev = tables[i - 1]
            curr = tables[i]
            fk = None
            direction = None

            # Try FK: curr → prev
            for candidate_fk in curr.foreign_keys:
                if candidate_fk.column.table == prev:
                    fk = candidate_fk
                    direction = "forward"
                    break

            # Try FK: prev → curr (reverse)
            if not fk:
                for candidate_fk in prev.foreign_keys:
                    if candidate_fk.column.table == curr:
                        fk = candidate_fk
                        direction = "reverse"
                        break

            if fk:
                if direction == "forward":
                    joins.append(
                        f"JOIN {quote_identifier(curr.name, db_type)} ON "
                        f"{quote_identifier(curr.name, db_type)}.{quote_identifier(fk.parent.name, db_type)} = "
                        f"{quote_identifier(prev.name, db_type)}.{quote_identifier(fk.column.name, db_type)}"
                    )
                else:
                    joins.append(
                        f"JOIN {quote_identifier(curr.name, db_type)} ON "
                        f"{quote_identifier(prev.name, db_type)}.{quote_identifier(fk.parent.name, db_type)} = "
                        f"{quote_identifier(curr.name, db_type)}.{quote_identifier(fk.column.name, db_type)}"
                    )
            else:
                return None  # Could not find valid FK

        return f"SELECT *\nFROM {base_table}\n" + "\n".join(joins) + "\nLIMIT 100;"

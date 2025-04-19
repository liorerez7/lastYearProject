from typing import Optional
from main.core.db_compare.query_generator.strategies.base_query_strategy import BaseQueryStrategy
from main.core.db_compare.query_generator.utils.table_access_utils import resolve_table_key
from main.core.db_compare.query_generator.utils.quoting_utils import quote_table_name
from main.core.db_compare.query_generator.utils.schema_graph_utils import (
    build_foreign_key_graph,
    find_deep_join_path
)


class DeepJoinQueryStrategy(BaseQueryStrategy):
    """
    Strategy to generate SQL queries using deep joins across multiple tables
    via foreign key paths.

    Args:
        min_join_size (int): Minimum number of tables to include in the join path.
        max_join_size (Optional[int]): Maximum number of tables to include.
        longest (bool): If True, finds the longest valid join path regardless of selector.
    """

    def __init__(self, min_join_size: int = 2, max_join_size: Optional[int] = None, longest: bool = False):
        self.min_join_size = min_join_size
        self.max_join_size = max_join_size
        self.longest = longest

    def generate_query(self, schema_metadata, db_type: str, selector: int = None) -> Optional[str]:
        selector = self.ensure_selector(selector)
        graph = build_foreign_key_graph(schema_metadata)
        path = find_deep_join_path(
            graph,
            selector=selector,
            min_length=self.min_join_size,
            max_length=self.max_join_size,
            longest=self.longest
        )

        if not path:
            return None  # No path found

        tables = [resolve_table_key(schema_metadata, name) for name in path]
        if None in tables:
            return None  # Table resolution failed

        base_table = quote_table_name(tables[0].name, db_type)
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
                        f"JOIN {quote_table_name(curr.name, db_type)} ON "
                        f"{quote_table_name(curr.name, db_type)}.{quote_table_name(fk.parent.name, db_type)} = "
                        f"{quote_table_name(prev.name, db_type)}.{quote_table_name(fk.column.name, db_type)}"
                    )
                else:
                    joins.append(
                        f"JOIN {quote_table_name(curr.name, db_type)} ON "
                        f"{quote_table_name(prev.name, db_type)}.{quote_table_name(fk.parent.name, db_type)} = "
                        f"{quote_table_name(curr.name, db_type)}.{quote_table_name(fk.column.name, db_type)}"
                    )
            else:
                return None  # Could not find valid FK

        return f"SELECT *\nFROM {base_table}\n" + "\n".join(joins) + "\nLIMIT 100;"

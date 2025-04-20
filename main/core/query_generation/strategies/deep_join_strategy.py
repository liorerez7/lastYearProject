from typing import Optional
from main.core.query_generation.strategies.base_query_strategy import BaseQueryStrategy
from main.core.query_generation.utils.table_access_utils import resolve_table_key
from main.core.query_generation.utils.quoting_utils import quote_table_name, quote_column_name
from main.core.query_generation.utils.schema_graph_utils import (
    build_foreign_key_graph,
    find_deep_join_path
)


class DeepJoinQueryStrategy(BaseQueryStrategy):
    def __init__(self, min_join_size: int = 2, max_join_size: Optional[int] = None, longest: bool = False):
        self.min_join_size = min_join_size
        self.max_join_size = max_join_size
        self.longest = longest

    def generate_query(self, schema_metadata, db_type: str, selector: int) -> Optional[str]:
        graph = build_foreign_key_graph(schema_metadata)
        path = find_deep_join_path(
            graph,
            selector=selector,
            min_length=self.min_join_size,
            max_length=self.max_join_size,
            longest=self.longest
        )
        if selector is None:
            raise ValueError("❌ selector must be explicitly provided for DeepJoinQueryStrategy.")

        if not path:
            return None  # No path found

        tables = [resolve_table_key(schema_metadata, name) for name in path]
        if None in tables:
            return None  # Table resolution failed

        base_table = quote_table_name(tables[0], db_type)
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
                curr_q = quote_table_name(curr, db_type)
                prev_q = quote_table_name(prev, db_type)
                parent_col = quote_column_name(fk.parent.name, db_type)
                ref_col = quote_column_name(fk.column.name, db_type)

                if direction == "forward":
                    joins.append(
                        f"JOIN {curr_q} ON {curr_q}.{parent_col} = {prev_q}.{ref_col}"
                    )
                else:
                    joins.append(
                        f"JOIN {curr_q} ON {prev_q}.{parent_col} = {curr_q}.{ref_col}"
                    )
            else:
                return None  # Could not find valid FK

        return f"SELECT *\nFROM {base_table}\n" + "\n".join(joins) + "\nLIMIT 100;"

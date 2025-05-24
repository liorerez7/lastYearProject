from typing import Optional

from main.core.query_generation.strategies.base_query_strategy import BaseQueryStrategy
from main.core.query_generation.utils.quoting_utils import (
    quote_table_name,
    quote_column_name,
    get_quote_char,
)
from main.core.query_generation.utils.schema_graph_utils import (
    build_reverse_foreign_key_graph,
    find_reverse_join_path,
)
from main.core.query_generation.utils.table_access_utils import resolve_table_key

## This class is not working on this data base!
## it might work in general, but it wasnt checked. because on this particular database it doesnt work
## maybe because of the fact that the foreign keys are not set up in a way it can be used


class ReverseJoinQueryStrategy(BaseQueryStrategy):
    def __init__(self, limit: int = 8):
        super().__init__()
        self.limit = limit

    def generate_query(
        self, schema_metadata, db_type: str, selector: int = None
    ) -> Optional[str]:
        if selector is None:
            raise ValueError("❌ selector must be explicitly provided for ReverseJoinQueryStrategy.")

        # 1) build the “reverse” FK graph and pick a path
        graph = build_reverse_foreign_key_graph(schema_metadata)
        path = find_reverse_join_path(graph, selector=selector, limit=self.limit)
        if not path:
            return None

        # 2) turn each node name into a SQLAlchemy Table object
        tables = [resolve_table_key(schema_metadata, name) for name in path]
        if None in tables:
            return None

        # 3) quote the base table
        base = quote_table_name(tables[0], db_type)

        # 4) for each hop, find the FK and emit a JOIN
        joins = []
        for prev, curr in zip(tables, tables[1:]):
            # try “curr → prev” first
            fk = next(
                (fk for fk in curr.foreign_keys if fk.column.table == prev),
                None
            )
            if not fk:
                # otherwise “prev → curr”
                fk = next(
                    (fk for fk in prev.foreign_keys if fk.column.table == curr),
                    None
                )
                if not fk:
                    return None
                # reverse direction: prev.parent = curr.pk
                joins.append(
                    f"JOIN {quote_table_name(curr, db_type)} "
                    f"ON {quote_table_name(prev, db_type)}."
                    f"{quote_column_name(fk.parent.name, db_type)} = "
                    f"{quote_table_name(curr, db_type)}."
                    f"{quote_column_name(fk.column.name, db_type)}"
                )
            else:
                # forward direction: curr.parent = prev.pk
                joins.append(
                    f"JOIN {quote_table_name(curr, db_type)} "
                    f"ON {quote_table_name(curr, db_type)}."
                    f"{quote_column_name(fk.parent.name, db_type)} = "
                    f"{quote_table_name(prev, db_type)}."
                    f"{quote_column_name(fk.column.name, db_type)}"
                )

        return "SELECT *\nFROM " + base + "\n" + "\n".join(joins) + "\nLIMIT 100;"

from main.core.db_compare.query_generator.base_query_strategy import BaseQueryStrategy

from sqlalchemy.schema import MetaData
import random
from main.core.db_compare.query_generator.utils.table_utils import (
    resolve_table_key,
    quote_identifier,
    get_groupable_column,
    get_aggregatable_column,
)
class AggregationQueryStrategy(BaseQueryStrategy):
    def generate_query(self, schema_metadata: MetaData, db_type: str) -> str:
        # Pick a random table
        table_names = list(schema_metadata.tables.keys())
        if not table_names:
            return "-- No tables available"

        random.shuffle(table_names)
        for name in table_names:
            table = resolve_table_key(schema_metadata, name)
            if table is None:
                continue

            columns = list(table.columns)
            if len(columns) < 2:
                continue

            # Try to find a groupable and aggregatable column
            group_col = get_groupable_column(columns, table)
            agg_col = get_aggregatable_column(columns)

            if group_col and agg_col:
                table_name = quote_identifier(table.name, db_type)
                group_col_name = quote_identifier(group_col.name, db_type)
                agg_col_name = quote_identifier(agg_col.name, db_type)
                return (
                    f"SELECT {group_col_name}, COUNT({agg_col_name})\n"
                    f"FROM {table_name}\n"
                    f"GROUP BY {group_col_name}\n"
                    f"LIMIT 100;"
                )

        return "-- No suitable aggregation found"


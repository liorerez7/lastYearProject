from main.core.db_compare.query_generator.strategies.base_query_strategy import BaseQueryStrategy
from main.core.db_compare.query_generator.utils.table_access_utils import resolve_table_key
from main.core.db_compare.query_generator.utils.column_analysis_utils import (
    get_groupable_column,
    get_aggregatable_column
)
from main.core.db_compare.query_generator.utils.quoting_utils import quote_identifier


class AggregationQueryStrategy(BaseQueryStrategy):
    def generate_query(self, schema_metadata, db_type: str, selector: int = None) -> str:
        selector = self.ensure_selector(selector)
        table_names = sorted(schema_metadata.tables.keys())
        if not table_names:
            return "SELECT 1;"

        table = resolve_table_key(schema_metadata, table_names[selector % len(table_names)])
        columns = list(table.columns)

        if len(columns) < 2:
            return f"SELECT * FROM {quote_identifier(table.name, db_type)} LIMIT 100;"

        group_col = get_groupable_column(columns,table, selector)
        agg_col = get_aggregatable_column(columns, selector)

        if group_col and agg_col:
            return (
                f"SELECT {quote_identifier(group_col.name, db_type)}, COUNT({quote_identifier(agg_col.name, db_type)})\n"
                f"FROM {quote_identifier(table.name, db_type)}\n"
                f"GROUP BY {quote_identifier(group_col.name, db_type)}\n"
                f"LIMIT 100;"
            )
        else:
            return f"SELECT * FROM {quote_identifier(table.name, db_type)} LIMIT 100;"


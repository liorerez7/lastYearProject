from main.core.db_compare.query_generator.strategies.base_query_strategy import BaseQueryStrategy
from main.core.db_compare.query_generator.utils.table_access_utils import resolve_table_key
from main.core.db_compare.query_generator.utils.column_analysis_utils import (
    get_filterable_column,
    generate_condition
)
from main.core.db_compare.query_generator.utils.quoting_utils import quote_table_name


class FilteredQueryStrategy(BaseQueryStrategy):
    def generate_query(self, schema_metadata, db_type: str, selector: int = None) -> str:
        selector = self.ensure_selector(selector)
        table_names = sorted(schema_metadata.tables.keys())
        if not table_names:
            return "SELECT 1;"

        table_index = selector % len(table_names)
        table = resolve_table_key(schema_metadata, table_names[table_index])
        filter_col = get_filterable_column(table, selector)
        table_id = quote_table_name(table.name, db_type)

        if filter_col:
            col_id = quote_table_name(filter_col.name, db_type)
            condition = generate_condition(filter_col, selector)
            return f"SELECT * FROM {table_id} WHERE {col_id} {condition} LIMIT 100;"
        else:
            return f"SELECT * FROM {table_id} LIMIT 100;"

from main.core.query_generation.strategies.base_query_strategy import BaseQueryStrategy
from main.core.query_generation.utils.table_access_utils import resolve_table_key
from main.core.query_generation.utils.quoting_utils import quote_table_name, quote_column_name

class FilteredQueryStrategy(BaseQueryStrategy):
    def generate_query(self, schema_metadata, db_type: str, selector: int = None) -> str:
        table_names = sorted(schema_metadata.tables.keys())
        if not table_names:
            return "SELECT 1;"

        if selector is None:
            raise ValueError("❌ selector must be explicitly provided for FilteredQueryStrategy.")

        table_index = selector % len(table_names)
        table = resolve_table_key(schema_metadata, table_names[table_index])
        table_name = quote_table_name(table, db_type)

        column = quote_column_name(list(table.columns)[0].name, db_type)
        return f"SELECT * FROM {table_name} WHERE {column} IS NOT NULL LIMIT {self.LIMIT};"

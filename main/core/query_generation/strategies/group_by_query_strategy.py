from main.core.query_generation.strategies.base_query_strategy import BaseQueryStrategy
from main.core.query_generation.utils.table_access_utils import resolve_table_key
from main.core.query_generation.utils.quoting_utils import quote_table_name, quote_column_name


class GroupByQueryStrategy(BaseQueryStrategy):
    def generate_query(self, schema_metadata, db_type: str, selector: int = None) -> str:
        table_names = sorted(schema_metadata.tables.keys())
        if not table_names:
            return "SELECT 1;"

        if selector is None:
            raise ValueError("❌ selector must be explicitly provided for GroupByQueryStrategy.")

        table_index = selector % len(table_names)
        table = resolve_table_key(schema_metadata, table_names[table_index])
        table_name = quote_table_name(table, db_type)

        columns = list(table.columns)
        if len(columns) < 2:
            return None  

        col1 = quote_column_name(columns[0].name, db_type)
        col2 = quote_column_name(columns[1].name, db_type)

        return f"SELECT {col1}, {col2}, COUNT(*) FROM {table_name} GROUP BY {col1}, {col2} LIMIT {self.LIMIT};"

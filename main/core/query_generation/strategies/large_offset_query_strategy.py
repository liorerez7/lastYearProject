# large_offset_query_strategy.py
from main.core.query_generation.strategies.base_query_strategy import BaseQueryStrategy
from main.core.query_generation.utils.table_access_utils import resolve_table_key
from main.core.query_generation.utils.quoting_utils import quote_table_name

class LargeOffsetQueryStrategy(BaseQueryStrategy):

    def generate_query(self, schema_metadata, db_type: str, selector: int = None) -> str:
        employees = quote_table_name(resolve_table_key(schema_metadata, "employees"), db_type)
        return (f"SELECT emp_no, first_name, last_name "
                f"FROM {employees} "
                f"ORDER BY emp_no "
                f"LIMIT {self.LIMIT} OFFSET {self.OFFSET};")

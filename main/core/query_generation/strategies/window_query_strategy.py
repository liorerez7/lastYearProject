# window_query_strategy.py
from main.core.query_generation.strategies.base_query_strategy import BaseQueryStrategy
from main.core.query_generation.utils.table_access_utils import resolve_table_key
from main.core.query_generation.utils.quoting_utils import quote_table_name

class WindowQueryStrategy(BaseQueryStrategy):

    def generate_query(self, schema_metadata, db_type: str, selector: int = None) -> str:
        salaries = quote_table_name(resolve_table_key(schema_metadata, "salaries"), db_type)
        return (f"SELECT emp_no, salary, "
                f"ROW_NUMBER() OVER (PARTITION BY emp_no ORDER BY to_date DESC) AS rn "
                f"FROM {salaries} "
                f"WHERE salary > 70000 "
                f"LIMIT {self.LIMIT};")

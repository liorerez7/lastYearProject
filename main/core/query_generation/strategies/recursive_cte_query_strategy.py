# recursive_cte_query_strategy.py
from main.core.query_generation.strategies.base_query_strategy import BaseQueryStrategy
from main.core.query_generation.utils.table_access_utils import resolve_table_key
from main.core.query_generation.utils.quoting_utils import quote_table_name, quote_column_name

class RecursiveCTEQueryStrategy(BaseQueryStrategy):
    def generate_query(self, schema_metadata, db_type: str, selector: int = None) -> str:
        dept_emp = quote_table_name(resolve_table_key(schema_metadata, "dept_emp"), db_type)
        emp_no   = quote_column_name("emp_no",  db_type)
        dept_no  = quote_column_name("dept_no", db_type)

        return (
            f"WITH RECURSIVE r AS ( "
            f"  SELECT {emp_no}, {dept_no}, 1 AS lvl "
            f"  FROM {dept_emp} "
            f"  WHERE {dept_no} = 'd001' "
            f"  UNION ALL "
            f"  SELECT d.{emp_no}, d.{dept_no}, r.lvl + 1 "
            f"  FROM {dept_emp} d "
            f"  JOIN r ON d.{emp_no} = r.{emp_no} "
            f"  WHERE r.lvl < 4 "                      # ← עומק 3 בלבד
            f") "
            f"SELECT COUNT(*) FROM r "
            f"LIMIT {self.LIMIT};"
        )

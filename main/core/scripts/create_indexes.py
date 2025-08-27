# from sqlalchemy import text
# from main.core.schema_analysis.connection.db_connector import DBConnector
#
# MYSQL_INDEX_QUERIES = [
#     ("employees", "idx_emp_no_employees", "CREATE INDEX idx_emp_no_employees ON employees(emp_no);"),
#     ("salaries", "idx_emp_no_salaries", "CREATE INDEX idx_emp_no_salaries ON salaries(emp_no);"),
#     ("dept_emp", "idx_emp_no_dept_emp", "CREATE INDEX idx_emp_no_dept_emp ON dept_emp(emp_no);"),
#     ("dept_emp", "idx_dept_no_dept_emp", "CREATE INDEX idx_dept_no_dept_emp ON dept_emp(dept_no);"),
#     ("departments", "idx_dept_no_departments", "CREATE INDEX idx_dept_no_departments ON departments(dept_no);"),
#     ("employees", "idx_birth_date_employees", "CREATE INDEX idx_birth_date_employees ON employees(birth_date);"),
#     ("employees", "idx_emp_birth_employees", "CREATE INDEX idx_emp_birth_employees ON employees(emp_no, birth_date);"),
#     ("salaries", "idx_emp_to_date", "CREATE INDEX idx_emp_to_date ON salaries(emp_no, to_date);"),
#     ("salaries", "idx_emp_salary", "CREATE INDEX idx_emp_salary ON salaries(emp_no, salary);"),
#     ("dept_emp", "idx_dept_emp_combo", "CREATE INDEX idx_dept_emp_combo ON dept_emp(emp_no, dept_no, from_date);"),
#     ("salaries", "idx_salaries_emp_to_date", "CREATE INDEX idx_salaries_emp_to_date ON salaries(emp_no, to_date);"),
#     ("titles", "idx_titles_emp_no", "CREATE INDEX idx_titles_emp_no ON titles(emp_no);"),
#     ("salaries", "idx_salary_to_date", "CREATE INDEX idx_salary_to_date ON salaries(salary, to_date);"),
#     ("salaries", "idx_window_salary_to_date_emp", "CREATE INDEX idx_window_salary_to_date_emp ON salaries(salary, to_date DESC, emp_no);"),
#     ("salaries", "idx_window_emp_to_date_salary", "CREATE INDEX idx_window_emp_to_date_salary ON salaries(emp_no, to_date DESC, salary);")
# ]
#
# PG_INDEX_QUERIES = [
#     ("employees", "idx_emp_no_employees", 'CREATE INDEX idx_emp_no_employees ON "extendedEmp".employees(emp_no);'),
#     ("salaries", "idx_emp_no_salaries", 'CREATE INDEX idx_emp_no_salaries ON "extendedEmp".salaries(emp_no);'),
#     ("dept_emp", "idx_emp_no_dept_emp", 'CREATE INDEX idx_emp_no_dept_emp ON "extendedEmp".dept_emp(emp_no);'),
#     ("dept_emp", "idx_dept_no_dept_emp", 'CREATE INDEX idx_dept_no_dept_emp ON "extendedEmp".dept_emp(dept_no);'),
#     ("departments", "idx_dept_no_departments", 'CREATE INDEX idx_dept_no_departments ON "extendedEmp".departments(dept_no);'),
#     ("employees", "idx_birth_date_employees", 'CREATE INDEX idx_birth_date_employees ON "extendedEmp".employees(birth_date);'),
#     ("employees", "idx_emp_birth_employees", 'CREATE INDEX idx_emp_birth_employees ON "extendedEmp".employees(emp_no, birth_date);'),
#     ("salaries", "idx_emp_to_date", 'CREATE INDEX IF NOT EXISTS idx_emp_to_date ON "extendedEmp".salaries(emp_no, to_date);'),
#     ("salaries", "idx_emp_salary", 'CREATE INDEX IF NOT EXISTS idx_emp_salary ON "extendedEmp".salaries(emp_no, salary);'),
#     ("dept_emp", "idx_dept_emp_combo", 'CREATE INDEX idx_dept_emp_combo ON "extendedEmp".dept_emp(emp_no, dept_no, from_date);'),
#     ("salaries", "idx_salaries_emp_to_date", 'CREATE INDEX idx_salaries_emp_to_date ON "extendedEmp".salaries(emp_no, to_date);'),
#     ("titles", "idx_titles_emp_no", 'CREATE INDEX idx_titles_emp_no ON "extendedEmp".titles(emp_no);'),
#     ("salaries", "idx_salary_to_date", 'CREATE INDEX idx_salary_to_date ON "extendedEmp".salaries(salary, to_date);'),
#     ("salaries", "idx_window_salary_to_date_emp", 'CREATE INDEX idx_window_salary_to_date_emp ON "extendedEmp".salaries(salary, to_date DESC, emp_no);')
# ]
#
#
# def create_indexes_if_missing(db_type: str):
#     print(f"\n🔧 Checking indexes for {db_type.upper()}...")
#     engine, _ = DBConnector(db_type).connect("mydb")
#
#     if db_type == "mysql":
#         index_queries = MYSQL_INDEX_QUERIES
#         check_index_sql = """
#             SELECT COUNT(*)
#             FROM information_schema.statistics
#             WHERE table_schema = DATABASE()
#               AND table_name = :table
#               AND index_name = :index;
#         """
#     elif db_type == "postgres":
#         index_queries = PG_INDEX_QUERIES
#         check_index_sql = """
#             SELECT COUNT(*)
#             FROM pg_indexes
#             WHERE schemaname = 'finalEmp'
#               AND tablename = :table
#               AND indexname = :index;
#         """
#     else:
#         raise ValueError("Unsupported DB type")
#
#     with engine.connect() as conn:
#         for table, index_name, create_sql in index_queries:
#             result = conn.execute(text(check_index_sql), {"table": table, "index": index_name})
#             exists = result.scalar()
#
#             if exists:
#                 print(f"✅ Index `{index_name}` already exists on `{table}` [{db_type}]")
#             else:
#                 print(f"📌 Creating index `{index_name}` on `{table}` [{db_type}]")
#                 conn.execute(text(create_sql))
#
#     print(f"✅ Done for {db_type.upper()}\n")
#
#
# if __name__ == "__main__":
#     create_indexes_if_missing("mysql")
#     create_indexes_if_missing("postgres")


# index_setup.py

from typing import List, Tuple, Dict
from sqlalchemy import text
from main.core.schema_analysis.connection.db_connector import DBConnector

# הסכמה הלוגית שני המנועים ב-POC
SCHEMA_NAME = "mydb"

# פורמט: (table_name, index_name, create_sql)
# שים לב: ב-MySQL אנחנו על DB 'mydb' כבר, לכן לא צריך לציין סכימה.
MYSQL_INDEX_QUERIES: List[Tuple[str, str, str]] = [
    # --- salaries (גדולה) ---
    ("salaries", "idx_salaries_emp_to_date",
     "CREATE INDEX idx_salaries_emp_to_date ON salaries(emp_no, to_date)"),
    # אופציונלי (אם יש חלונות/מיון לפי תאריך/שכר):
    ("salaries", "idx_salaries_emp_to_date_salary",
     "CREATE INDEX idx_salaries_emp_to_date_salary ON salaries(emp_no, to_date, salary)"),

    # --- dept_emp (צמתי join נפוצים) ---
    ("dept_emp", "idx_dept_emp_emp_no",
     "CREATE INDEX idx_dept_emp_emp_no ON dept_emp(emp_no)"),
    ("dept_emp", "idx_dept_emp_dept_no",
     "CREATE INDEX idx_dept_emp_dept_no ON dept_emp(dept_no)"),
    ("dept_emp", "idx_dept_emp_combo",
     "CREATE INDEX idx_dept_emp_combo ON dept_emp(emp_no, dept_no, from_date)"),

    # --- titles ---
    ("titles", "idx_titles_emp_no",
     "CREATE INDEX idx_titles_emp_no ON titles(emp_no)"),

    # --- employees (לבדיקות מתקדמות אפשרי) ---
    ("employees", "idx_employees_birth_date",
     "CREATE INDEX idx_employees_birth_date ON employees(birth_date)")
]

# ב-Postgres חייבים לציין סכימה מפורשת ("mydb")
PG_INDEX_QUERIES: List[Tuple[str, str, str]] = [
    # --- salaries (גדולה) ---
    ("salaries", "idx_salaries_emp_to_date",
     'CREATE INDEX IF NOT EXISTS idx_salaries_emp_to_date ON "mydb".salaries(emp_no, to_date)'),
    # אופציונלי (אם יש חלונות/מיון לפי תאריך/שכר):
    ("salaries", "idx_salaries_emp_to_date_salary",
     'CREATE INDEX IF NOT EXISTS idx_salaries_emp_to_date_salary ON "mydb".salaries(emp_no, to_date, salary)'),

    # --- dept_emp ---
    ("dept_emp", "idx_dept_emp_emp_no",
     'CREATE INDEX IF NOT EXISTS idx_dept_emp_emp_no ON "mydb".dept_emp(emp_no)'),
    ("dept_emp", "idx_dept_emp_dept_no",
     'CREATE INDEX IF NOT EXISTS idx_dept_emp_dept_no ON "mydb".dept_emp(dept_no)'),
    ("dept_emp", "idx_dept_emp_combo",
     'CREATE INDEX IF NOT EXISTS idx_dept_emp_combo ON "mydb".dept_emp(emp_no, dept_no, from_date)'),

    # --- titles ---
    ("titles", "idx_titles_emp_no",
     'CREATE INDEX IF NOT EXISTS idx_titles_emp_no ON "mydb".titles(emp_no)'),

    # --- employees (לבדיקות מתקדמות אפשרי) ---
    ("employees", "idx_employees_birth_date",
     'CREATE INDEX IF NOT EXISTS idx_employees_birth_date ON "mydb".employees(birth_date)')
]


def _mysql_check_sql() -> str:
    # מחפש אינדקס בשם מסוים על טבלה בסכימה הנוכחית (DATABASE())
    return """
        SELECT COUNT(*)
        FROM information_schema.statistics
        WHERE table_schema = DATABASE()
          AND table_name = :table
          AND index_name = :index
    """


def _pg_check_sql() -> str:
    # מחפש אינדקס בשם מסוים על טבלה בסכימה ספציפית
    return """
        SELECT COUNT(*)
        FROM pg_indexes
        WHERE schemaname = :schema
          AND tablename = :table
        AND indexname = :index
    """


def create_indexes_if_missing(db_type: str, schema: str = SCHEMA_NAME):
    db_type = db_type.lower()
    print(f"\n🔧 Checking indexes for {db_type.upper()} (schema='{schema}')...")

    # התחברות לסכימה הנכונה לרפלקציה (לא חובה ליצירה – כן שימושי ל-ANALYZE)
    engine, _ = DBConnector(db_type).connect(schema)

    if db_type == "mysql":
        index_queries = MYSQL_INDEX_QUERIES
        check_sql = _mysql_check_sql()
        analyze_stmt_templates: Dict[str, str] = {
            # MySQL 8:
            "salaries":  "ANALYZE TABLE salaries",
            "dept_emp":  "ANALYZE TABLE dept_emp",
            "titles":    "ANALYZE TABLE titles",
            "employees": "ANALYZE TABLE employees",
        }
    elif db_type == "postgres":
        index_queries = PG_INDEX_QUERIES
        check_sql = _pg_check_sql()
        analyze_stmt_templates = {
            # Postgres:
            "salaries":  'ANALYZE "mydb".salaries',
            "dept_emp":  'ANALYZE "mydb".dept_emp',
            "titles":    'ANALYZE "mydb".titles',
            "employees": 'ANALYZE "mydb".employees',
        }
    else:
        raise ValueError("Unsupported DB type")

    touched_tables = set()

    # חשוב: DDL תחת engine.begin() → מבטיח COMMIT
    with engine.begin() as conn:
        for table, index_name, create_sql in index_queries:
            params = {"table": table, "index": index_name}
            if db_type == "postgres":
                params["schema"] = schema

            exists = conn.execute(text(check_sql), params).scalar()

            if exists:
                print(f"✅ Index `{index_name}` already exists on `{table}` [{db_type}]")
            else:
                print(f"📌 Creating index `{index_name}` on `{table}` [{db_type}]")
                conn.execute(text(create_sql))
                touched_tables.add(table)

        # רענון סטטיסטיקות על טבלאות שיצרנו בהן אינדקס
        for table in sorted(touched_tables):
            analyze_sql = analyze_stmt_templates.get(table)
            if analyze_sql:
                try:
                    conn.execute(text(analyze_sql))
                    print(f"🔍 ANALYZE done for `{table}` [{db_type}]")
                except Exception as e:
                    print(f"⚠️ ANALYZE failed for `{table}` [{db_type}]: {e}")

    print(f"✅ Done for {db_type.upper()}\n")


if __name__ == "__main__":
    create_indexes_if_missing("mysql")
    create_indexes_if_missing("postgres")

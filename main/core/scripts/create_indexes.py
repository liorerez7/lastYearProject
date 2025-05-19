from sqlalchemy import text
from main.core.schema_analysis.connection.db_connector import DBConnector

# רשימת האינדקסים הרצויים לפי DB
MYSQL_INDEX_QUERIES = [
    ("employees", "idx_emp_no_employees", "CREATE INDEX idx_emp_no_employees ON employees(emp_no);"),
    ("salaries", "idx_emp_no_salaries", "CREATE INDEX idx_emp_no_salaries ON salaries(emp_no);"),
    ("dept_emp", "idx_emp_no_dept_emp", "CREATE INDEX idx_emp_no_dept_emp ON dept_emp(emp_no);"),
    ("dept_emp", "idx_dept_no_dept_emp", "CREATE INDEX idx_dept_no_dept_emp ON dept_emp(dept_no);"),
    ("departments", "idx_dept_no_departments", "CREATE INDEX idx_dept_no_departments ON departments(dept_no);"),
    ("employees", "idx_birth_date_employees", "CREATE INDEX idx_birth_date_employees ON employees(birth_date);"),
    ("employees", "idx_emp_birth_employees", "CREATE INDEX idx_emp_birth_employees ON employees(emp_no, birth_date);"),
    ("salaries", "idx_emp_to_date", "CREATE INDEX idx_emp_to_date ON salaries(emp_no, to_date);"),
    ("salaries", "idx_emp_salary", "CREATE INDEX idx_emp_salary ON salaries(emp_no, salary);")

    ("dept_emp", "idx_dept_emp_combo", "CREATE INDEX idx_dept_emp_combo ON dept_emp(emp_no, dept_no, from_date);"),
    ("salaries", "idx_salaries_emp_to_date", "CREATE INDEX idx_salaries_emp_to_date ON salaries(emp_no, to_date);"),
    ("titles", "idx_titles_emp_no", "CREATE INDEX idx_titles_emp_no ON titles(emp_no);")
    ("salaries", "idx_salary_to_date", "CREATE INDEX idx_salary_to_date ON salaries(salary, to_date);"),
    ("salaries", "idx_window_salary_to_date_emp", "CREATE INDEX idx_window_salary_to_date_emp ON salaries(salary, to_date DESC, emp_no);")
    ("salaries", "idx_window_emp_to_date_salary", "CREATE INDEX idx_window_emp_to_date_salary ON salaries(emp_no, to_date DESC, salary);")



]

PG_INDEX_QUERIES = [
    ("employees", "idx_emp_no_employees", 'CREATE INDEX idx_emp_no_employees ON "extendedEmp".employees(emp_no);'),
    ("salaries", "idx_emp_no_salaries", 'CREATE INDEX idx_emp_no_salaries ON "extendedEmp".salaries(emp_no);'),
    ("dept_emp", "idx_emp_no_dept_emp", 'CREATE INDEX idx_emp_no_dept_emp ON "extendedEmp".dept_emp(emp_no);'),
    ("dept_emp", "idx_dept_no_dept_emp", 'CREATE INDEX idx_dept_no_dept_emp ON "extendedEmp".dept_emp(dept_no);'),
    ("departments", "idx_dept_no_departments", 'CREATE INDEX idx_dept_no_departments ON "extendedEmp".departments(dept_no);'),
    ("employees", "idx_birth_date_employees", 'CREATE INDEX idx_birth_date_employees ON "extendedEmp".employees(birth_date);'),
    ("employees", "idx_emp_birth_employees", 'CREATE INDEX idx_emp_birth_employees ON "extendedEmp".employees(emp_no, birth_date);'),
    ("salaries", "idx_emp_to_date",
     'CREATE INDEX IF NOT EXISTS idx_emp_to_date '
     'ON "extendedEmp".salaries(emp_no, to_date);'),
    ("salaries", "idx_emp_salary",
     'CREATE INDEX IF NOT EXISTS idx_emp_salary '
     'ON "extendedEmp".salaries(emp_no, salary);')

    ("dept_emp", "idx_dept_emp_combo",
     'CREATE INDEX idx_dept_emp_combo ON "extendedEmp".dept_emp(emp_no, dept_no, from_date);'),
    ("salaries", "idx_salaries_emp_to_date",
     'CREATE INDEX idx_salaries_emp_to_date ON "extendedEmp".salaries(emp_no, to_date);'),
    ("titles", "idx_titles_emp_no", 'CREATE INDEX idx_titles_emp_no ON "extendedEmp".titles(emp_no);')

    ("salaries", "idx_salary_to_date", 'CREATE INDEX idx_salary_to_date ON "extendedEmp".salaries(salary, to_date);'),
    ("salaries", "idx_window_salary_to_date_emp", 'CREATE INDEX idx_window_salary_to_date_emp ON "extendedEmp".salaries(salary, to_date DESC, emp_no);')


]


def create_indexes_if_missing(db_type: str):
    print(f"\n🔧 Checking indexes for {db_type.upper()}...")
    engine, _ = DBConnector(db_type).connect("finalEmp")

    if db_type == "mysql":
        index_queries = MYSQL_INDEX_QUERIES
        check_index_sql = """
            SELECT COUNT(*)
            FROM information_schema.statistics
            WHERE table_schema = DATABASE()
              AND table_name = :table
              AND index_name = :index;
        """
    elif db_type == "postgres":
        index_queries = PG_INDEX_QUERIES
        check_index_sql = """
            SELECT COUNT(*)
            FROM pg_indexes
            WHERE schemaname = 'finalEmp'
              AND tablename = :table
              AND indexname = :index;
        """
    else:
        raise ValueError("Unsupported DB type")

    with engine.connect() as conn:
        for table, index_name, create_sql in index_queries:
            result = conn.execute(text(check_index_sql), {"table": table, "index": index_name})
            exists = result.scalar()

            if exists:
                print(f"✅ Index `{index_name}` already exists on `{table}` [{db_type}]")
            else:
                print(f"📌 Creating index `{index_name}` on `{table}` [{db_type}]")
                conn.execute(text(create_sql))

    print(f"✅ Done for {db_type.upper()}\n")


if __name__ == "__main__":
    create_indexes_if_missing("mysql")
    create_indexes_if_missing("postgres")

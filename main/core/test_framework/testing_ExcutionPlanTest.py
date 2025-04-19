from main.core.db_compare.connection.db_connector import DBConnector
from main.core.test_framework.execution_plan_test import ExecutionPlanTest
from main.core.test_framework.plans.deep_join_plan import deep_join_plan

if __name__ == '__main__':
    # ✅ Step 1: Create DBConnector for Postgres
    connector = DBConnector(db_type="mysql")

    # ✅ Step 2: Connect and reflect metadata
    engine, metadata = connector.connect(schema="sakila")

    # ✅ Step 3: Load the plan and run it
    test = ExecutionPlanTest(deep_join_plan())
    test.run(engine, metadata,"mysql")
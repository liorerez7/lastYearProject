from main.core.db_compare.connection.db_connector import DBConnector
from main.core.test_framework.execution_plan_test import ExecutionPlanTest
from main.core.test_framework.plans.deep_join_plan import deep_join_plan

if __name__ == '__main__':
    connector_mysql = DBConnector(db_type="mysql")
    connector_postgres = DBConnector(db_type="postgres")
    # ✅ Step 2: Connect and reflect metadata
    engine1, metadata1 = connector_mysql.connect(schema="sakila")
    test1 = ExecutionPlanTest(deep_join_plan())
    test1.run(engine1, metadata1, "mysql")

    engine2, metadata2 = connector_postgres.connect(schema="sakila")
    # ✅ Step 3: Load the plan and run it
    test2 = ExecutionPlanTest(deep_join_plan())
    test2.run(engine2, metadata2, "postgres")

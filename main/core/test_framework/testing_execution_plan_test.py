from main.core.test_framework.plans.deep_join_plans import deep_join_longest, deep_join_default
from main.core.db_compare.connection.db_connector import DBConnector
from main.core.test_framework.execution_plan_test import ExecutionPlanTest
from main.core.db_compare.query_generator.selector_explorer import SelectorExplorer
from main.core.db_compare.query_generator.strategies.deep_join_strategy import DeepJoinQueryStrategy

def find_selector(schema: str, db_type: str):
    connector = DBConnector(db_type)
    engine, metadata = connector.connect(schema)
    explorer = SelectorExplorer(DeepJoinQueryStrategy, metadata, db_type)
    print(f"explorer: {explorer}")
    return explorer.find_first_valid_selector()

def run_test(schema: str):
    selector = find_selector(schema, "mysql")
    print(f"✅ Using selector {selector} for both MySQL and PostgreSQL")

    for db_type in ["mysql", "postgres"]:
        connector = DBConnector(db_type)
        engine, metadata = connector.connect(schema=schema)

        steps = (
            deep_join_longest(db_type, selector) +
            deep_join_default(db_type, selector)
        )

        test = ExecutionPlanTest(steps, db_type)
        test.run(engine, metadata)


if __name__ == '__main__':
    run_test(schema="sakila")


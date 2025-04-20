from main.core.query_generation.selector_explorer import SelectorExplorer
from main.core.query_generation.strategies.deep_join_strategy import DeepJoinQueryStrategy
from main.core.test_framework.plans.aggregation_plans import aggregation_test
from main.core.test_framework.plans.basic_select_plans import basic_select
from main.core.schema_analysis.connection.db_connector import DBConnector
from main.core.test_framework.execution_plan_test import ExecutionPlanTest
from main.core.test_framework.plans.selector_helpers import find_selector_for


def find_selector(schema: str, db_type: str):
    connector = DBConnector(db_type)
    engine, metadata = connector.connect(schema)
    explorer = SelectorExplorer(DeepJoinQueryStrategy, metadata, db_type)
    return explorer.find_first_valid_selector()

def run_test(schema: str):
    connector = DBConnector("mysql")
    engine, metadata = connector.connect(schema)

    selector_deep = find_selector_for("deep_join", metadata, "mysql")
    selector_basic = find_selector_for("basic_select", metadata, "mysql")
    selector_agg = find_selector_for("aggregation", metadata, "mysql")

    print(f"✅ DeepJoin selector = {selector_deep}")
    print(f"✅ BasicSelect selector = {selector_basic}")
    print(f"✅ Aggregation selector = {selector_agg}")

    for db_type in ["postgres", "mysql"]:
        connector = DBConnector(db_type)
        engine, metadata = connector.connect(schema=schema)

        steps = (
            # deep_join_longest(db_type, selector_deep) +
            # deep_join_default(db_type, selector_deep) +
            basic_select(db_type, selector_basic) +
            aggregation_test(db_type, selector_agg)
        )

        test = ExecutionPlanTest(steps, db_type)
        test.run(engine, metadata)


if __name__ == '__main__':
    run_test(schema="sakila")


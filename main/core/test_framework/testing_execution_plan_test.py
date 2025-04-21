# from main.core.query_generation.selector_explorer import SelectorExplorer
# from main.core.query_generation.strategies.deep_join_strategy import DeepJoinQueryStrategy
# from main.core.test_framework.plans.aggregation_plans import aggregation_test
# from main.core.test_framework.plans.basic_select_plans import basic_select
# from main.core.schema_analysis.connection.db_connector import DBConnector
# from main.core.test_framework.execution_plan_test import ExecutionPlanTest
# from main.core.test_framework.plans.filtered_query_plans import filtered_test
# from main.core.test_framework.plans.group_by_plans import group_by
# from main.core.test_framework.plans.reverse_join_plans import reverse_join
# from main.core.test_framework.plans.selector_helpers import find_selector_for, get_size_based_selectors
#
#
#
# def run_test(schema: str):
#     connector = DBConnector("mysql")
#     engine, metadata = connector.connect(schema)
#
#     sel_deep = find_selector_for("deep_join", metadata, "mysql")
#     sel_rev = find_selector_for("reverse_join", metadata, "mysql")
#
#     sizes = get_size_based_selectors(schema, "mysql")
#     sel_small, sel_mid, sel_large = sizes["small"], sizes["medium"], sizes["large"]
#
#     print(f"✅ DeepJoin selector = {sel_deep}")
#     print(f"✅ ReverseJoin selector = {sel_rev}")
#     print(f"✅ size‑based selectors = {sizes}")
#
#     for db_type in ["postgres", "mysql"]:
#         connector = DBConnector(db_type)
#         engine, metadata = connector.connect(schema=schema)
#
#         steps = (
#
#             reverse_join(db_type, sel_rev, repeat=2, delay=1)
#             + basic_select(db_type, sel_small, repeat=1, delay=1)
#             + basic_select(db_type, sel_mid, repeat=2, delay=1)
#             + basic_select(db_type, sel_large, repeat=1, delay=1)
#         )
#
#         test = ExecutionPlanTest(steps, db_type, schema)
#         test.run(engine, metadata)
#
#
# if __name__ == '__main__':
#     run_test(schema="sakila")
#
from main.core.query_generation.selector_explorer import SelectorExplorer
from main.core.query_generation.strategies.deep_join_strategy import DeepJoinQueryStrategy



from main.core.test_framework.plans.aggregation_plans import aggregation_test
from main.core.test_framework.plans.basic_select_plans import basic_select
from main.core.schema_analysis.connection.db_connector import DBConnector
from main.core.test_framework.execution_plan_test import ExecutionPlanTest
from main.core.test_framework.plans.deep_join_plans import deep_join_longest
from main.core.test_framework.plans.filtered_query_plans import filtered_test
from main.core.test_framework.plans.group_by_plans import group_by
from main.core.test_framework.plans.reverse_join_plans import reverse_join
from main.core.test_framework.plans.selector_helpers import find_selector_for, get_size_based_selectors


def run_test_select(schema: str):
    sizes = get_size_based_selectors(schema, "mysql")
    run("basic_select", schema, steps_fn=lambda db: (
        basic_select(db, sizes["small"], repeat=1) +
        basic_select(db, sizes["medium"], repeat=2) +
        basic_select(db, sizes["large"], repeat=1)
    ))


def run_test_filtered(schema: str):
    sizes = get_size_based_selectors(schema, "mysql")
    run("filtered", schema, steps_fn=lambda db: (
        filtered_test(db, sizes["small"], repeat=1) +
        filtered_test(db, sizes["medium"], repeat=2) +
        filtered_test(db, sizes["large"], repeat=1)
    ))


def run_test_group_by(schema: str):
    sizes = get_size_based_selectors(schema, "mysql")
    run("group_by", schema, steps_fn=lambda db: (
        group_by(db, sizes["small"], repeat=1) +
        group_by(db, sizes["medium"], repeat=2) +
        group_by(db, sizes["large"], repeat=1)
    ))


def run_test_aggregation(schema: str):
    sizes = get_size_based_selectors(schema, "mysql")
    run("aggregation", schema, steps_fn=lambda db: (
        aggregation_test(db, sizes["small"], repeat=1) +
        aggregation_test(db, sizes["medium"], repeat=2) +
        aggregation_test(db, sizes["large"], repeat=1)
    ))
def run_test_deep_join(schema: str):
    try:
        sel = find_selector_for("deep_join", _get_metadata(schema, "mysql"), "mysql")
    except ValueError:
        print("⚠️  No valid DeepJoin selector found – skipping.")
        return

    run("deep_join", schema, steps_fn=lambda db: deep_join_longest(db, sel))

def run_test_reverse_join(schema: str):
    try:
        sel = find_selector_for("reverse_join", _get_metadata(schema, "mysql"), "mysql")
    except ValueError:
        print("⚠️  No valid ReverseJoin selector found – skipping.")
        return

    run("reverse_join", schema, steps_fn=lambda db: reverse_join(db, sel, repeat=3))


def run(test_type: str, schema: str, steps_fn):
    print(f"\n🚀 Running test: {test_type.upper()}")
    for db_type in ["postgres", "mysql"]:
        connector = DBConnector(db_type)
        engine, metadata = connector.connect(schema=schema)
        steps = steps_fn(db_type)
        test = ExecutionPlanTest(steps, db_type, schema)
        test.run(engine, metadata)


def _get_metadata(schema: str, db_type: str):
    conn = DBConnector(db_type)
    _, metadata = conn.connect(schema)
    return metadata


if __name__ == '__main__':
    #run_test_select("sakila")
    #run_test_filtered("sakila")
    #run_test_group_by("sakila")
    #run_test_aggregation("sakila")
    #run_test_reverse_join("sakila")
    run_test_deep_join("sakila")

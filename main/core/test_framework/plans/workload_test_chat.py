from main.core.query_generation.query_generator_service import QueryGeneratorService
from main.core.test_framework.plans.deep_join_plans import deep_join_longest, deep_join_default


def realistic_workload(db_type: str, selector: int = None):
    steps = []

    # Step 1: Simple Select from small table (departments)
    steps.append({
        "label": "Select Small Table",
        "generator": QueryGeneratorService("basic_select", db_type, {
        }).generator,
        "repeat": 3,
        "delay": 1,
        "selector": selector
    })

    # Step 2: Simple Select from large table (employees)
    steps.append({
        "label": "Select Large Table",
        "generator": QueryGeneratorService("basic_select", db_type, {
        }).generator,
        "repeat": 3,
        "delay": 1,
        "selector": selector
    })

    # Step 3: Deep Join (Longest)
    steps += deep_join_longest(db_type, selector)

    # Step 4: Deep Join (Default)
    steps += deep_join_default(db_type, selector)

    # Step 5: Aggregate (e.g., avg salary)
    steps.append({
        "label": "Aggregate Salary",
        "generator": QueryGeneratorService("aggregation", db_type, {
        }).generator,
        "repeat": 2,
        "delay": 1,
        "selector": selector
    })

    # Step 6: Filtered Select (e.g., where gender = 'F')
    steps.append({
        "label": "Filtered Select",
        "generator": QueryGeneratorService("filtered", db_type, {
        }).generator,
        "repeat": 2,
        "delay": 1,
        "selector": selector
    })

    return steps

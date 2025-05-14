import pprint
from datetime import datetime
from typing import Dict, Any
import statistics

from main.core.test_framework.plans.aggregation_plans import aggregation_test
from main.core.test_framework.plans.deep_join_plans import deep_join_longest
from main.core.test_framework.plans.filtered_query_plans import filtered_test
from main.core.test_framework.plans.group_by_plans import group_by
from main.core.test_framework.plans.pagination_plans import pagination_test
from main.core.test_framework.plans.pure_count_plans import pure_count
from main.core.test_framework.plans.selector_helpers import get_size_based_selectors
from main.core.test_framework.plans.window_query_plans import window_query
from main.core.test_framework.plans.basic_select_plans import basic_select
from main.core.schema_analysis.connection.db_connector import DBConnector
from main.core.test_framework.execution_plan_test import ExecutionPlanTest
from main.services.supabase_service import insert_metadata, insert_execution
from models.test_model import TestMetadata, TestExecution


def create_simple_test_service():
    # 1. צור מזהה טסט ייחודי
    test_id = f"user_demo#test#{datetime.utcnow().isoformat()}"

    # 2. צור metadata
    metadata = TestMetadata(
        test_id=test_id,
        cloud_provider="aws",
        source_db="mysql",
        destination_db="postgres",
        status="pending",
        mail="lior@example.com"
    )
    insert_metadata(metadata.to_dynamo_item())

    # 3. צור ובנה את תכנית הבדיקה
    schema = "employees"
    test_type = "basic_select"
    sizes = get_size_based_selectors(schema, "mysql")
    timestamp = datetime.utcnow().isoformat()

    execution_results = {}

    for db_type in ["mysql", "postgres"]:
        engine, metadata_obj = DBConnector(db_type).connect(schema)
        plan = (basic_select(db_type, sizes["small"], repeat=1) +
                basic_select(db_type, sizes["large"], repeat=2))

        test = ExecutionPlanTest(plan, db_type, schema, test_name=test_type)
        built = test.build(engine, metadata_obj)
        test.run(engine, metadata_obj)

        # 4. שמור execution עם built (ולא התוצאה)
        execution = TestExecution(
            test_id=test_id,
            timestamp=timestamp,
            db_type=db_type,
            test_type=test_type,
            schema=schema,
            queries=list(test.get_built_plan_with_durations().values())
        )

        insert_execution(execution.to_dynamo_item())

        execution_results[db_type] = execution.to_dynamo_item()

    # 5. נחזיר ל־UI תוצאה ברורה
    return {
        "test_id": test_id,
        "execution": execution_results
    }


def create_full_test_benchmark() -> Dict[str, Any]:
    """Run the benchmark twice (10 and 20 users) with 60‑second sessions."""

    test_id = f"user_demo#test#{datetime.utcnow().isoformat()}"
    meta = TestMetadata(
        test_id=test_id,
        cloud_provider="aws",
        source_db="mysql",
        destination_db="postgres",
        status="pending",
        mail="lior@example.com",
    )
    insert_metadata(meta.to_dynamo_item())

    schema = "extendedEmp"
    sizes = get_size_based_selectors(schema, "mysql")
    execution_results: Dict[str, Any] = {}

    steps_tpl = (
        aggregation_test(":db", sizes["large"], repeat=5) +
        pure_count(":db", sizes["large"], repeat=2) +
        basic_select(":db", sizes["small"], repeat=30) +
        filtered_test(":db", sizes["medium"], repeat=20) +
        pagination_test(":db", sizes["large"], repeat=10) +
        window_query(":db", sizes["medium"], repeat=5) +
        deep_join_longest(":db", sizes["large"]) +
        group_by(":db", sizes["medium"], repeat=5)
    )

    for db_type in ("mysql", "postgres"):
        engine, meta_obj = DBConnector(db_type).connect(schema)
        for users in (10, 20):
            # instantiate steps for the specific db
            steps = [{**s, "generator": s["generator"], "repeat": s["repeat"], "selector": s.get("selector")}
                     for s in steps_tpl]
            for step in steps:
                step["generator"] = step["generator"](db_type) if callable(step["generator"]) else step["generator"]

            test = ExecutionPlanTest(steps, db_type, schema, test_name=f"extreme_suite_{users}u")
            test.build(engine, meta_obj)
            locust_cfg = {
                "wait_time_min": 1,
                "wait_time_max": 3,
                "users": users,
                "spawn_rate": 2,
                "run_time": 30,
            }
            test.run(engine, meta_obj, locust_config=locust_cfg)

            exec_obj = TestExecution(
                test_id=test_id,
                timestamp=datetime.utcnow().isoformat(),
                db_type=db_type,
                test_type=f"extreme_suite_{users}u",
                schema=schema,
                queries=list(test.get_built_plan_with_durations().values()),
            )

            pprint.pprint(test.get_built_plan_with_durations())
            insert_execution(exec_obj.to_dynamo_item())
            key = f"{db_type}_{users}u"
            execution_results[key] = exec_obj.to_dynamo_item()

    return {"test_id": test_id, "execution": execution_results}

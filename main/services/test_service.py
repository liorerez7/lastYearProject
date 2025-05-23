# import json
# import uuid
# from datetime import datetime
# import time
# import statistics
# from typing import Dict, Any, Callable
# from main.core.test_framework.plans.aggregation_plans import aggregation_test
# from main.core.test_framework.plans.deep_join_plans import deep_join_longest, deep_join_default
# from main.core.test_framework.plans.filtered_query_plans import filtered_test
# from main.core.test_framework.plans.group_by_plans import group_by
# from main.core.test_framework.plans.pagination_plans import pagination_test
# from main.core.test_framework.plans.pure_count_plans import pure_count
# from main.core.test_framework.plans.selector_helpers import get_size_based_selectors, get_adaptive_selectors
# from main.core.test_framework.plans.window_query_plans import window_query
# from main.core.test_framework.plans.basic_select_plans import basic_select
# from main.core.test_framework.plans.large_offset_plans import large_offset
# from main.core.test_framework.plans.recursive_cte_plans import recursive_cte
# from main.core.schema_analysis.connection.db_connector import DBConnector
# from main.core.test_framework.execution_plan_test import ExecutionPlanTest
# from main.services.supabase_service import insert_metadata, insert_execution
#
#
# def _create_test_metadata(tag: str) -> tuple[int, str]:
#     """Create and print test metadata only once per test suite."""
#     run_uid = uuid.uuid4().hex
#     started_at = datetime.utcnow().isoformat()
#
#     print("\n📦 META DATA:")
#     metadata = {
#         "run_uid": run_uid,
#         "cloud_provider": "aws",
#         "source_db": "mysql",
#         "destination_db": "postgres",
#         "status": "done",
#         "mail": "lior@example.com",
#         "plan_name": f"Extreme Plan – {tag}",
#         "started_at": started_at,
#         "finished_at": datetime.utcnow().isoformat(),
#         "summary_json": {"summary": "some summary here"},
#         "recommendations": "some recs here"
#     }
#     print(json.dumps(metadata, indent=2))
#     run_id = insert_metadata(metadata)
#
#     return run_id, run_uid
#
#
# def _generic_extreme_suite(*, users: list[int], run_time: int, tag: str,
#                            steps_override: Callable | None = None, spread: bool = False) -> Dict[str, Any]:
#     """Build + run the suite for both engines and multiple user counts."""
#
#     run_id, run_uid = _create_test_metadata(tag)
#
#     schema = "finalEmp"
#     sizes = get_adaptive_selectors(schema, "mysql") if spread else get_size_based_selectors(schema, "mysql")
#
#     default_steps = (
#             basic_select(":db", sizes.get("t1"), repeat=40) +
#             filtered_test(":db", sizes.get("t3"), repeat=25) +
#             aggregation_test(":db", sizes.get("t6"), repeat=5) +
#             pagination_test(":db", sizes.get("t5"), repeat=10) +
#             window_query(":db", sizes.get("t4"), repeat=6) +
#             pure_count(":db", sizes.get("t7"), repeat=6) +
#             group_by(":db", sizes.get("t5"), repeat=6)
#     )
#
#     steps_tpl = steps_override(sizes) if steps_override else default_steps
#
#     for db_type in ("mysql", "postgres"):
#         engine, meta_obj = DBConnector(db_type).connect(schema)
#         for u in users:
#             steps = [{**s, "selector": s.get("selector"), "repeat": s["repeat"], "generator": s["generator"]} for s in
#                      steps_tpl]
#             for s in steps:
#                 if callable(s["generator"]):
#                     s["generator"] = s["generator"](db_type)
#
#             test = ExecutionPlanTest(steps, db_type, schema, test_name=f"{tag}_{u}u")
#             test.build(engine, meta_obj)
#             test.run(
#                 engine,
#                 meta_obj,
#                 locust_config={
#                     "wait_time_min": 0.5,
#                     "wait_time_max": 1.5,
#                     "users": u,
#                     "spawn_rate": 2,
#                     "run_time": run_time,
#                 },
#             )
#
#             queries = list(test.get_built_plan_with_durations().values())
#             for q in queries:
#                 q["p95"] = statistics.quantiles(q["durations"], n=100)[94] if q["durations"] else 0.0
#                 q["p99"] = statistics.quantiles(q["durations"], n=100)[98] if q["durations"] else 0.0
#
#             step_results = []
#             for step in queries:
#
#                 executions_count = len(step.get("durations", []))
#
#                 insert_execution(
#                     test_id=run_id,
#                     db_type=db_type,
#                     test_type=f"{tag}_{u}u",
#                     schema=schema,
#                     timestamp=datetime.utcnow().isoformat(),
#                     query_type=step["query_type"],
#                     selector=step.get("selector", "0"),
#                     avg=step.get("avg", 0.0),
#                     p95=step.get("p95", 0.0),
#                     p99=step.get("p99", 0.0),
#                     stddev=step.get("stddev", 0.0),
#                     executions_count=executions_count,
#                     queries=[step]
#                 )
#
#                 step_results.append(step)
#
#     return {"run_id": run_id, "run_uid": run_uid}
#
#
# def _run_named_suite(label: str, order: list[str]) -> Dict[str, Any]:
#     """Run a named benchmark suite with a list of test plan names."""
#
#     # Create metadata once for the entire suite
#     tag = label.lower().replace(" ", "_")
#     run_id, run_uid = _create_test_metadata(tag)
#
#     results: Dict[str, Any] = {}
#
#     for name in order:
#         func = TEST_PLANS.get(name)
#         if not func:
#             print(f"⚠️ Unknown test plan: {name}")
#             continue
#
#         print(f"\n=== Running benchmark: {name} ===")
#         try:
#             # Run the test but use the suite's metadata
#             test_result = func(use_existing_metadata=(run_id, run_uid))
#             results[name] = test_result
#             print(f"✅ '{name}' done – test_id: {run_id}")
#         except Exception as e:
#             print(f"❌ '{name}' failed: {e}")
#         print("🕒 Cooling‑down 5 s…")  ## need to move back into 45, after testing.
#         time.sleep(5)
#
#     print(f"\n🏁 Suite '{label}' completed.\n")
#     return {
#         "run_id": run_id,
#         "run_uid": run_uid,
#         "results": results,
#         "message": f"{label} suite completed"
#     }
#
#
# # Helper function to run tests with existing metadata
# def _generic_test_with_metadata(run_id, run_uid, *, tag, users, run_time, spread=False, steps_override=None):
#     """Version of _generic_extreme_suite that uses existing metadata."""
#     schema = "finalEmp"
#     sizes = get_adaptive_selectors(schema, "mysql") if spread else get_size_based_selectors(schema, "mysql")
#
#     # Default spread pattern (used only if no override is passed)
#     default_steps = (
#             basic_select(":db", sizes.get("t1"), repeat=40) +
#             filtered_test(":db", sizes.get("t3"), repeat=25) +
#             aggregation_test(":db", sizes.get("t6"), repeat=5) +
#             pagination_test(":db", sizes.get("t5"), repeat=10) +
#             window_query(":db", sizes.get("t4"), repeat=6) +
#             pure_count(":db", sizes.get("t7"), repeat=6) +
#             group_by(":db", sizes.get("t5"), repeat=6)
#     )
#
#     steps_tpl = steps_override(sizes) if steps_override else default_steps
#
#     for db_type in ("mysql", "postgres"):
#         engine, meta_obj = DBConnector(db_type).connect(schema)
#         for u in users:
#             steps = [{**s, "selector": s.get("selector"), "repeat": s["repeat"], "generator": s["generator"]} for s in
#                      steps_tpl]
#             for s in steps:
#                 if callable(s["generator"]):
#                     s["generator"] = s["generator"](db_type)
#
#             test = ExecutionPlanTest(steps, db_type, schema, test_name=f"{tag}_{u}u")
#             test.build(engine, meta_obj)
#             test.run(
#                 engine,
#                 meta_obj,
#                 locust_config={
#                     "wait_time_min": 0.5,
#                     "wait_time_max": 1.5,
#                     "users": u,
#                     "spawn_rate": 2,
#                     "run_time": run_time,
#                 },
#             )
#
#             queries = list(test.get_built_plan_with_durations().values())
#             for q in queries:
#                 q["p95"] = statistics.quantiles(q["durations"], n=100)[94] if q["durations"] else 0.0
#                 q["p99"] = statistics.quantiles(q["durations"], n=100)[98] if q["durations"] else 0.0
#
#             step_results = []
#             for step in queries:
#
#                 executions_count = len(step.get("durations", []))
#
#                 insert_execution(
#                     test_id=run_id,
#                     db_type=db_type,
#                     test_type=f"{tag}_{u}u",
#                     schema=schema,
#                     timestamp=datetime.utcnow().isoformat(),
#                     query_type=step["query_type"],
#                     selector=step.get("selector", "0"),
#                     avg=step.get("avg", 0.0),
#                     p95=step.get("p95", 0.0),
#                     p99=step.get("p99", 0.0),
#                     stddev=step.get("stddev", 0.0),
#                     executions_count=executions_count,
#                     queries=[step]
#                 )
#
#                 step_results.append(step)
#
#     return {"run_id": run_id, "run_uid": run_uid}
#
#
# # Modified to accept existing metadata parameter
# def run_mix_workload(use_existing_metadata=None):
#     if use_existing_metadata:
#         run_id, run_uid = use_existing_metadata
#         return _generic_test_with_metadata(run_id, run_uid, tag="mix", users=[10, 20], run_time=45, spread=True)
#     return _generic_extreme_suite(tag="mix", users=[10, 20], run_time=45, spread=True)
#
#
# # Update all test functions to accept the metadata parameter
# def run_multi_user_smoke(use_existing_metadata=None):
#     if use_existing_metadata:
#         run_id, run_uid = use_existing_metadata
#         return _generic_test_with_metadata(run_id, run_uid, tag="smoke", users=[5, 10], run_time=20, spread=True,
#                                            steps_override=lambda s: basic_select(":db", s["t1"], repeat=25) +
#                                                                     filtered_test(":db", s["t2"], repeat=25) +
#                                                                     pure_count(":db", s["t1"], repeat=5))
#     return _generic_extreme_suite(tag="smoke", users=[5, 10], run_time=20, spread=True,
#                                   steps_override=lambda s: basic_select(":db", s["t1"], repeat=25) +
#                                                            filtered_test(":db", s["t2"], repeat=25) +
#                                                            pure_count(":db", s["t1"], repeat=5))
#
#
# def run_index_stress(use_existing_metadata=None):
#     if use_existing_metadata:
#         run_id, run_uid = use_existing_metadata
#         return _generic_test_with_metadata(run_id, run_uid, tag="index", users=[15], run_time=45, spread=True,
#                                            steps_override=lambda s: filtered_test(":db", s["t3"], repeat=25) +
#                                                                     group_by(":db", s["t4"], repeat=20) +
#                                                                     pagination_test(":db", s["t5"], repeat=15))
#     return _generic_extreme_suite(tag="index", users=[15], run_time=45, spread=True,
#                                   steps_override=lambda s: filtered_test(":db", s["t3"], repeat=25) +
#                                                            group_by(":db", s["t4"], repeat=20) +
#                                                            pagination_test(":db", s["t5"], repeat=15))
#
#
# def run_heavy_read_write(use_existing_metadata=None):
#     if use_existing_metadata:
#         run_id, run_uid = use_existing_metadata
#         return _generic_test_with_metadata(run_id, run_uid, tag="rw", users=[8, 16], run_time=120, spread=True,
#                                            steps_override=lambda s: pagination_test(":db", s["t6"], repeat=15) +
#                                                                     basic_select(":db", s["t2"], repeat=15) +
#                                                                     aggregation_test(":db", s["t5"], repeat=12) +
#                                                                     pure_count(":db", s["t1"], repeat=12))
#     return _generic_extreme_suite(tag="rw", users=[8, 16], run_time=120, spread=True,
#                                   steps_override=lambda s: pagination_test(":db", s["t6"], repeat=15) +
#                                                            basic_select(":db", s["t2"], repeat=15) +
#                                                            aggregation_test(":db", s["t5"], repeat=12) +
#                                                            pure_count(":db", s["t1"], repeat=12))
#
#
# def run_reporting_analytics(use_existing_metadata=None):
#     if use_existing_metadata:
#         run_id, run_uid = use_existing_metadata
#         return _generic_test_with_metadata(run_id, run_uid, tag="report", users=[5], run_time=50, spread=True,
#                                            steps_override=lambda s: window_query(":db", s["t5"], repeat=20) +
#                                                                     group_by(":db", s["t6"], repeat=20) +
#                                                                     aggregation_test(":db", s["t6"], repeat=20))
#     return _generic_extreme_suite(tag="report", users=[5], run_time=50, spread=True,
#                                   steps_override=lambda s: window_query(":db", s["t5"], repeat=20) +
#                                                            group_by(":db", s["t6"], repeat=20) +
#                                                            aggregation_test(":db", s["t6"], repeat=20))
#
#
# def run_edge_case_offsets(use_existing_metadata=None):
#     if use_existing_metadata:
#         run_id, run_uid = use_existing_metadata
#         return _generic_test_with_metadata(run_id, run_uid, tag="edge", users=[12], run_time=50, spread=True,
#                                            steps_override=lambda s: large_offset(":db", s["t7"], repeat=18) +
#                                                                     recursive_cte(":db", s["t2"], repeat=10) +
#                                                                     filtered_test(":db", s["t4"], repeat=12))
#     return _generic_extreme_suite(tag="edge", users=[12], run_time=50, spread=True,
#                                   steps_override=lambda s: large_offset(":db", s["t7"], repeat=18) +
#                                                            recursive_cte(":db", s["t2"], repeat=10) +
#                                                            filtered_test(":db", s["t4"], repeat=12))
#
#
# def run_point_lookup(use_existing_metadata=None):
#     if use_existing_metadata:
#         run_id, run_uid = use_existing_metadata
#         return _generic_test_with_metadata(run_id, run_uid, tag="lookup", users=[2], run_time=45, spread=True,
#                                            steps_override=lambda s: basic_select(":db", s["t1"], repeat=1) +
#                                                                     basic_select(":db", s["t2"], repeat=1) +
#                                                                     basic_select(":db", s["t3"], repeat=1) +
#                                                                     basic_select(":db", s["t4"], repeat=1) +
#                                                                     basic_select(":db", s["t5"], repeat=1) +
#                                                                     basic_select(":db", s["t6"], repeat=1))
#     return _generic_extreme_suite(tag="lookup", users=[2], run_time=45, spread=True,
#                                   steps_override=lambda s: basic_select(":db", s["t1"], repeat=1) +
#                                                            basic_select(":db", s["t2"], repeat=1) +
#                                                            basic_select(":db", s["t3"], repeat=1) +
#                                                            basic_select(":db", s["t4"], repeat=1) +
#                                                            basic_select(":db", s["t5"], repeat=1) +
#                                                            basic_select(":db", s["t6"], repeat=1))
#
#
# def run_small_join_select(use_existing_metadata=None):
#     if use_existing_metadata:
#         run_id, run_uid = use_existing_metadata
#         return _generic_test_with_metadata(run_id, run_uid, tag="smalljoin", users=[2], run_time=30, spread=True,
#                                            steps_override=lambda s: deep_join_default(":db", selector=s["t2"],
#                                                                                       join_size=2) +
#                                                                     group_by(":db", s["t2"], repeat=6))
#     return _generic_extreme_suite(tag="smalljoin", users=[2], run_time=30, spread=True,
#                                   steps_override=lambda s: deep_join_default(":db", selector=s["t2"], join_size=2) +
#                                                            group_by(":db", s["t2"], repeat=6))
#
#
# def run_dashboard_reads(use_existing_metadata=None):
#     if use_existing_metadata:
#         run_id, run_uid = use_existing_metadata
#         return _generic_test_with_metadata(run_id, run_uid, tag="dash", users=[3], run_time=35, spread=True,
#                                            steps_override=lambda s: filtered_test(":db", s["t1"], repeat=20) +
#                                                                     filtered_test(":db", s["t5"], repeat=20) +
#                                                                     pagination_test(":db", s["t1"], repeat=10))
#     return _generic_extreme_suite(tag="dash", users=[3], run_time=30, spread=True,
#                                   steps_override=lambda s: filtered_test(":db", s["t1"], repeat=20) +
#                                                            filtered_test(":db", s["t5"], repeat=20) +
#                                                            pagination_test(":db", s["t1"], repeat=10))
#
#
# def run_spike_30_users(use_existing_metadata=None):
#     if use_existing_metadata:
#         run_id, run_uid = use_existing_metadata
#         return _generic_test_with_metadata(run_id, run_uid, tag="spike30", users=[30], run_time=600, spread=True)
#     return _generic_extreme_suite(tag="spike30", users=[30], run_time=600, spread=True)
#
#
# def run_heavy_only(use_existing_metadata=None):
#     if use_existing_metadata:
#         run_id, run_uid = use_existing_metadata
#         return _generic_test_with_metadata(run_id, run_uid, tag="heavy", users=[4], run_time=180, spread=True,
#                                            steps_override=lambda s: pure_count(":db", s["t6"], repeat=6) +
#                                                                     window_query(":db", s["t5"], repeat=6) +
#                                                                     deep_join_longest(":db", s["t7"]) +
#                                                                     pagination_test(":db", s["t7"], repeat=8))
#     return _generic_extreme_suite(tag="heavy", users=[4], run_time=180, spread=True,
#                                   steps_override=lambda s: pure_count(":db", s["t6"], repeat=6) +
#                                                            window_query(":db", s["t5"], repeat=6) +
#                                                            deep_join_longest(":db", s["t7"]) +
#                                                            pagination_test(":db", s["t7"], repeat=8))
#
#
#
#
# def run_basic_queries_suite() -> Dict[str, Any]:
#     return _run_named_suite("Basic Queries", ["lookup", "dash", "smalljoin", "smoke", "index"])
#
# def run_advanced_workload_suite() -> Dict[str, Any]:
#     return _run_named_suite("Advanced Workload", ["heavy"])
#
#
# def run_balanced_suite() -> Dict[str, Any]:
#     return _run_named_suite("Balanced Suite", [
#         "lookup", "dash", "smalljoin",
#         "smoke", "index",
#         "heavy",
#         "mix", "rw", "report", "edge", "spike30"
#     ])
#
#
# # ---------------------------------------------------------------------
# # 3. TEST_PLANS
# # ---------------------------------------------------------------------
# TEST_PLANS: Dict[str, Callable[..., Dict[str, Any]]] = {
#     "lookup": run_point_lookup,
#     "dash": run_dashboard_reads,
#     "smalljoin": run_small_join_select,
#     "smoke": run_multi_user_smoke,
#     "index": run_index_stress,
#     "mix": run_mix_workload,
#     "rw": run_heavy_read_write,
#     "report": run_reporting_analytics,
#     "edge": run_edge_case_offsets,
#     "heavy": run_heavy_only,
#     "spike30": run_spike_30_users,
# }

import json
import uuid
from datetime import datetime
import time
import statistics
from typing import Dict, Any, Callable, Optional, Tuple
from main.core.test_framework.plans.aggregation_plans import aggregation_test
from main.core.test_framework.plans.deep_join_plans import deep_join_longest, deep_join_default
from main.core.test_framework.plans.filtered_query_plans import filtered_test
from main.core.test_framework.plans.group_by_plans import group_by
from main.core.test_framework.plans.pagination_plans import pagination_test
from main.core.test_framework.plans.pure_count_plans import pure_count
from main.core.test_framework.plans.selector_helpers import get_size_based_selectors, get_adaptive_selectors
from main.core.test_framework.plans.window_query_plans import window_query
from main.core.test_framework.plans.basic_select_plans import basic_select
from main.core.test_framework.plans.large_offset_plans import large_offset
from main.core.test_framework.plans.recursive_cte_plans import recursive_cte
from main.core.schema_analysis.connection.db_connector import DBConnector
from main.core.test_framework.execution_plan_test import ExecutionPlanTest
from main.services.supabase_service import insert_metadata, insert_execution, update_metadata_status


def _create_test_metadata(tag: str) -> Tuple[int, str]:
    """Create and return test metadata."""
    run_uid = uuid.uuid4().hex
    started_at = datetime.utcnow().isoformat()

    print("\n📦 META DATA:")
    metadata = {
        "run_uid": run_uid,
        "cloud_provider": "aws",
        "source_db": "mysql",
        "destination_db": "postgres",
        "status": "running",
        "mail": "lior@example.com",
        "plan_name": f"Extreme Plan – {tag}",
        "started_at": started_at,
        "finished_at": None,
        "summary_json": {"summary": "some summary here"},
        "recommendations": "some recs here"
    }
    print(json.dumps(metadata, indent=2))
    run_id = insert_metadata(metadata)

    return run_id, run_uid


def _execute_test_plan(
        tag: str,
        users: list[int],
        run_time: int,
        spread: bool = False,
        steps_override: Optional[Callable] = None,
        metadata: Optional[Tuple[int, str]] = None
) -> Dict[str, Any]:
    """Execute a test plan with the given parameters."""

    # Use existing metadata or create new
    if metadata:
        run_id, run_uid = metadata
    else:
        run_id, run_uid = _create_test_metadata(tag)

    schema = "finalEmp"
    sizes = get_adaptive_selectors(schema, "mysql") if spread else get_size_based_selectors(schema, "mysql")

    # Default test steps
    default_steps = (
            basic_select(":db", sizes.get("t1"), repeat=40) +
            filtered_test(":db", sizes.get("t3"), repeat=25) +
            aggregation_test(":db", sizes.get("t6"), repeat=5) +
            pagination_test(":db", sizes.get("t5"), repeat=10) +
            window_query(":db", sizes.get("t4"), repeat=6) +
            pure_count(":db", sizes.get("t7"), repeat=6) +
            group_by(":db", sizes.get("t5"), repeat=6)
    )

    steps_tpl = steps_override(sizes) if steps_override else default_steps

    for db_type in ("mysql", "postgres"):
        engine, meta_obj = DBConnector(db_type).connect(schema)
        for u in users:
            steps = [{**s, "selector": s.get("selector"), "repeat": s["repeat"], "generator": s["generator"]} for s in
                     steps_tpl]
            for s in steps:
                if callable(s["generator"]):
                    s["generator"] = s["generator"](db_type)

            test = ExecutionPlanTest(steps, db_type, schema, test_name=f"{tag}_{u}u")
            test.build(engine, meta_obj)
            test.run(
                engine,
                meta_obj,
                locust_config={
                    "wait_time_min": 0.5,
                    "wait_time_max": 1.5,
                    "users": u,
                    "spawn_rate": 2,
                    "run_time": run_time,
                },
            )

            queries = list(test.get_built_plan_with_durations().values())
            for q in queries:
                q["p95"] = statistics.quantiles(q["durations"], n=100)[94] if q["durations"] else 0.0
                q["p99"] = statistics.quantiles(q["durations"], n=100)[98] if q["durations"] else 0.0

            for step in queries:
                executions_count = len(step.get("durations", []))

                insert_execution(
                    test_id=run_id,
                    db_type=db_type,
                    test_type=f"{tag}_{u}u",
                    schema=schema,
                    timestamp=datetime.utcnow().isoformat(),
                    query_type=step["query_type"],
                    selector=step.get("selector", "0"),
                    avg=step.get("avg", 0.0),
                    p95=step.get("p95", 0.0),
                    p99=step.get("p99", 0.0),
                    stddev=step.get("stddev", 0.0),
                    executions_count=executions_count,
                    queries=[step]
                )

    return {"run_id": run_id, "run_uid": run_uid}


def _run_named_suite(label: str, test_names: list[str]) -> Dict[str, Any]:
    """Run a named benchmark suite with a list of test plan names."""

    tag = label.lower().replace(" ", "_")
    run_id, run_uid = _create_test_metadata(tag)
    results: Dict[str, Any] = {}
    failed_tests = []
    successful_tests = []

    for name in test_names:
        test_config = TEST_CONFIGS.get(name)
        if not test_config:
            print(f"⚠️ Unknown test plan: {name}")
            failed_tests.append(name)
            continue

        print(f"\n=== Running benchmark: {name} ===")
        try:
            # Run the test using existing metadata
            test_result = _execute_test_plan(
                tag=test_config["tag"],
                users=test_config["users"],
                run_time=test_config["run_time"],
                spread=test_config.get("spread", False),
                steps_override=test_config.get("steps_override"),
                metadata=(run_id, run_uid)
            )
            results[name] = test_result
            successful_tests.append(name)
            print(f"✅ '{name}' done – test_id: {run_id}")
        except Exception as e:
            print(f"❌ '{name}' failed: {e}")
            failed_tests.append(name)

        print("🕒 Cooling‑down 5 s…")
        time.sleep(5)

    # Update metadata status after all tests are completed
    finished_at = datetime.utcnow().isoformat()

    # Create summary of the test suite results
    summary_json = {
        "total_tests": len(test_names),
        "successful_tests": len(successful_tests),
        "failed_tests": len(failed_tests),
        "successful_test_names": successful_tests,
        "failed_test_names": failed_tests,
        "suite_name": label
    }

    # Determine final status
    final_status = "completed" if len(failed_tests) == 0 else "completed_with_errors"

    # Generate recommendations based on results
    recommendations = f"Suite '{label}' completed with {len(successful_tests)}/{len(test_names)} tests successful."
    if failed_tests:
        recommendations += f" Failed tests: {', '.join(failed_tests)}. Consider investigating these failures."

    try:
        update_metadata_status(
            test_id=run_id,
            status=final_status,
            summary_json=summary_json,
            recommendations=recommendations,
            finished_at=finished_at
        )
        print(f"✅ Metadata updated to '{final_status}' status")
    except Exception as e:
        print(f"❌ Failed to update metadata status: {e}")

    print(f"\n🏁 Suite '{label}' completed.\n")
    return {
        "run_id": run_id,
        "run_uid": run_uid,
        "results": results,
        "summary": summary_json,
        "message": f"{label} suite completed with status: {final_status}"
    }


# Test configurations - all test parameters in one place
TEST_CONFIGS: Dict[str, Dict[str, Any]] = {
    "lookup": {
        "tag": "lookup",
        "users": [2],
        "run_time": 10,
        "spread": True,
        "steps_override": lambda s: (
            basic_select(":db", s["t1"], repeat=1)

        )
    },
    "dash": {
        "tag": "dash",
        "users": [3],
        "run_time": 10,
        "spread": True,
        "steps_override": lambda s: (
                filtered_test(":db", s["t1"], repeat=20) +
                filtered_test(":db", s["t5"], repeat=20) +
                pagination_test(":db", s["t1"], repeat=10)
        )
    },
    "smalljoin": {
        "tag": "smalljoin",
        "users": [2],
        "run_time": 30,
        "spread": True,
        "steps_override": lambda s: (
                deep_join_default(":db", selector=s["t2"], join_size=2) +
                group_by(":db", s["t2"], repeat=6)
        )
    },
    "smoke": {
        "tag": "smoke",
        "users": [5, 10],
        "run_time": 20,
        "spread": True,
        "steps_override": lambda s: (
                basic_select(":db", s["t1"], repeat=25) +
                filtered_test(":db", s["t2"], repeat=25) +
                pure_count(":db", s["t1"], repeat=5)
        )
    },
    "index": {
        "tag": "index",
        "users": [15],
        "run_time": 45,
        "spread": True,
        "steps_override": lambda s: (
                filtered_test(":db", s["t3"], repeat=25) +
                group_by(":db", s["t4"], repeat=20) +
                pagination_test(":db", s["t5"], repeat=15)
        )
    },
    "mix": {
        "tag": "mix",
        "users": [10, 20],
        "run_time": 45,
        "spread": True
    },
    "rw": {
        "tag": "rw",
        "users": [8, 16],
        "run_time": 120,
        "spread": True,
        "steps_override": lambda s: (
                pagination_test(":db", s["t6"], repeat=15) +
                basic_select(":db", s["t2"], repeat=15) +
                aggregation_test(":db", s["t5"], repeat=12) +
                pure_count(":db", s["t1"], repeat=12)
        )
    },
    "report": {
        "tag": "report",
        "users": [5],
        "run_time": 50,
        "spread": True,
        "steps_override": lambda s: (
                window_query(":db", s["t5"], repeat=20) +
                group_by(":db", s["t6"], repeat=20) +
                aggregation_test(":db", s["t6"], repeat=20)
        )
    },
    "edge": {
        "tag": "edge",
        "users": [12],
        "run_time": 50,
        "spread": True,
        "steps_override": lambda s: (
                large_offset(":db", s["t7"], repeat=18) +
                recursive_cte(":db", s["t2"], repeat=10) +
                filtered_test(":db", s["t4"], repeat=12)
        )
    },
    "heavy": {
        "tag": "heavy",
        "users": [4],
        "run_time": 180,
        "spread": True,
        "steps_override": lambda s: (
                pure_count(":db", s["t6"], repeat=6) +
                window_query(":db", s["t5"], repeat=6) +
                deep_join_longest(":db", s["t7"]) +
                pagination_test(":db", s["t7"], repeat=8)
        )
    },
    "spike30": {
        "tag": "spike30",
        "users": [30],
        "run_time": 600,
        "spread": True
    }
}


# Individual test functions (if you still need them for standalone use)
def run_point_lookup() -> Dict[str, Any]:
    config = TEST_CONFIGS["lookup"]
    result = _execute_test_plan(**config)

    # Update metadata status for individual test
    try:
        update_metadata_status(
            test_id=result["run_id"],
            status="completed",
            summary_json={"test_type": "individual", "test_name": "lookup"},
            recommendations="Individual lookup test completed successfully",
            finished_at=datetime.utcnow().isoformat()
        )
    except Exception as e:
        print(f"❌ Failed to update metadata for individual test: {e}")

    return result


def run_dashboard_reads() -> Dict[str, Any]:
    config = TEST_CONFIGS["dash"]
    result = _execute_test_plan(**config)

    # Update metadata status for individual test
    try:
        update_metadata_status(
            test_id=result["run_id"],
            status="completed",
            summary_json={"test_type": "individual", "test_name": "dash"},
            recommendations="Individual dashboard reads test completed successfully",
            finished_at=datetime.utcnow().isoformat()
        )
    except Exception as e:
        print(f"❌ Failed to update metadata for individual test: {e}")

    return result


def run_small_join_select() -> Dict[str, Any]:
    config = TEST_CONFIGS["smalljoin"]
    result = _execute_test_plan(**config)

    try:
        update_metadata_status(
            test_id=result["run_id"],
            status="completed",
            summary_json={"test_type": "individual", "test_name": "smalljoin"},
            recommendations="Individual small join test completed successfully",
            finished_at=datetime.utcnow().isoformat()
        )
    except Exception as e:
        print(f"❌ Failed to update metadata for individual test: {e}")

    return result


def run_multi_user_smoke() -> Dict[str, Any]:
    config = TEST_CONFIGS["smoke"]
    result = _execute_test_plan(**config)

    try:
        update_metadata_status(
            test_id=result["run_id"],
            status="completed",
            summary_json={"test_type": "individual", "test_name": "smoke"},
            recommendations="Individual multi-user smoke test completed successfully",
            finished_at=datetime.utcnow().isoformat()
        )
    except Exception as e:
        print(f"❌ Failed to update metadata for individual test: {e}")

    return result


def run_index_stress() -> Dict[str, Any]:
    config = TEST_CONFIGS["index"]
    result = _execute_test_plan(**config)

    try:
        update_metadata_status(
            test_id=result["run_id"],
            status="completed",
            summary_json={"test_type": "individual", "test_name": "index"},
            recommendations="Individual index stress test completed successfully",
            finished_at=datetime.utcnow().isoformat()
        )
    except Exception as e:
        print(f"❌ Failed to update metadata for individual test: {e}")

    return result


def run_mix_workload() -> Dict[str, Any]:
    config = TEST_CONFIGS["mix"]
    result = _execute_test_plan(**config)

    try:
        update_metadata_status(
            test_id=result["run_id"],
            status="completed",
            summary_json={"test_type": "individual", "test_name": "mix"},
            recommendations="Individual mix workload test completed successfully",
            finished_at=datetime.utcnow().isoformat()
        )
    except Exception as e:
        print(f"❌ Failed to update metadata for individual test: {e}")

    return result


def run_heavy_read_write() -> Dict[str, Any]:
    config = TEST_CONFIGS["rw"]
    result = _execute_test_plan(**config)

    try:
        update_metadata_status(
            test_id=result["run_id"],
            status="completed",
            summary_json={"test_type": "individual", "test_name": "rw"},
            recommendations="Individual heavy read-write test completed successfully",
            finished_at=datetime.utcnow().isoformat()
        )
    except Exception as e:
        print(f"❌ Failed to update metadata for individual test: {e}")

    return result


def run_reporting_analytics() -> Dict[str, Any]:
    config = TEST_CONFIGS["report"]
    result = _execute_test_plan(**config)

    try:
        update_metadata_status(
            test_id=result["run_id"],
            status="completed",
            summary_json={"test_type": "individual", "test_name": "report"},
            recommendations="Individual reporting analytics test completed successfully",
            finished_at=datetime.utcnow().isoformat()
        )
    except Exception as e:
        print(f"❌ Failed to update metadata for individual test: {e}")

    return result


def run_edge_case_offsets() -> Dict[str, Any]:
    config = TEST_CONFIGS["edge"]
    result = _execute_test_plan(**config)

    try:
        update_metadata_status(
            test_id=result["run_id"],
            status="completed",
            summary_json={"test_type": "individual", "test_name": "edge"},
            recommendations="Individual edge case offsets test completed successfully",
            finished_at=datetime.utcnow().isoformat()
        )
    except Exception as e:
        print(f"❌ Failed to update metadata for individual test: {e}")

    return result


def run_heavy_only() -> Dict[str, Any]:
    config = TEST_CONFIGS["heavy"]
    result = _execute_test_plan(**config)

    try:
        update_metadata_status(
            test_id=result["run_id"],
            status="completed",
            summary_json={"test_type": "individual", "test_name": "heavy"},
            recommendations="Individual heavy test completed successfully",
            finished_at=datetime.utcnow().isoformat()
        )
    except Exception as e:
        print(f"❌ Failed to update metadata for individual test: {e}")

    return result


def run_spike_30_users() -> Dict[str, Any]:
    config = TEST_CONFIGS["spike30"]
    result = _execute_test_plan(**config)

    try:
        update_metadata_status(
            test_id=result["run_id"],
            status="completed",
            summary_json={"test_type": "individual", "test_name": "spike30"},
            recommendations="Individual spike 30 users test completed successfully",
            finished_at=datetime.utcnow().isoformat()
        )
    except Exception as e:
        print(f"❌ Failed to update metadata for individual test: {e}")

    return result


# Suite functions
def run_basic_queries_suite() -> Dict[str, Any]:
    return _run_named_suite("Basic Queries", ["lookup", "dash"])


def run_advanced_workload_suite() -> Dict[str, Any]:
    return _run_named_suite("Advanced Workload", ["heavy"])


def run_balanced_suite() -> Dict[str, Any]:
    return _run_named_suite("Balanced Suite", [
        "lookup", "dash", "smalljoin",
        "smoke", "index",
        "heavy",
        "mix", "rw", "report", "edge", "spike30"
    ])


# Backward compatibility mapping (if needed)
TEST_PLANS: Dict[str, Callable[..., Dict[str, Any]]] = {
    "lookup": run_point_lookup,
    "dash": run_dashboard_reads,
    "smalljoin": run_small_join_select,
    "smoke": run_multi_user_smoke,
    "index": run_index_stress,
    "mix": run_mix_workload,
    "rw": run_heavy_read_write,
    "report": run_reporting_analytics,
    "edge": run_edge_case_offsets,
    "heavy": run_heavy_only,
    "spike30": run_spike_30_users,
}
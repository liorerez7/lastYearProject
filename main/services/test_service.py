import json
import uuid
from datetime import datetime
import time
import statistics
from typing import Dict, Any, Callable
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
from main.services.supabase_service import insert_metadata, insert_execution
from models.models import TestMetadata, TestExecution


def _create_test_metadata(tag: str) -> tuple[str, str]:
    """Create and print test metadata only once per test suite."""
    run_uid = uuid.uuid4().hex
    run_id = f"manual_run_{uuid.uuid4().hex}"  # simple random just for testing
    started_at = datetime.utcnow().isoformat()

    print("\n📦 META DATA:")
    metadata = {
        "run_uid": run_uid,
        "cloud_provider": "aws",
        "source_db": "mysql",
        "destination_db": "postgres",
        "status": "done",
        "mail": "lior@example.com",
        "plan_name": f"Extreme Plan – {tag}",
        "started_at": started_at,
        "finished_at": datetime.utcnow().isoformat(),
        "summary_json": {"summary": "some summary here"},
        "recommendations": "some recs here"
    }
    print(json.dumps(metadata, indent=2))

    # Uncomment for production:
    # run_id = insert_metadata({
    #     "run_uid": run_uid,
    #     "cloud_provider": "aws",
    #     "source_db": "mysql",
    #     "destination_db": "postgres",
    #     "status": "pending",
    #     "mail": "lior@example.com",
    #     "plan_name": f"Extreme Plan – {tag}",
    #     "started_at": datetime.utcnow().isoformat()
    # })

    return run_id, run_uid


def _generic_extreme_suite(*, users: list[int], run_time: int, tag: str,
                           steps_override: Callable | None = None, spread: bool = False) -> Dict[str, Any]:
    """Build + run the suite for both engines and multiple user counts."""

    run_id, run_uid = _create_test_metadata(tag)

    schema = "finalEmp"
    sizes = get_adaptive_selectors(schema, "mysql") if spread else get_size_based_selectors(schema, "mysql")

    # Default spread pattern (used only if no override is passed)
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

            step_results = []
            for step in queries:
                print("\n🧪 EXECUTION ENTRY:")
                print(json.dumps({
                    "test_id": run_id,
                    "db_type": db_type,
                    "test_type": f"{tag}_{u}u",
                    "schema": schema,
                    "timestamp": datetime.utcnow().isoformat(),
                    "query_type": step["query_type"],
                    "selector": step.get("selector", "0"),
                    "avg": step.get("avg", 0.0),
                    "p95": step.get("p95", 0.0),
                    "p99": step.get("p99", 0.0),
                    "queries": [step]
                }, indent=2))

                step_results.append(step)

    return {"run_id": run_id, "run_uid": run_uid}


def _run_named_suite(label: str, order: list[str]) -> Dict[str, Any]:
    """Run a named benchmark suite with a list of test plan names."""

    # Create metadata once for the entire suite
    tag = label.lower().replace(" ", "_")
    run_id, run_uid = _create_test_metadata(tag)

    results: Dict[str, Any] = {}

    for name in order:
        func = TEST_PLANS.get(name)
        if not func:
            print(f"⚠️ Unknown test plan: {name}")
            continue

        print(f"\n=== Running benchmark: {name} ===")
        try:
            # Run the test but use the suite's metadata
            test_result = func(use_existing_metadata=(run_id, run_uid))
            results[name] = test_result
            print(f"✅ '{name}' done – test_id: {run_id}")
        except Exception as e:
            print(f"❌ '{name}' failed: {e}")
        print("🕒 Cooling‑down 5 s…")  ## need to move back into 45, after testing.
        time.sleep(5)

    print(f"\n🏁 Suite '{label}' completed.\n")
    return {
        "run_id": run_id,
        "run_uid": run_uid,
        "results": results,
        "message": f"{label} suite completed"
    }


# Modified to accept existing metadata parameter
def run_mix_workload(use_existing_metadata=None):
    if use_existing_metadata:
        run_id, run_uid = use_existing_metadata
        return _generic_test_with_metadata(run_id, run_uid, tag="mix", users=[10, 20], run_time=45, spread=True)
    return _generic_extreme_suite(tag="mix", users=[10, 20], run_time=45, spread=True)


# Helper function to run tests with existing metadata
def _generic_test_with_metadata(run_id, run_uid, *, tag, users, run_time, spread=False, steps_override=None):
    """Version of _generic_extreme_suite that uses existing metadata."""
    schema = "finalEmp"
    sizes = get_adaptive_selectors(schema, "mysql") if spread else get_size_based_selectors(schema, "mysql")

    # Default spread pattern (used only if no override is passed)
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

            step_results = []
            for step in queries:
                print("\n🧪 EXECUTION ENTRY:")
                print(json.dumps({
                    "test_id": run_id,
                    "db_type": db_type,
                    "test_type": f"{tag}_{u}u",
                    "schema": schema,
                    "timestamp": datetime.utcnow().isoformat(),
                    "query_type": step["query_type"],
                    "selector": step.get("selector", "0"),
                    "avg": step.get("avg", 0.0),
                    "p95": step.get("p95", 0.0),
                    "p99": step.get("p99", 0.0),
                    "queries": [step]
                }, indent=2))

                step_results.append(step)

    return {"run_id": run_id, "run_uid": run_uid}


# Update all test functions to accept the metadata parameter
def run_multi_user_smoke(use_existing_metadata=None):
    if use_existing_metadata:
        run_id, run_uid = use_existing_metadata
        return _generic_test_with_metadata(run_id, run_uid, tag="smoke", users=[5, 10], run_time=15, spread=True,
                                           steps_override=lambda s: basic_select(":db", s["t1"], repeat=25) +
                                                                    filtered_test(":db", s["t2"], repeat=25) +
                                                                    pure_count(":db", s["t1"], repeat=5))
    return _generic_extreme_suite(tag="smoke", users=[5, 10], run_time=15, spread=True,
                                  steps_override=lambda s: basic_select(":db", s["t1"], repeat=25) +
                                                           filtered_test(":db", s["t2"], repeat=25) +
                                                           pure_count(":db", s["t1"], repeat=5))


def run_index_stress(use_existing_metadata=None):
    if use_existing_metadata:
        run_id, run_uid = use_existing_metadata
        return _generic_test_with_metadata(run_id, run_uid, tag="index", users=[15], run_time=45, spread=True,
                                           steps_override=lambda s: filtered_test(":db", s["t3"], repeat=25) +
                                                                    group_by(":db", s["t4"], repeat=20) +
                                                                    pagination_test(":db", s["t5"], repeat=15))
    return _generic_extreme_suite(tag="index", users=[15], run_time=45, spread=True,
                                  steps_override=lambda s: filtered_test(":db", s["t3"], repeat=25) +
                                                           group_by(":db", s["t4"], repeat=20) +
                                                           pagination_test(":db", s["t5"], repeat=15))


def run_heavy_read_write(use_existing_metadata=None):
    if use_existing_metadata:
        run_id, run_uid = use_existing_metadata
        return _generic_test_with_metadata(run_id, run_uid, tag="rw", users=[8, 16], run_time=120, spread=True,
                                           steps_override=lambda s: pagination_test(":db", s["t6"], repeat=15) +
                                                                    basic_select(":db", s["t2"], repeat=15) +
                                                                    aggregation_test(":db", s["t5"], repeat=12) +
                                                                    pure_count(":db", s["t1"], repeat=12))
    return _generic_extreme_suite(tag="rw", users=[8, 16], run_time=120, spread=True,
                                  steps_override=lambda s: pagination_test(":db", s["t6"], repeat=15) +
                                                           basic_select(":db", s["t2"], repeat=15) +
                                                           aggregation_test(":db", s["t5"], repeat=12) +
                                                           pure_count(":db", s["t1"], repeat=12))


def run_reporting_analytics(use_existing_metadata=None):
    if use_existing_metadata:
        run_id, run_uid = use_existing_metadata
        return _generic_test_with_metadata(run_id, run_uid, tag="report", users=[5], run_time=50, spread=True,
                                           steps_override=lambda s: window_query(":db", s["t5"], repeat=20) +
                                                                    group_by(":db", s["t6"], repeat=20) +
                                                                    aggregation_test(":db", s["t6"], repeat=20))
    return _generic_extreme_suite(tag="report", users=[5], run_time=50, spread=True,
                                  steps_override=lambda s: window_query(":db", s["t5"], repeat=20) +
                                                           group_by(":db", s["t6"], repeat=20) +
                                                           aggregation_test(":db", s["t6"], repeat=20))


def run_edge_case_offsets(use_existing_metadata=None):
    if use_existing_metadata:
        run_id, run_uid = use_existing_metadata
        return _generic_test_with_metadata(run_id, run_uid, tag="edge", users=[12], run_time=50, spread=True,
                                           steps_override=lambda s: large_offset(":db", s["t7"], repeat=18) +
                                                                    recursive_cte(":db", s["t2"], repeat=10) +
                                                                    filtered_test(":db", s["t4"], repeat=12))
    return _generic_extreme_suite(tag="edge", users=[12], run_time=50, spread=True,
                                  steps_override=lambda s: large_offset(":db", s["t7"], repeat=18) +
                                                           recursive_cte(":db", s["t2"], repeat=10) +
                                                           filtered_test(":db", s["t4"], repeat=12))


def run_point_lookup(use_existing_metadata=None):
    if use_existing_metadata:
        run_id, run_uid = use_existing_metadata
        return _generic_test_with_metadata(run_id, run_uid, tag="lookup", users=[2], run_time=7, spread=True,
                                           steps_override=lambda s: basic_select(":db", s["t1"], repeat=10))
    return _generic_extreme_suite(tag="lookup", users=[2], run_time=7, spread=True,
                                  steps_override=lambda s: basic_select(":db", s["t1"], repeat=10))


def run_small_join_select(use_existing_metadata=None):
    if use_existing_metadata:
        run_id, run_uid = use_existing_metadata
        return _generic_test_with_metadata(run_id, run_uid, tag="smalljoin", users=[2], run_time=25, spread=True,
                                           steps_override=lambda s: deep_join_default(":db", selector=s["t2"],
                                                                                      join_size=2) +
                                                                    group_by(":db", s["t2"], repeat=6))
    return _generic_extreme_suite(tag="smalljoin", users=[2], run_time=25, spread=True,
                                  steps_override=lambda s: deep_join_default(":db", selector=s["t2"], join_size=2) +
                                                           group_by(":db", s["t2"], repeat=6))


def run_dashboard_reads(use_existing_metadata=None):
    if use_existing_metadata:
        run_id, run_uid = use_existing_metadata
        return _generic_test_with_metadata(run_id, run_uid, tag="dash", users=[3], run_time=30, spread=True,
                                           steps_override=lambda s: basic_select(":db", s["t1"], repeat=40) +
                                                                    pagination_test(":db", s["t1"], repeat=10))
    return _generic_extreme_suite(tag="dash", users=[3], run_time=30, spread=True,
                                  steps_override=lambda s: basic_select(":db", s["t1"], repeat=40) +
                                                           pagination_test(":db", s["t1"], repeat=10))


def run_spike_30_users(use_existing_metadata=None):
    if use_existing_metadata:
        run_id, run_uid = use_existing_metadata
        return _generic_test_with_metadata(run_id, run_uid, tag="spike30", users=[30], run_time=600, spread=True)
    return _generic_extreme_suite(tag="spike30", users=[30], run_time=600, spread=True)


def run_heavy_only(use_existing_metadata=None):
    if use_existing_metadata:
        run_id, run_uid = use_existing_metadata
        return _generic_test_with_metadata(run_id, run_uid, tag="heavy", users=[4], run_time=180, spread=True,
                                           steps_override=lambda s: pure_count(":db", s["t6"], repeat=6) +
                                                                    window_query(":db", s["t5"], repeat=6) +
                                                                    deep_join_longest(":db", s["t7"]) +
                                                                    pagination_test(":db", s["t7"], repeat=8))
    return _generic_extreme_suite(tag="heavy", users=[4], run_time=180, spread=True,
                                  steps_override=lambda s: pure_count(":db", s["t6"], repeat=6) +
                                                           window_query(":db", s["t5"], repeat=6) +
                                                           deep_join_longest(":db", s["t7"]) +
                                                           pagination_test(":db", s["t7"], repeat=8))


def run_basic_queries_suite() -> Dict[str, Any]:
    return _run_named_suite("Basic Queries", ["lookup"])


def run_advanced_workload_suite() -> Dict[str, Any]:
    return _run_named_suite("Advanced Workload", ["heavy"])


def run_balanced_suite() -> Dict[str, Any]:
    return _run_named_suite("Balanced Suite", [
        "lookup", "dash", "smalljoin",
        "smoke", "index",
        "heavy",
        "mix", "rw", "report", "edge", "spike30"
    ])


# ---------------------------------------------------------------------
# 3. TEST_PLANS
# ---------------------------------------------------------------------
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


# import json
# import uuid
# from datetime import datetime
# import time
# import statistics
# from typing import Dict, Any, Callable
# from main.core.test_framework.plans.aggregation_plans   import aggregation_test
# from main.core.test_framework.plans.deep_join_plans      import deep_join_longest, deep_join_default
# from main.core.test_framework.plans.filtered_query_plans import filtered_test
# from main.core.test_framework.plans.group_by_plans       import group_by
# from main.core.test_framework.plans.pagination_plans      import pagination_test
# from main.core.test_framework.plans.pure_count_plans      import pure_count
# from main.core.test_framework.plans.selector_helpers import get_size_based_selectors, get_adaptive_selectors
# from main.core.test_framework.plans.window_query_plans    import window_query
# from main.core.test_framework.plans.basic_select_plans    import basic_select
# from main.core.test_framework.plans.large_offset_plans    import large_offset
# from main.core.test_framework.plans.recursive_cte_plans   import recursive_cte
# from main.core.schema_analysis.connection.db_connector    import DBConnector
# from main.core.test_framework.execution_plan_test         import ExecutionPlanTest
# from main.services.supabase_service                       import insert_metadata, insert_execution
# from models.models import TestMetadata, TestExecution
#
#
# def _generic_extreme_suite(*, users: list[int], run_time: int, tag: str,
#                            steps_override: Callable | None = None, spread: bool = False) -> Dict[str, Any]:
#     """Build + run the suite for both engines and multiple user counts."""
#
#
#     run_uid = uuid.uuid4().hex
#     run_id = f"manual_run_{uuid.uuid4().hex}"  # simple random just for testing
#     started_at = datetime.utcnow().isoformat()
#
#     print("\n📦 META DATA:")
#
#     print(json.dumps({
#         "run_uid": run_uid,
#         "cloud_provider": "aws",
#         "source_db": "mysql",
#         "destination_db": "postgres",
#         "status": "done",
#         "mail": "lior@example.com",
#         "plan_name": "simple query Plan",
#         "started_at": started_at,
#         "finished_at": datetime.utcnow().isoformat(),
#         "summary_json": {"summary": "some summary here"},
#         "recommendations": "some recs here"
#     }, indent=2))
#
#     # run_id = insert_metadata({
#     #     "run_uid": run_uid,
#     #     "cloud_provider": "aws",
#     #     "source_db": "mysql",
#     #     "destination_db": "postgres",
#     #     "status": "pending",
#     #     "mail": "lior@example.com",
#     #     "plan_name": f"Extreme Plan – {tag}",
#     #     "started_at": datetime.utcnow().isoformat()
#     # })
#
#     schema = "finalEmp"
#     sizes = get_adaptive_selectors(schema, "mysql") if spread else get_size_based_selectors(schema, "mysql")
#
#     # Default spread pattern (used only if no override is passed)
#     default_steps = (
#         basic_select      (":db", sizes.get("t1"), repeat=40) +
#         filtered_test     (":db", sizes.get("t3"), repeat=25) +
#         aggregation_test  (":db", sizes.get("t6"), repeat=5)  +
#         pagination_test   (":db", sizes.get("t5"), repeat=10) +
#         window_query      (":db", sizes.get("t4"), repeat=6) +
#         pure_count        (":db", sizes.get("t7"), repeat=6)  +
#         group_by          (":db", sizes.get("t5"), repeat=6)
#     )
#
#     steps_tpl = steps_override(sizes) if steps_override else default_steps
#
#
#
#     for db_type in ("mysql", "postgres"):
#         engine, meta_obj = DBConnector(db_type).connect(schema)
#         for u in users:
#             steps = [{**s, "selector": s.get("selector"), "repeat": s["repeat"], "generator": s["generator"]} for s in steps_tpl]
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
#
#
#             step_results = []
#             for step in queries:
#                 print("\n🧪 EXECUTION ENTRY:")
#                 print(json.dumps({
#                     "test_id": run_id,
#                     "db_type": db_type,
#                     "test_type": f"{tag}_{u}u",
#                     "schema": schema,
#                     "timestamp": datetime.utcnow().isoformat(),
#                     "query_type": step["query_type"],
#                     "selector": step.get("selector", "0"),
#                     "avg": step.get("avg", 0.0),
#                     "p95": step.get("p95", 0.0),
#                     "p99": step.get("p99", 0.0),
#                     "queries": [step]
#                 }, indent=2))
#
#                 step_results.append(step)
#
#     return {"run_id": run_id, "run_uid": run_uid}
#
#
#
# def _run_named_suite(label: str, order: list[str]) -> Dict[str, Any]:
#     """Run a named benchmark suite with a list of test plan names."""
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
#             results[name] = func()
#             print(f"✅ '{name}' done – test_id: {results[name]['run_id']}")
#         except Exception as e:
#             print(f"❌ '{name}' failed: {e}")
#         print("🕒 Cooling‑down 5 s…") ## need to move back into 45, after testing.
#         time.sleep(5)
#
#     print(f"\n🏁 Suite '{label}' completed.\n")
#     first_key = next(iter(results))
#     run_id = results[first_key]["run_id"]
#     return {
#         "run_id": run_id,
#         "results": results,
#         "message": f"{label} suite completed"
#     }
#
#
#
# def run_mix_workload():
#     return _generic_extreme_suite(tag="mix", users=[10, 20], run_time=45, spread=True)
#
# def run_multi_user_smoke():
#     return _generic_extreme_suite(tag="smoke", users=[5, 10], run_time=15, spread=True,
#         steps_override=lambda s: basic_select(":db", s["t1"], repeat=25) +
#                                  filtered_test(":db", s["t2"], repeat=25) +
#                                  pure_count(":db", s["t1"], repeat=5))
#
# def run_index_stress():
#     return _generic_extreme_suite(tag="index", users=[15], run_time=45, spread=True,
#         steps_override=lambda s: filtered_test(":db", s["t3"], repeat=25) +
#                                  group_by(":db", s["t4"], repeat=20) +
#                                  pagination_test(":db", s["t5"], repeat=15))
#
# def run_heavy_read_write():
#     return _generic_extreme_suite(tag="rw", users=[8, 16], run_time=120, spread=True,
#         steps_override=lambda s: pagination_test(":db", s["t6"], repeat=15) +
#                                  basic_select(":db", s["t2"], repeat=15) +
#                                  aggregation_test(":db", s["t5"], repeat=12) +
#                                  pure_count(":db", s["t1"], repeat=12))
#
# def run_reporting_analytics():
#     return _generic_extreme_suite(tag="report", users=[5], run_time=50, spread=True,
#         steps_override=lambda s: window_query(":db", s["t5"], repeat=20) +
#                                  group_by(":db", s["t6"], repeat=20) +
#                                  aggregation_test(":db", s["t6"], repeat=20))
#
# def run_edge_case_offsets():
#     return _generic_extreme_suite(tag="edge", users=[12], run_time=50, spread=True,
#         steps_override=lambda s: large_offset(":db", s["t7"], repeat=18) +
#                                  recursive_cte(":db", s["t2"], repeat=10) +
#                                  filtered_test(":db", s["t4"], repeat=12))
#
# def run_point_lookup():
#     return _generic_extreme_suite(tag="lookup", users=[2], run_time=7, spread=True,
#         steps_override=lambda s: basic_select(":db", s["t1"], repeat=10)) #needs to be more run time
#
#
# def run_small_join_select():
#     return _generic_extreme_suite(tag="smalljoin", users=[2], run_time=25, spread=True,
#         steps_override=lambda s: deep_join_default(":db", selector=s["t2"], join_size=2) +
#                                  group_by(":db", s["t2"], repeat=6))
#
# def run_dashboard_reads():
#     return _generic_extreme_suite(tag="dash", users=[3], run_time=30, spread=True,
#         steps_override=lambda s: basic_select(":db", s["t1"], repeat=40) +
#                                  pagination_test(":db", s["t1"], repeat=10))
#
# def run_spike_30_users():
#     return _generic_extreme_suite(tag="spike30", users=[30], run_time=600, spread=True)
#
# def run_heavy_only():
#     return _generic_extreme_suite(tag="heavy", users=[4], run_time=180, spread=True,
#         steps_override=lambda s: pure_count(":db", s["t6"], repeat=6) +
#                                  window_query(":db", s["t5"], repeat=6) +
#                                  deep_join_longest(":db", s["t7"]) +
#                                  pagination_test(":db", s["t7"], repeat=8))
#
#
# def run_basic_queries_suite() -> Dict[str, Any]:
#     return _run_named_suite("Basic Queries", ["lookup"])
#
# def run_advanced_workload_suite() -> Dict[str, Any]:
#     return _run_named_suite("Advanced Workload", ["heavy"])
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
#
# # ---------------------------------------------------------------------
# # 3. TEST_PLANS
# # ---------------------------------------------------------------------
# TEST_PLANS: Dict[str, Callable[[], Dict[str, Any]]] = {
#     "lookup"   : run_point_lookup,
#     "dash"     : run_dashboard_reads,
#     "smalljoin": run_small_join_select,
#     "smoke"    : run_multi_user_smoke,
#     "index"    : run_index_stress,
#     "mix"      : run_mix_workload,
#     "rw"       : run_heavy_read_write,
#     "report"   : run_reporting_analytics,
#     "edge"     : run_edge_case_offsets,
#     "heavy"    : run_heavy_only,
#     "spike30" : run_spike_30_users,
# }

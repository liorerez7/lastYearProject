from datetime import datetime
import time
import statistics
from typing import Dict, Any, Callable
from main.core.test_framework.plans.aggregation_plans   import aggregation_test
from main.core.test_framework.plans.deep_join_plans      import deep_join_longest, deep_join_default
from main.core.test_framework.plans.filtered_query_plans import filtered_test
from main.core.test_framework.plans.group_by_plans       import group_by
from main.core.test_framework.plans.pagination_plans      import pagination_test
from main.core.test_framework.plans.pure_count_plans      import pure_count
from main.core.test_framework.plans.selector_helpers      import get_size_based_selectors
from main.core.test_framework.plans.window_query_plans    import window_query
from main.core.test_framework.plans.basic_select_plans    import basic_select
from main.core.test_framework.plans.large_offset_plans    import large_offset
from main.core.test_framework.plans.recursive_cte_plans   import recursive_cte
from main.core.schema_analysis.connection.db_connector    import DBConnector
from main.core.test_framework.execution_plan_test         import ExecutionPlanTest
from main.services.supabase_service                       import insert_metadata, insert_execution
from models.test_model                                    import TestMetadata, TestExecution

# ---------------------------------------------------------------------
# 1. Generic runner
# ---------------------------------------------------------------------

def _generic_extreme_suite(*, users: list[int], run_time: int, tag: str, steps_override: Callable | None = None) -> Dict[str, Any]:
    """ Build + run the suite for both engines and multiple user counts. """

    test_id = f"user_demo#{tag}#{datetime.utcnow().isoformat()}"
    insert_metadata(TestMetadata(
        test_id=test_id,
        cloud_provider="aws",
        source_db="mysql",
        destination_db="postgres",
        status="pending",
        mail="lior@example.com",
    ).to_dynamo_item())

    schema = "finalEmp"
    sizes  = get_size_based_selectors(schema, "mysql")  # selector always via MySQL stats

    default_steps = (
        aggregation_test  (":db", sizes["large" ], repeat=5)  +
        pure_count        (":db", sizes["large" ], repeat=6)  +
        basic_select      (":db", sizes["small" ], repeat=40) +
        filtered_test     (":db", sizes["medium"], repeat=25) +
        pagination_test   (":db", sizes["large" ], repeat=12) +
        window_query      (":db", sizes["medium"], repeat=6)  +
        deep_join_longest (":db", sizes["large" ]) +
        group_by          (":db", sizes["medium"], repeat=6)
    )
    steps_tpl = steps_override(sizes) if steps_override else default_steps

    exec_results: Dict[str, Any] = {}
    for db_type in ("mysql", "postgres"):
        engine, meta_obj = DBConnector(db_type).connect(schema)
        for u in users:
            steps = [{**s, "selector": s.get("selector"), "repeat": s["repeat"], "generator": s["generator"]} for s in steps_tpl]
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
                q["p95"] = statistics.quantiles(q["durations"], n=100)[94] if q["durations"] else None

            exec_obj = TestExecution(
                test_id=test_id,
                timestamp=datetime.utcnow().isoformat(),
                db_type=db_type,
                test_type=f"{tag}_{u}u",
                schema=schema,
                queries=list(test.get_built_plan_with_durations().values()),
            )
            insert_execution(exec_obj.to_dynamo_item())
            exec_results[f"{db_type}_{u}u"] = exec_obj.to_dynamo_item()

    return {"test_id": test_id, "execution": exec_results}

# ---------------------------------------------------------------------
# 2. Individual scenarios (unchanged run_time unless noted)
# ---------------------------------------------------------------------

def run_mix_workload():      return _generic_extreme_suite(tag="mix"   , users=[10, 20], run_time=45)
def run_multi_user_smoke():  return _generic_extreme_suite(tag="smoke" , users=[5, 10] , run_time=15,
    steps_override=lambda s: basic_select(":db", s["small"], repeat=20) +
                             filtered_test(":db", s["medium"], repeat=20) +
                             pure_count   (":db", s["small"], repeat=4))

def run_index_stress():     return _generic_extreme_suite(tag="index" , users=[15]   , run_time=45,
    steps_override=lambda s: filtered_test(":db", s["medium"], repeat=30) +
                             group_by     (":db", s["medium"], repeat=15) +
                             pagination_test(":db", s["large"], repeat=15))

def run_heavy_read_write(): return _generic_extreme_suite(tag="rw"    , users=[8, 16], run_time=120,
    steps_override=lambda s: pagination_test(":db", s["large"], repeat=20) +
                             basic_select (":db", s["small"], repeat=20) +
                             aggregation_test(":db", s["medium"], repeat=15) +
                             pure_count   (":db", s["small"], repeat=12))

def run_reporting_analytics(): return _generic_extreme_suite(tag="report", users=[5], run_time=50,
    steps_override=lambda s: window_query(":db", s["medium"], repeat=25) +
                             group_by    (":db", s["large" ], repeat=20) +
                             aggregation_test(":db", s["large"], repeat=15))

def run_edge_case_offsets(): return _generic_extreme_suite(tag="edge"  , users=[12], run_time=50,
    steps_override=lambda s: large_offset (":db", s["large"], repeat=15) +
                             recursive_cte(":db", s["small"], repeat=10) +
                             filtered_test(":db", s["medium"], repeat=12))

def run_point_lookup():      return _generic_extreme_suite(tag="lookup", users=[2],  run_time=20,
    steps_override=lambda s: basic_select(":db", s["small"], repeat=60))

def run_small_join_select(): return _generic_extreme_suite(tag="smalljoin", users=[2], run_time=25,
    steps_override=lambda s: deep_join_default(":db", selector=s["small"], join_size=2) +
                             group_by       (":db", s["small"], repeat=6))

def run_dashboard_reads():   return _generic_extreme_suite(tag="dash" , users=[3],  run_time=30,
    steps_override=lambda s: basic_select   (":db", s["small"], repeat=40) +
                             pagination_test(":db", s["small"], repeat=8))

def run_spike_30_users():
    return _generic_extreme_suite(
        tag="spike30",
        users=[30],
        run_time=600,  #
        steps_override=None
    )


# --- NEW: heavy‑only ensures complex queries really run ----------------

def run_heavy_only():
    return _generic_extreme_suite(tag="heavy", users=[4], run_time=180,
        steps_override=lambda s: pure_count      (":db", s["large" ], repeat=6) +
                                 window_query    (":db", s["medium"], repeat=6) +
                                 deep_join_longest(":db", s["large" ])           +
                                 pagination_test (":db", s["large" ], repeat=8))

# ---------------------------------------------------------------------
# 3. TEST_PLANS
# ---------------------------------------------------------------------
TEST_PLANS: Dict[str, Callable[[], Dict[str, Any]]] = {
    "lookup"   : run_point_lookup,
    "dash"     : run_dashboard_reads,
    "smalljoin": run_small_join_select,
    "smoke"    : run_multi_user_smoke,
    "index"    : run_index_stress,
    "mix"      : run_mix_workload,
    "rw"       : run_heavy_read_write,
    "report"   : run_reporting_analytics,
    "edge"     : run_edge_case_offsets,
    "heavy"    : run_heavy_only,
    "spike30" : run_spike_30_users,
}

# ---------------------------------------------------------------------
# 4. Master runner – runs **all** plans in logical order
# ---------------------------------------------------------------------

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


def _run_named_suite(label: str, order: list[str]) -> Dict[str, Any]:
    """Run a named benchmark suite with a list of test plan names."""
    print(f"\n🚀 Starting benchmark suite: {label}")
    results: Dict[str, Any] = {}

    for name in order:
        func = TEST_PLANS.get(name)
        if not func:
            print(f"⚠️ Unknown test plan: {name}")
            continue

        print(f"\n=== Running benchmark: {name} ===")
        try:
            results[name] = func()
            print(f"✅ '{name}' done – test_id: {results[name]['test_id']}")
        except Exception as e:
            print(f"❌ '{name}' failed: {e}")
        print("🕒 Cooling‑down 45 s…")
        time.sleep(45)

    print(f"\n🏁 Suite '{label}' completed.\n")
    return {"message": f"{label} suite completed", "results": results}

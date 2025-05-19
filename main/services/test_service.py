import pprint
from datetime import datetime
from typing import Dict, Any
import statistics

# from main.core.test_framework.plans.aggregation_plans import aggregation_test
# from main.core.test_framework.plans.deep_join_plans import deep_join_longest
# from main.core.test_framework.plans.filtered_query_plans import filtered_test
# from main.core.test_framework.plans.group_by_plans import group_by
# from main.core.test_framework.plans.pagination_plans import pagination_test
# from main.core.test_framework.plans.pure_count_plans import pure_count
# from main.core.test_framework.plans.selector_helpers import get_size_based_selectors
# from main.core.test_framework.plans.window_query_plans import window_query
# from main.core.test_framework.plans.basic_select_plans import basic_select
# from main.core.schema_analysis.connection.db_connector import DBConnector
# from main.core.test_framework.execution_plan_test import ExecutionPlanTest
# from main.services.supabase_service import insert_metadata, insert_execution
# from models.test_model import TestMetadata, TestExecution
#
#
# def create_simple_test_service():
#     # 1. צור מזהה טסט ייחודי
#     test_id = f"user_demo#test#{datetime.utcnow().isoformat()}"
#
#     # 2. צור metadata
#     metadata = TestMetadata(
#         test_id=test_id,
#         cloud_provider="aws",
#         source_db="mysql",
#         destination_db="postgres",
#         status="pending",
#         mail="lior@example.com"
#     )
#     insert_metadata(metadata.to_dynamo_item())
#
#     # 3. צור ובנה את תכנית הבדיקה
#     schema = "employees"
#     test_type = "basic_select"
#     sizes = get_size_based_selectors(schema, "mysql")
#     timestamp = datetime.utcnow().isoformat()
#
#     execution_results = {}
#
#     for db_type in ["mysql", "postgres"]:
#         engine, metadata_obj = DBConnector(db_type).connect(schema)
#         plan = (basic_select(db_type, sizes["small"], repeat=1) +
#                 basic_select(db_type, sizes["large"], repeat=2))
#
#         test = ExecutionPlanTest(plan, db_type, schema, test_name=test_type)
#         built = test.build(engine, metadata_obj)
#         test.run(engine, metadata_obj)
#
#         # 4. שמור execution עם built (ולא התוצאה)
#         execution = TestExecution(
#             test_id=test_id,
#             timestamp=timestamp,
#             db_type=db_type,
#             test_type=test_type,
#             schema=schema,
#             queries=list(test.get_built_plan_with_durations().values())
#         )
#
#         insert_execution(execution.to_dynamo_item())
#
#         execution_results[db_type] = execution.to_dynamo_item()
#
#     # 5. נחזיר ל־UI תוצאה ברורה
#     return {
#         "test_id": test_id,
#         "execution": execution_results
#     }
#
#
# def create_full_test_benchmark() -> Dict[str, Any]:
#     """Run the benchmark twice (10 and 20 users) with 60‑second sessions."""
#
#     test_id = f"user_demo#test#{datetime.utcnow().isoformat()}"
#     meta = TestMetadata(
#         test_id=test_id,
#         cloud_provider="aws",
#         source_db="mysql",
#         destination_db="postgres",
#         status="pending",
#         mail="lior@example.com",
#     )
#     insert_metadata(meta.to_dynamo_item())
#
#     schema = "extendedEmp"
#     sizes = get_size_based_selectors(schema, "mysql")
#     execution_results: Dict[str, Any] = {}
#
#     steps_tpl = (
#         aggregation_test(":db", sizes["large"], repeat=5) +
#         pure_count(":db", sizes["large"], repeat=2) +
#         basic_select(":db", sizes["small"], repeat=30) +
#         filtered_test(":db", sizes["medium"], repeat=20) +
#         pagination_test(":db", sizes["large"], repeat=10) +
#         window_query(":db", sizes["medium"], repeat=5) +
#         deep_join_longest(":db", sizes["large"]) +
#         group_by(":db", sizes["medium"], repeat=5)
#     )
#
#     for db_type in ("mysql", "postgres"):
#         engine, meta_obj = DBConnector(db_type).connect(schema)
#         for users in (10, 20):
#             # instantiate steps for the specific db
#             steps = [{**s, "generator": s["generator"], "repeat": s["repeat"], "selector": s.get("selector")}
#                      for s in steps_tpl]
#             for step in steps:
#                 step["generator"] = step["generator"](db_type) if callable(step["generator"]) else step["generator"]
#
#             test = ExecutionPlanTest(steps, db_type, schema, test_name=f"extreme_suite_{users}u")
#             test.build(engine, meta_obj)
#             locust_cfg = {
#                 "wait_time_min": 1,
#                 "wait_time_max": 3,
#                 "users": users,
#                 "spawn_rate": 2,
#                 "run_time": 60, # seconds. for 30 second it will be slower but alot more reliable
#             }
#             test.run(engine, meta_obj, locust_config=locust_cfg)
#
#             exec_obj = TestExecution(
#                 test_id=test_id,
#                 timestamp=datetime.utcnow().isoformat(),
#                 db_type=db_type,
#                 test_type=f"extreme_suite_{users}u",
#                 schema=schema,
#                 queries=list(test.get_built_plan_with_durations().values()),
#             )
#
#             pprint.pprint(test.get_built_plan_with_durations())
#             insert_execution(exec_obj.to_dynamo_item())
#             key = f"{db_type}_{users}u"
#             execution_results[key] = exec_obj.to_dynamo_item()
#
#     return {"test_id": test_id, "execution": execution_results}

# ------------- imports קיימים -------------
#
# from main.core.test_framework.plans.aggregation_plans import aggregation_test
# from main.core.test_framework.plans.deep_join_plans import deep_join_longest, deep_join_default
# from main.core.test_framework.plans.filtered_query_plans import filtered_test
# from main.core.test_framework.plans.group_by_plans import group_by
# from main.core.test_framework.plans.pagination_plans import pagination_test
# from main.core.test_framework.plans.pure_count_plans import pure_count
# from main.core.test_framework.plans.selector_helpers import get_size_based_selectors
# from main.core.test_framework.plans.window_query_plans import window_query
# from main.core.test_framework.plans.basic_select_plans import basic_select
# from main.core.schema_analysis.connection.db_connector import DBConnector
# from main.core.test_framework.execution_plan_test import ExecutionPlanTest
# from main.services.supabase_service import insert_metadata, insert_execution
# from models.test_model import TestMetadata, TestExecution
# from main.core.test_framework.plans.large_offset_plans import large_offset
# from main.core.test_framework.plans.recursive_cte_plans import recursive_cte
# from datetime import datetime
# import time
# from typing import Dict, Any, Callable
#
# # (שאר ה-imports שלך נשארים כפי שהם)
#
# # --------------------------------------------------------
# #           1. פונקציות-מבחן נפרדות
# # --------------------------------------------------------
#
# def run_mix_workload() -> Dict[str, Any]:
#     """
#     המבחן המלא – aggregation + group-by + deep join וכו׳ (מה שהיה extreme_suite).
#     """
#     return _generic_extreme_suite(users=[10, 20], run_time=45)
#
# def run_multi_user_smoke() -> Dict[str, Any]:
#     """
#     Smoke קצר: רק basic-select + filtered + count, עם 5-10 משתמשים ל-30 שניות.
#     """
#     return _generic_extreme_suite(
#         users=[5, 10],
#         run_time=10,
#         steps_override=lambda sizes: (
#             basic_select(":db", sizes["small"], repeat=10) +
#             filtered_test(":db", sizes["medium"], repeat=10) +
#             pure_count(":db", sizes["small"], repeat=2)
#         ),
#         tag="smoke"
#     )
#
# def run_index_stress() -> Dict[str, Any]:
#     """
#     דוגמה ל-suite שלישי לבחירתך: בודק רק שאילתות שמנצלות אינדקסים —
#     group-by, filtered ב-WHERE על עמודות מאונדקסות, וגם pagination.
#     """
#     return _generic_extreme_suite(
#         users=[15],
#         run_time=45,
#         steps_override=lambda sizes: (
#             filtered_test(":db", sizes["medium"], repeat=25) +
#             group_by(":db", sizes["medium"], repeat=10) +
#             pagination_test(":db", sizes["large"], repeat=10)
#         ),
#         tag="index_stress"
#     )
#
# # --------------------------------------------------------
# #           2.  סוויטה גנרית (קוד שלך עם מעט הכללות)
# # --------------------------------------------------------
#
# def _generic_extreme_suite(
#     *,
#     users: list[int],
#     run_time: int,
#     steps_override: Callable | None = None,
#     tag: str = "mix"
# ) -> Dict[str, Any]:
#
#     test_id = f"user_demo#{tag}#{datetime.utcnow().isoformat()}"
#     meta = TestMetadata(
#         test_id=test_id,
#         cloud_provider="aws",
#         source_db="mysql",
#         destination_db="postgres",
#         status="pending",
#         mail="lior@example.com",
#     )
#     insert_metadata(meta.to_dynamo_item())
#
#     schema = "finalEmp"
#     sizes  = get_size_based_selectors(schema, "mysql")
#     exec_results: Dict[str, Any] = {}
#
#     default_steps = (
#         aggregation_test(":db", sizes["large"], repeat=5) +
#         pure_count      (":db", sizes["large"], repeat=2) +
#         basic_select    (":db", sizes["small"], repeat=30) +
#         filtered_test   (":db", sizes["medium"], repeat=20) +
#         pagination_test (":db", sizes["large"], repeat=10) +
#         window_query    (":db", sizes["medium"], repeat=5) +
#         deep_join_longest(":db", sizes["large"])          +
#         group_by        (":db", sizes["medium"], repeat=5)
#     )
#     steps_tpl = steps_override(sizes) if steps_override else default_steps
#
#     for db_type in ("mysql", "postgres"):
#         engine, meta_obj = DBConnector(db_type).connect(schema)
#         for u in users:
#             steps = [
#                 {**s, "generator": s["generator"], "repeat": s["repeat"],
#                  "selector": s.get("selector")}
#                 for s in steps_tpl
#             ]
#             for s in steps:
#                 if callable(s["generator"]):
#                     s["generator"] = s["generator"](db_type)
#
#             test = ExecutionPlanTest(
#                 steps, db_type, schema, test_name=f"{tag}_{u}u"
#             )
#             test.build(engine, meta_obj)
#             locust_cfg = {
#                 "wait_time_min": 1,
#                 "wait_time_max": 3,
#                 "users": u,
#                 "spawn_rate": 2,
#                 "run_time": run_time,
#             }
#             test.run(engine, meta_obj, locust_config=locust_cfg)
#
#             exec_obj = TestExecution(
#                 test_id=test_id,
#                 timestamp=datetime.utcnow().isoformat(),
#                 db_type=db_type,
#                 test_type=f"{tag}_{u}u",
#                 schema=schema,
#                 queries=list(test.get_built_plan_with_durations().values()),
#             )
#             insert_execution(exec_obj.to_dynamo_item())
#             exec_results[f"{db_type}_{u}u"] = exec_obj.to_dynamo_item()
#
#     return {"test_id": test_id, "execution": exec_results}
#
# # --------------------------------------------------------
# # 4.  Heavy READ + WRITE (50% עדכון/הוספה בספירות)
# # --------------------------------------------------------
# def run_heavy_read_write() -> Dict[str, Any]:
#     """ תסריט CRUD מאוזן – מדמה אפליקציה שמעדכנת משכורות ומושכת הרבה דפים. """
#     return _generic_extreme_suite(
#         tag="rw",
#         users=[8, 16],
#         run_time=50,
#         steps_override=lambda sizes: (
#             # קריאות גדולות
#             pagination_test(":db", sizes["large"], repeat=15) +
#             basic_select  (":db", sizes["small"], repeat=20)   +
#             # “כתיבה” – נשתמש ב-Aggregation/Pure-count כ-stand-in ל–insert/update
#             aggregation_test(":db", sizes["medium"], repeat=10) +
#             pure_count      (":db", sizes["small"],  repeat=10)
#         )
#     )
#
# # --------------------------------------------------------
# # 5.  Reporting / Analytics (חלונות, Group-By, Aggregations)
# # --------------------------------------------------------
# def run_reporting_analytics() -> Dict[str, Any]:
#     """ workload אופייני לדוחות חודשיים / BI. """
#     return _generic_extreme_suite(
#         tag="report",
#         users=[5],
#         run_time=40,
#         steps_override=lambda sizes: (
#             window_query(":db", sizes["medium"], repeat=20) +
#             group_by    (":db", sizes["large"],  repeat=15) +
#             aggregation_test(":db", sizes["large"], repeat=10)
#         )
#     )
#
# # --------------------------------------------------------
# # 6.  Edge-case Offsets + Recursive CTE
# # --------------------------------------------------------
# def run_edge_case_offsets() -> Dict[str, Any]:
#     """ בוחן מקרים שידועים כבעיה ב-MySQL (large OFFSET) + recursion. """
#
#     return _generic_extreme_suite(
#         tag="edge",
#         users=[12],
#         run_time=45,
#         steps_override=lambda sizes: (
#             large_offset(":db", sizes["large"], repeat=12) +
#             recursive_cte(":db", sizes["small"], repeat=8) +
#             filtered_test(":db", sizes["medium"], repeat=10)
#         )
#     )
#
#
#
# # --------------------------------------------------------
# # 7.  Point lookup – MySQL usually wins
# # --------------------------------------------------------
# def run_point_lookup() -> Dict[str, Any]:
#     return _generic_extreme_suite(
#         tag="lookup",
#         users=[2],          # עומס קל
#         run_time=15,
#         steps_override=lambda sizes: (
#             basic_select(":db", sizes["small"], repeat=50)   # טבלה קטנה
#         )
#     )
#
#
# # --------------------------------------------------------
# # 8.  Bulk-insert / update burst
# # --------------------------------------------------------
# def run_small_join_select() -> Dict[str, Any]:
#     # deep_join_default כבר קיים אצלך – מתקנים רק את override:
#     from main.core.test_framework.plans.deep_join_plans import deep_join_default
#
#     return _generic_extreme_suite(
#         tag="smalljoin",
#         users=[2],
#         run_time=20,
#         steps_override=lambda sizes: (
#             deep_join_default(":db", selector=sizes["small"], join_size=2) +  # join קצר
#             group_by(":db", sizes["small"], repeat=4)
#         )
#     )
#
#
# # --------------------------------------------------------
# # 9.  Mini-dashboard read-only
# # --------------------------------------------------------
# def run_dashboard_reads() -> Dict[str, Any]:
#     return _generic_extreme_suite(
#         tag="dash",
#         users=[3],
#         run_time=25,
#         steps_override=lambda sizes: (
#             basic_select   (":db", sizes["small"],  repeat=30) +
#             pagination_test(":db", sizes["small"],  repeat=6)
#         )
#     )
#
#
#
#
# # --------------------------------------------------------
# # 10. מיפוי שם → פונקציה  (הרחבה)
# # --------------------------------------------------------
# TEST_PLANS: dict[str, Callable[[], Dict[str, Any]]] = {
#     "mix"       : run_mix_workload,
#     "smoke"     : run_multi_user_smoke,
#     "index"     : run_index_stress,
#     "lookup"    : run_point_lookup,
#     "dash"      : run_dashboard_reads,
#     "smalljoin" : run_small_join_select,
#     "rw"        : run_heavy_read_write,
#     "report"    : run_reporting_analytics,
#     "edge"      : run_edge_case_offsets,
# }
#
#
# def run_full_benchmark_suite() -> Dict[str, Any]:
#     test_functions = [
#         ("lookup"   , run_point_lookup),
#         ("dash"     , run_dashboard_reads),
#         ("smalljoin", run_small_join_select),
#         ("mix"      , run_mix_workload),   # הארוך בסוף
#     ]
#     results = {}
#     for name, func in test_functions:
#         print(f"\n=== Running benchmark: {name} ===")
#         try:
#             results[name] = func()
#             print(f"✅ '{name}' done – test_id: {results[name]['test_id']}")
#         except Exception as e:
#             print(f"❌ '{name}' failed: {e}")
#         print("🕒 Cooling-down 30 s…"); time.sleep(30)
#     return {"message": "Full suite completed", "results": results}



"""
benchmark_suite.py  – FULL RUN VERSION (2025‑05‑15)
-----------------------------------------------------
• מריץ את **כל** 10 התרחישים שב‑TEST_PLANS ברצף אחד, כולל heavy‑only.
• Cool‑down מובנה של 45 s בין תרחישים כדי לאפס cache ו‑locks.
• תרחיש heavy_only (90 s, 4 משתמשים) מבטיח שהשאילתות הכבדות (COUNT, WINDOW, Deep‑Join) ירוצו ≥ 6×.
• wait‑time Locust קצר יותר (0.5‑1.5 s) להגברת RPS.
"""

from datetime import datetime
import time
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

    schema = "finalEmp"                       # same name on both engines
    sizes  = get_size_based_selectors(schema, "mysql")  # selector always via MySQL stats

    default_steps = (
        aggregation_test  (":db", sizes["large" ], repeat=5)  +
        pure_count        (":db", sizes["large" ], repeat=6)  +  # ↑ 6 כדי למדוד בטוח
        basic_select      (":db", sizes["small" ], repeat=40) +
        filtered_test     (":db", sizes["medium"], repeat=25) +
        pagination_test   (":db", sizes["large" ], repeat=12) +
        window_query      (":db", sizes["medium"], repeat=6)  +  # ↑ window ≥6
        deep_join_longest (":db", sizes["large" ])             +
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

def run_everything() -> Dict[str, Any]:
    """Run all test plans; total ~60‑65 minutes including cool‑downs."""
    order = [
        "lookup", "dash", "smalljoin",          # latency‑low first
        "smoke", "index",                         # mid‑weight
        "heavy",                                   # guarantee heavy queries
        "mix", "rw", "report", "edge",         # long runs at the end
        "spike30",

    ]
    results: Dict[str, Any] = {}
    for name in order:
        func = TEST_PLANS[name]
        print(f"\n=== Running benchmark: {name} ===")
        try:
            results[name] = func()
            print(f"✅ '{name}' done – test_id: {results[name]['test_id']}")
        except Exception as e:
            print(f"❌ '{name}' failed: {e}")
        print("🕒 Cooling‑down 45 s…"); time.sleep(45)
    return {"message": "All plans completed", "results": results}
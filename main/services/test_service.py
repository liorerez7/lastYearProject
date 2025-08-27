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



def create_metadata_only(tag: str) -> Tuple[int, str]:
    return _create_test_metadata(tag.lower().replace(" ", "_"))

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

    # נשתמש בשם הסכמה להצגה/דיווח בתוצאות (בשני המנועים תרצה לראות 'mydb')
    schema_for_metrics = "finalEmp"

    # -------- חשוב: selectors חייבים להיבנות לפי כל DB בנפרד --------
    for db_type in ("mysql", "postgres"):
        # קביעת הסכמה/סקופ לרפלקציה לכל מנוע
        if db_type == "mysql":
            # ב-MySQL שם ה-"schema" הוא למעשה שם ה-DB
            schema_reflection = "finalEmp"
        else:
            # ב-Postgres מתחברים ל-DB mydb2 (מוגדר ב-db_config) ועובדים בסכמה mydb
            schema_reflection = "sakila_migrated"

        # בניית selectors עבור המנוע הנוכחי
        if spread:
            sizes = get_adaptive_selectors(schema_reflection, db_type)
            if not sizes:
                raise RuntimeError(
                    f"No tables discovered for {db_type} (schema='{schema_reflection}'). "
                    f"Check Postgres DB='mydb2' has schema '{schema_reflection}' and permissions, "
                    f"and that DBConnector sets search_path properly."
                )
        else:
            sizes = get_size_based_selectors(schema_reflection, db_type)

        # בניית steps עפ"י selectors של אותו מנוע
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

        # חיבור למנוע עם הסכמה/סקופ הנכון לרפלקציה
        engine, meta_obj = DBConnector(db_type).connect(schema_reflection)

        for u in users:
            # קלונינג ה-steps + הזרקת generator פר-DB
            steps = [{
                **s,
                "selector": s.get("selector"),
                "repeat": s["repeat"],
                "generator": s["generator"]
            } for s in steps_tpl]

            for s in steps:
                if callable(s["generator"]):
                    s["generator"] = s["generator"](db_type)

            test = ExecutionPlanTest(steps, db_type, schema_for_metrics, test_name=f"{tag}_{u}u")
            test.build(engine, meta_obj)
            test.run(
                engine,
                meta_obj,
                locust_config={
                    "wait_time_min": 0.4,
                    "wait_time_max": 0.7,
                    "users": u,
                    "spawn_rate": 5,
                    "run_time": run_time,
                },
            )

            # איסוף תוצאות וכתיבה ל-Supabase
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
                    schema=schema_for_metrics,  # נשאר 'mydb' להצגה
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




def _run_named_suite(label: str, test_names: list[str], run_id_override: Optional[int] = None) -> Dict[str, Any]:
    """Run a named benchmark suite with a list of test plan names."""

    tag = label.lower().replace(" ", "_")
    if run_id_override:
        run_id = run_id_override
        run_uid = "unknown"  # or fetch from DB if needed
    else:
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

        print("🕒 Cooling‑down 30 s…")
        time.sleep(30)

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

    # 1. קריאות קלות – Lookup / Dashlets
    "basic": {
        "tag": "basic",
        "users": [3],
        #"run_time": 90,
        "run_time": 25,
        "spread": True,
        "steps_override": lambda s: (
                basic_select(":db", s["t1"], repeat=30) +
                            basic_select(":db", s["t4"], repeat=10) +
                            filtered_test(":db", s["t1"], repeat=25) +
                            pagination_test(":db", s["t2"], repeat=20) +
                            pure_count(":db", s["t3"], repeat=10) +
                            aggregation_test(":db", s["t2"], repeat=5)
        )
    },

    # 2. עומס כבד – דיווחים / BI
    "advanced": {
        "tag": "advanced",
        "users": [18],
        "run_time": 150,
        "spread": True,
        "steps_override": lambda s: (
            deep_join_longest(":db",  s["t7"]) +             # 5 %
            window_query(":db",      s["t6"], repeat=6) +    # 15 %
            aggregation_test(":db",  s["t6"], repeat=6) +    # 15 %
            group_by(":db",          s["t5"], repeat=6) +    # 15 %
            pagination_test(":db",   s["t4"], repeat=10) +   # 25 %
            basic_select(":db",      s["t3"], repeat=8) +    # 20 %
            pure_count(":db",        s["t6"], repeat=4)      # 5 %
        )
    },

    # 3. Balanced  – יום עבודה ממוצע
    "balanced": {
        "tag": "balanced",
        "users": [10, 40], # should be 6, 12
        "run_time": 150, # should be 180,
        "spread": True,
        "steps_override": lambda s: (
                basic_select(":db", s["t1"], repeat=10) +
                basic_select(":db", s["t2"], repeat=20) +
                basic_select(":db", s["t3"], repeat=30) +
                pagination_test(":db", s["t1"], repeat=15) +
                filtered_test(":db", s["t2"], repeat=20) +
                pagination_test(":db", s["t2"], repeat=15) +
                filtered_test(":db", s["t3"], repeat=20) +

                # ---------- 25 % queries – medium ----------
                aggregation_test(":db", s["t5"], repeat=40) +
                group_by(":db", s["t5"], repeat=40) +
                pure_count(":db", s["t4"], repeat=30) +
                basic_select(":db", s["t4"], repeat=25) +
                basic_select(":db", s["t5"], repeat=25) +
                filtered_test(":db", s["t4"], repeat=25) +
                filtered_test(":db", s["t5"], repeat=25) +


                # ---------- 15 % queries – heavy ----------
                basic_select(":db", s["t7"], repeat=10) +
                basic_select(":db", s["t6"], repeat=10) +
                filtered_test(":db", s["t7"], repeat=20) +
                filtered_test(":db", s["t6"], repeat=15) +

                deep_join_default(":db", selector=s["t7"], join_size=3) +  # runs once per repeat
                deep_join_default(":db", selector=s["t7"], join_size=3) +  # runs once per repeat
                deep_join_default(":db", selector=s["t7"], join_size=3) +  # runs once per repeat
                deep_join_default(":db", selector=s["t7"], join_size=3) +  # runs once per repeat
                deep_join_default(":db", selector=s["t7"], join_size=3) +  # runs once per repeat
                deep_join_default(":db", selector=s["t7"], join_size=3) +  # runs once per repeat
                deep_join_longest(":db", s["t6"]) +  # runs once per repeat
                deep_join_longest(":db", s["t6"]) +  # runs once per repeat
                deep_join_longest(":db", s["t6"]) +  # runs once per repeat
                deep_join_longest(":db", s["t6"]) +  # runs once per repeat
                deep_join_longest(":db", s["t6"]) +  # runs once per repeat
                deep_join_longest(":db", s["t6"]) +  # runs once per repeat
                deep_join_longest(":db", s["t6"]) +  # runs once per repeat
                deep_join_longest(":db", s["t6"]) +  # runs once per repeat
                deep_join_default(":db", selector=s["t7"], join_size=3) +  # runs once per repeat
                deep_join_default(":db", selector=s["t7"], join_size=3) +  # runs once per repeat
                deep_join_default(":db", selector=s["t7"], join_size=3) +  # runs once per repeat
                deep_join_default(":db", selector=s["t7"], join_size=3) +  # runs once per repeat
                deep_join_default(":db", selector=s["t7"], join_size=3) +  # runs once per repeat
                deep_join_default(":db", selector=s["t7"], join_size=3) +  # runs once per repeat
                deep_join_longest(":db", s["t6"]) +  # runs once per repeat
                deep_join_longest(":db", s["t6"]) +  # runs once per repeat
                deep_join_longest(":db", s["t6"]) +  # runs once per repeat
                deep_join_longest(":db", s["t6"]) +  # runs once per repeat
                deep_join_longest(":db", s["t6"]) +  # runs once per repeat
                deep_join_longest(":db", s["t6"]) +  # runs once per repeat
                deep_join_longest(":db", s["t6"]) +  # runs once per repeat
                deep_join_longest(":db", s["t6"]) +  # runs once per repeat
                group_by(":db", s["t6"], repeat=20) +
                group_by(":db", s["t7"], repeat=20)
        )
    }
}

# Suite functions

def run_basic_queries_suite(run_id: Optional[int] = None) -> Dict[str, Any]:
    return _run_named_suite("Basic Queries", ["basic"], run_id)

def run_advanced_workload_suite(run_id: Optional[int] = None) -> Dict[str, Any]:
    return _run_named_suite("Advanced Workload", ["advanced"], run_id)

def run_balanced_suite(run_id: Optional[int] = None) -> Dict[str, Any]:
    return _run_named_suite("Balanced Suite", ["balanced"], run_id)

#
# TEST_PLANS: Dict[str, Callable[..., Dict[str, Any]]] = {
#     "basic":   lambda: _execute_test_plan(**TEST_CONFIGS["basic"]),
#     "advanced": lambda: _execute_test_plan(**TEST_CONFIGS["advanced"]),
#     "balanced": lambda: _execute_test_plan(**TEST_CONFIGS["balanced"]),
# }
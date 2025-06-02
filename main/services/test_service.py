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

    # 1. קריאות קלות – Lookup / Dashlets
    "basic": {
        "tag": "basic",
        "users": [3],
        "run_time": 45,
        "spread": True,
        "steps_override": lambda s: (
                basic_select(":db", s["t1"], repeat=30) +  # 30 %
                basic_select(":db", s["t4"], repeat=10) +  # 10 %
                filtered_test(":db", s["t1"], repeat=25) +  # 25 %
                pagination_test(":db", s["t2"], repeat=20) +  # 20 %
                pure_count(":db", s["t3"], repeat=10) +  # 10 %
                aggregation_test(":db", s["t2"], repeat=5)  # 5 %
        )
    },

    # 2. עומס כבד – דיווחים / BI
    "advanced": {
        "tag": "advanced",
        "users": [18],
        "run_time": 120,
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
        "users": [6, 12],
        "run_time": 90,
        "spread": True,
        "steps_override": lambda s: (
            # 60 % קלות
            basic_select(":db",     s["t1"], repeat=24) +
            pagination_test(":db",  s["t2"], repeat=12) +
            filtered_test(":db",    s["t2"], repeat=12) +

            # 25 % בינוניות
            aggregation_test(":db", s["t3"], repeat=8) +
            group_by(":db",         s["t3"], repeat=8) +

            # 15 % כבדות
            window_query(":db",     s["t5"], repeat=4)  +
            deep_join_default(":db", selector=s["t4"], join_size=3) +
            basic_select(":db",     s["t6"], repeat=4) +
            basic_select(":db",     s["t7"], repeat=4)
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


TEST_PLANS: Dict[str, Callable[..., Dict[str, Any]]] = {
    "basic":   lambda: _execute_test_plan(**TEST_CONFIGS["basic"]),
    "advanced": lambda: _execute_test_plan(**TEST_CONFIGS["advanced"]),
    "balanced": lambda: _execute_test_plan(**TEST_CONFIGS["balanced"]),
}





def testing() -> Dict[str, Any]:
    config = TEST_CONFIGS["testing"]
    result = _execute_test_plan(**config)

    # Update metadata status for individual test
    try:
        update_metadata_status(
            test_id=result["run_id"],
            status="completed",
            summary_json={"test_type": "individual", "test_name": "testing"},
            recommendations="Individual testing test completed successfully",
            finished_at=datetime.utcnow().isoformat()
        )
    except Exception as e:
        print(f"❌ Failed to update metadata for individual test: {e}")

    return result


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
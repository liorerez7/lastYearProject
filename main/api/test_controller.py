import asyncio

from fastapi import APIRouter, HTTPException, Body, BackgroundTasks
from typing import Literal
from main.services import test_service

testRouter = APIRouter()

# it has to be compatible with the UI in Home.js
TEST_TYPE_TO_FUNCTION = {
    "Basic Queries": test_service.run_basic_queries_suite,
    "Advanced Workload": test_service.run_advanced_workload_suite,
    "Balanced Suite": test_service.run_balanced_suite,
}


@testRouter.post("/create-simple-test")
def create_simple_test(
    test_type: Literal["Basic Queries", "Advanced Workload", "Balanced Suite"] = Body(..., embed=True),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    try:
        print(f"\n🎯 Starting suite for: {test_type}")

        run_id, run_uid = test_service.create_metadata_only(test_type)
        background_tasks.add_task(TEST_TYPE_TO_FUNCTION[test_type], run_id)

        return {
            "message": f"Suite '{test_type}' execution started",
            "test_id": run_id
        }

    except Exception as e:
        print("🔥 create_simple_test error:", e)
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, HTTPException, Body
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
        test_type: Literal["Basic Queries", "Advanced Workload", "Balanced Suite"] = Body(..., embed=True)
):
    try:
        print(f"\n🎯 RUNNING SUITE TYPE: {test_type}")
        test_data = TEST_TYPE_TO_FUNCTION[test_type]()
        print("✅ test_data returned:", test_data)

        return {
            "message": "Simple test created",
            "test_id": test_data["run_id"]
        }

    except Exception as e:
        print("🔥 create_simple_test error:", e)
        raise HTTPException(status_code=500, detail=str(e))

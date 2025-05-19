# from fastapi import APIRouter, HTTPException
# from main.services import test_service
#
# #CURRENT_PLAN = test_service.run_mix_workload
# #CURRENT_PLAN = test_service.run_multi_user_smoke
# #CURRENT_PLAN = test_service.run_index_stress
# CURRENT_PLAN = test_service.run_everything
#
# testRouter = APIRouter()
#
# @testRouter.post("/create-simple-test")
# def create_simple_test():
#     try:
#         test_data = CURRENT_PLAN()
#         print("Test data created:", test_data)
#         return {"message": "Simple test created", "test_id": test_data}
#     except Exception as e:
#         print("🔥 Caught Exception:", str(e))
#         raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, HTTPException, Body
from typing import Literal
from main.services import test_service

testRouter = APIRouter()

#it has to be compatible with the UI in Home.js
TEST_TYPE_TO_FUNCTION = {
    "Basic Queries": test_service.run_basic_queries_suite,
    "Advanced Workload": test_service.run_advanced_workload_suite,
    "Balanced Suite": test_service.run_balanced_suite,
}

@testRouter.post("/create-simple-test")
def create_simple_test(test_type: Literal["Basic Queries", "Advanced Workload", "Balanced Suite"] = Body(..., embed=True)):
    try:
        runner = TEST_TYPE_TO_FUNCTION.get(test_type)
        if not runner:
            raise ValueError(f"No test plan defined for '{test_type}'")
        test_data = runner()
        print("✅ Test executed:", test_data)
        return {"message": "Test executed", "test_id": test_data}
    except Exception as e:
        print("🔥 Caught Exception:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

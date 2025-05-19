# from fastapi import APIRouter, HTTPException
# from typing import List
#
# from main.services.test_service import create_simple_test_service, create_full_test_benchmark
#
# testRouter = APIRouter()
#
#
# @testRouter.post("/create-simple-test")
# def create_simple_test():
#     try:
#         test_data = create_full_test_benchmark()
#         print("Test data created:", test_data)
#         return {"message": "Simple test created", "test_id": test_data}
#     except Exception as e:
#         print("🔥 Caught Exception:", str(e))
#         raise HTTPException(status_code=500, detail=str(e))
#

# main/api/test_controller.py
from fastapi import APIRouter, HTTPException
from main.services import test_service

# בחר כאן איזו פונקציית בדיקה תופעל בריצה זו:
#CURRENT_PLAN = test_service.run_mix_workload
#CURRENT_PLAN = test_service.run_multi_user_smoke
#CURRENT_PLAN = test_service.run_index_stress  # ← זוהי הפעילה כרגע
CURRENT_PLAN = test_service.run_everything





testRouter = APIRouter()

@testRouter.post("/create-simple-test")
def create_simple_test():
    try:
        test_data = CURRENT_PLAN()
        print("Test data created:", test_data)
        return {"message": "Simple test created", "test_id": test_data}
    except Exception as e:
        print("🔥 Caught Exception:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

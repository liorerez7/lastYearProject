from fastapi import APIRouter
from main.services.test_service import create_test_service, create_simple_test_service
from typing import List
from fastapi import HTTPException
testRouter = APIRouter()



@testRouter.post("/create-simple-test")
def create_simple_test():
    try:
        test_data = create_simple_test_service()
        print("Test data created:", test_data)
        return {"message": "Simple test created", "test_id": test_data}
    except Exception as e:
        print("🔥 Caught Exception:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

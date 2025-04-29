from fastapi import APIRouter, HTTPException
from typing import List

from main.services.test_service import create_simple_test_service

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


@testRouter.get("/test1")
def test1():
    try:
        # Simulate some processing
        result = {"message": "Test 1 succes"}
        return result
    except Exception as e:
        print("🔥 Caught Exception:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    test_data = create_simple_test_service()
    print("Test data created:", test_data)
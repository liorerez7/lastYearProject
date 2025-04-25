from fastapi import APIRouter
from main.services.test_service import create_test_service, create_simple_test_service
from pydantic import BaseModel
from typing import List

testRouter = APIRouter()


class CreateTestRequest(BaseModel):
    user_id: str
    source_db: str
    destination_db: str
    schema: str
    label: str
    test_type: str
    generator: str
    parameters: dict
    queries: List[dict]
    stage: int = 1


@testRouter.post("/create-test")
def create_test(data: CreateTestRequest):
    test_id = create_test_service(data)
    return {"message": "Test created", "test_id": test_id}


@testRouter.post("/create-simple-test")
def create_simple_test():
    test_id = create_simple_test_service()
    return {"message": "Simple test created", "test_id": test_id}


if __name__ == '__main__':
    #runn the create_simle test
    test_id = create_simple_test_service()

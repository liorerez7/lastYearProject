from datetime import datetime
from models.test_model import TestMetadata, TestExecution
from main.services.dynamo_service import insert_item
from typing import List, Dict, Any


def create_test_service(data) -> str:
    test_id = f"user_{data.user_id}#test#{datetime.utcnow().isoformat()}"

    metadata = TestMetadata.create(
        user_id=data.user_id,
        source_db=data.source_db,
        destination_db=data.destination_db
    )
    metadata.test_id = test_id
    insert_item(metadata.to_dynamo_item())

    for db_type in ["mysql", "postgres"]:
        execution = TestExecution(
            test_id=test_id,
            db_type=db_type,
            test_type=data.test_type,
            schema=data.schema,
            queries=data.queries
        )
        insert_item(execution.to_dynamo_item())

    return test_id


def create_simple_test_service() -> dict[str, Any]:
    test_id = f"user_demo#test#{datetime.utcnow().isoformat()}"

    metadata = TestMetadata(
        test_id=test_id,
        cloud_provider="aws",
        source_db="mysql",
        destination_db="postgres",
        status="pending",
        mail="stam mail"
    )
    metadata_dict = metadata.to_dynamo_item()
    insert_item(metadata_dict)

    execution = TestExecution(
        test_id=test_id,
        timestamp=datetime.utcnow().isoformat(),
        db_type="mysql",
        test_type="filtered",
        schema="sakila",
        queries=[
            {
                "sql": "SELECT * FROM actor WHERE actor_id > 50;",
                "size": "small",
                "repeat": 1
            }
        ]

    )
    execution_dict = execution.to_dynamo_item()
    insert_item(execution_dict)

    return {
        "metadata": metadata_dict,
        "execution": execution_dict
    }

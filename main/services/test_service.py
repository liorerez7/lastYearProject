from datetime import datetime

from main.core.test_framework.plans.selector_helpers import get_size_based_selectors
from models.test_model import TestMetadata, TestExecution
from main.services.dynamo_service import insert_item
from typing import List, Dict, Any
from datetime import datetime
from models.test_model import TestMetadata, TestExecution
from main.services.dynamo_service import insert_item
from main.core.schema_analysis.connection.db_connector import DBConnector
from main.core.test_framework.execution_plan_test import ExecutionPlanTest
from main.core.test_framework.plans.basic_select_plans import basic_select  # או build_basic_select
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



def create_simple_test_service():
    # 1. צור מזהה טסט ייחודי
    test_id = f"user_demo#test#{datetime.utcnow().isoformat()}"

    # 2. צור metadata
    metadata = TestMetadata(
        test_id=test_id,
        cloud_provider="aws",
        source_db="mysql",
        destination_db="postgres",
        status="pending",
        mail="lior@example.com"
    )
    insert_item(metadata.to_dynamo_item())

    # 3. צור ובנה את תכנית הבדיקה
    schema = "employees"
    test_type = "basic_select"
    sizes = get_size_based_selectors(schema, "mysql")
    timestamp = datetime.utcnow().isoformat()

    execution_results = {}

    for db_type in ["mysql", "postgres"]:
        engine, metadata_obj = DBConnector(db_type).connect(schema)
        plan = basic_select(db_type, sizes["small"], repeat=1)

        test = ExecutionPlanTest(plan, db_type, schema, test_name=test_type)
        built = test.build(engine, metadata_obj)
        test.run(engine, metadata_obj)

        # 4. שמור execution עם built (ולא התוצאה)
        execution = TestExecution(
            test_id=test_id,
            timestamp=timestamp,
            db_type=db_type,
            test_type=test_type,
            schema=schema,
            queries=list(built.values())
        )
        insert_item(execution.to_dynamo_item())

        execution_results[db_type] = execution.to_dynamo_item()

    # 5. נחזיר ל־UI תוצאה ברורה
    return {
        "test_id": test_id,
        "execution": execution_results
    }

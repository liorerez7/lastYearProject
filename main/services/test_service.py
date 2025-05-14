import statistics
from datetime import datetime

from main.core.test_framework.plans.aggregation_plans import aggregation_test
from main.core.test_framework.plans.deep_join_plans import deep_join_longest
from main.core.test_framework.plans.filtered_query_plans import filtered_test
from main.core.test_framework.plans.group_by_plans import group_by
from main.core.test_framework.plans.pagination_plans import pagination_test
from main.core.test_framework.plans.pure_count_plans import pure_count
from main.core.test_framework.plans.reverse_join_plans import reverse_join
from main.core.test_framework.plans.selector_helpers import get_size_based_selectors
from main.core.test_framework.plans.workload_test_chat import realistic_workload
from main.services.supabase_service import insert_metadata, insert_execution
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
    #insert_item(metadata.to_dynamo_item())
    insert_metadata(metadata.to_dynamo_item())

    # 3. צור ובנה את תכנית הבדיקה
    schema = "employees"
    test_type = "basic_select"
    sizes = get_size_based_selectors(schema, "mysql")
    timestamp = datetime.utcnow().isoformat()

    execution_results = {}

    for db_type in ["mysql", "postgres"]:
        engine, metadata_obj = DBConnector(db_type).connect(schema)
        plan = (basic_select(db_type, sizes["small"], repeat=1) +
                basic_select(db_type, sizes["large"], repeat=2))

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
            queries=list(test.get_built_plan_with_durations().values())
        )
        #insert_item(execution.to_dynamo_item())
        insert_execution(execution.to_dynamo_item())

        execution_results[db_type] = execution.to_dynamo_item()

    # 5. נחזיר ל־UI תוצאה ברורה
    return {
        "test_id": test_id,
        "execution": execution_results
    }

def create_full_test_benchmark():
    test_id = f"user_demo#test#{datetime.utcnow().isoformat()}"

    metadata = TestMetadata(
        test_id=test_id,
        cloud_provider="aws",
        source_db="mysql",
        destination_db="postgres",
        status="pending",
        mail="lior@example.com"
    )
    insert_metadata(metadata.to_dynamo_item())

    schema = "extendedEmp"
    sizes = get_size_based_selectors(schema, "mysql")
    timestamp = datetime.utcnow().isoformat()
    execution_results = {}

    for db_type in ["mysql", "postgres"]:
        engine, metadata_obj = DBConnector(db_type).connect(schema)

        steps = (
            basic_select(db_type, sizes["small"], repeat=3) +
            basic_select(db_type, sizes["large"], repeat=3) +
            group_by(db_type, sizes["medium"], repeat=5) +
            aggregation_test(db_type, sizes["large"], repeat=5) +
            deep_join_longest(db_type, sizes["large"]) +
            filtered_test(db_type, sizes["medium"], repeat=3) +
            pure_count(db_type, sizes["large"], repeat=2) +
            pagination_test(db_type, sizes["large"], repeat=2)
        )

        test = ExecutionPlanTest(steps, db_type, schema, test_name="extreme_suite")
        test.build(engine, metadata_obj)
        test.run(engine, metadata_obj)

        execution = TestExecution(
            test_id=test_id,
            timestamp=timestamp,
            db_type=db_type,
            test_type="extreme_suite",
            schema=schema,
            queries=list(test.get_built_plan_with_durations().values())
        )
        insert_execution(execution.to_dynamo_item())
        execution_results[db_type] = execution.to_dynamo_item()

    return {
        "test_id": test_id,
        "execution": execution_results
    }




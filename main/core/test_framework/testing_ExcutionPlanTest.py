from main.config.db_config import POSTGRES_CONFIG
from main.core.test_framework.execution_plan_test import ExecutionPlanTest
from main.core.test_framework.plans.deep_join_plan import deep_join_plan
from main.core.DBcomare.query_generator.testWithAlchmey import load_metadata


if __name__ == '__main__':
    postgres_url = (
        f"postgresql+psycopg2://{POSTGRES_CONFIG['user']}:{POSTGRES_CONFIG['password']}"
        f"@{POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}/{POSTGRES_CONFIG['dbname']}"
    )
    engine, metadata = load_metadata(postgres_url, schema="sakila")

    test = ExecutionPlanTest(deep_join_plan())
    test.preview(metadata)  # No engine needed

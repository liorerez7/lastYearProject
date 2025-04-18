from main.config.db_config import POSTGRES_CONFIG
from main.core.test_framework.execution_plan_test import ExecutionPlanTest
from main.core.test_framework.plans.deep_join_plan import deep_join_plan
from main.core.db_compare.query_generator import test_with_alchemy

if __name__ == '__main__':
    postgres_url = (
        f"postgresql+psycopg2://{POSTGRES_CONFIG['user']}:{POSTGRES_CONFIG['password']}"
        f"@{POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}/{POSTGRES_CONFIG['dbname']}"
    )

    engine, metadata = testWithAlchmey.load_metadata(postgres_url, schema="sakila")
    test = ExecutionPlanTest(deep_join_plan())

    test.run(engine,metadata)
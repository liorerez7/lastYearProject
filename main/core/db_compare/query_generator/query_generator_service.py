# query_generator_service.py
from main.core.db_compare.query_generator.query_strategy_registry import QUERY_GENERATOR_REGISTRY


class QueryGeneratorService:

    """
    Responsible for generating SQL queries based on a given test type,
    schema metadata, and the database engine type (e.g., MySQL, PostgreSQL).

    This class acts as a bridge between the caller and the specific query generation strategy.
    """

    def __init__(self, test_type, schema_metadata, db_type):
        if test_type not in QUERY_GENERATOR_REGISTRY:
            raise ValueError(f"Unsupported test type: {test_type}")

        self.generator = QUERY_GENERATOR_REGISTRY[test_type]()
        self.schema_metadata = schema_metadata
        self.db_type = db_type

    def generate(self, selector=None):
        return self.generator.generate_query(self.schema_metadata, self.db_type, selector=selector)


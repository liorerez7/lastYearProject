# query_generator_service.py

from main.core.db_compare.query_generator.query_generator_registry_defaults import build_strategy


class QueryGeneratorService:
    """
    Responsible for generating SQL queries based on a given test type,
    schema metadata, and the database engine type (e.g., MySQL, PostgreSQL).
    This class acts as a bridge between the caller and the specific query generation strategy.
    """

    def __init__(self, test_type, db_type, strategy_config=None):
        self.generator = build_strategy(test_type, strategy_config or {})
        self.db_type = db_type

    def generate(self, schema_metadata, selector=None):
        return self.generator.generate_query(schema_metadata, self.db_type, selector=selector)

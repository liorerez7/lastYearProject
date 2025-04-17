# generator_manager.py
from main.core.DBcomare.query_generator.registry import QUERY_GENERATOR_REGISTRY


class QueryGeneratorManager:
    """
    this class is responsible for managing the query generation process
     it will take the test type and schema metadata as input
    and will use the appropriate query generator to generate the query
    """

    def __init__(self, test_type, schema_metadata, db_type):
        if test_type not in QUERY_GENERATOR_REGISTRY:
            raise ValueError(f"Unsupported test type: {test_type}")

        self.generator = QUERY_GENERATOR_REGISTRY[test_type]()
        self.schema_metadata = schema_metadata
        self.db_type = db_type

    def generate(self):
        return self.generator.generate_query(self.schema_metadata, self.db_type)

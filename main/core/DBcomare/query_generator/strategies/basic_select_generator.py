from sqlalchemy.schema import MetaData
from main.core.DBcomare.query_generator.base_strategy import QueryGenerationStrategy


class SimpleQueryGenerator(QueryGenerationStrategy):
    def generate_query(self, metadata: MetaData) -> str:
        # Get all table names from the metadata
        table_names = list(metadata.tables.keys())

        if not table_names:
            raise ValueError("❌ No tables found in the schema.")

        # Always pick the first table in the metadata (deterministic and simple)
        table_name = table_names[0]

        return f"SELECT * FROM {table_name} LIMIT 100;"
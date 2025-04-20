from typing import Optional, Dict

from sqlalchemy import text

from main.core.schema_analysis.connection.db_connector import DBConnector
from main.core.query_generation.query_generator import QueryGeneratorService
from main.core.query_generation.query_generator import SelectorExplorer


class QueryExecutionHandler:
    def __init__(self, db_type: str, test_type: str, schema: str, db_url: Optional[str] = None,
                 strategy_config: Optional[Dict] = None):
        self.db_type = db_type
        self.test_type = test_type
        self.schema = schema
        self.db_url = db_url
        self.strategy_config = strategy_config or {}
        self.connector = DBConnector(db_type, db_url=db_url)

    def run(self, sample_size: int = 5, selector: Optional[int] = None):
        engine, metadata = self.connector.connect(schema=self.schema)

        # generator is an instance of the QueryGeneratorService thats holds inside the strategy class
        # (for example DeepJoinQueryStrategy)

        generator = QueryGeneratorService(self.test_type, self.db_type, strategy_config=self.strategy_config)
        query = generator.generate(metadata,selector)

        if not query or not query.strip().lower().startswith("select"):
            print(f"⚠️ Selector {selector} failed to generate a valid query. Trying to find a fallback selector...")

            explorer = SelectorExplorer(type(generator.generator), metadata, self.db_type)
            valid_selector = explorer.find_first_valid_selector()  # tries 1-100 selectors

            if valid_selector == -1:
                print("❌ No valid selector found for this strategy and schema.")
                return
            print(f"🔄 Using fallback selector: {valid_selector}")
            query = generator.generate(metadata,valid_selector)

        print("📄 Generated SQL:\n", query)

        with engine.connect() as conn:
            results = conn.execute(text(query)).fetchmany(sample_size)

        print("\n🧪 Sample Results (5 rows):")
        for row in results:
            print(dict(row._mapping))


def test_execution_handler_deep_join():
    # Initialize the execution handler with custom strategy configuration
    handler = QueryExecutionHandler(
        db_type="mysql",
        test_type="deep_join",
        schema="sakila",
        strategy_config={
            "longest": True
        }
    )

    print("\n🚀 Running Deep Join Execution Test with Custom Config...\n")
    # Run the handler with a specific selector (selector controls the starting node in the graph)
    handler.run(selector=2)

if __name__ == "__main__":
    test_execution_handler_deep_join()
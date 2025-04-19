from typing import Optional

from sqlalchemy import text

from main.core.db_compare.connection.db_connector import DBConnector
from main.core.db_compare.query_generator.query_generator_service import QueryGeneratorService
from main.core.db_compare.query_generator.selector_explorer import SelectorExplorer


class QueryExecutionHandler:
    def __init__(self, db_type: str, test_type: str, schema: str, db_url: Optional[str] = None):
        self.db_type = db_type
        self.test_type = test_type
        self.schema = schema
        self.connector = DBConnector(db_type, db_url=db_url)
    def run(self, sample_size: int = 5, selector: Optional[int] = None):
        engine, metadata = self.connector.connect(schema=self.schema)
        print("✅ Tables loaded:", list(metadata.tables.keys()))

        generator = QueryGeneratorService(self.test_type, metadata, self.db_type)
        query = generator.generate(selector=selector)

        if not query or not query.strip().lower().startswith("select"):
            print(f"⚠️ Selector {selector} failed to generate a valid query. Trying to find a fallback selector...")

            explorer = SelectorExplorer(type(generator.generator), metadata, self.db_type)
            valid_selector = explorer.find_first_valid_selector() # tries 1-100 selectors

            if valid_selector == -1:
                print("❌ No valid selector found for this strategy and schema.")
                return
            print(f"🔄 Using fallback selector: {valid_selector}")
            query = generator.generate(selector=valid_selector)

        print("📄 Generated SQL:\n", query)

        with engine.connect() as conn:
            results = conn.execute(text(query)).fetchmany(sample_size)

        print("\n🧪 Sample Results (5 rows):")
        for row in results:
            print(dict(row._mapping))

if __name__ == "__main__":
    handler = QueryExecutionHandler(
        db_type="mysql",
        test_type="deep_join",
        schema="sakila"
    )
    handler.run(selector=0)
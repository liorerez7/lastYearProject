from typing import Tuple, Optional

from sqlalchemy import create_engine, MetaData, text

from main.config.db_config import POSTGRES_CONFIG
from main.core.DBcomare.query_generator.strategies.deep_join_generator import DeepJoinGenerator


def load_metadata(db_url: str, schema: Optional[str] = None) -> Tuple:
    """
    Loads the metadata and engine for a given database URL and schema.
    """
    engine = create_engine(db_url)
    metadata = MetaData()
    metadata.reflect(bind=engine, schema=schema)
    return engine, metadata

if __name__ == '__main__':
    postgres_url = (
        f"postgresql+psycopg2://{POSTGRES_CONFIG['user']}:{POSTGRES_CONFIG['password']}"
        f"@{POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}/{POSTGRES_CONFIG['dbname']}"
    )
    # Load metadata + engine
    engine, metadata = load_metadata(postgres_url, schema="sakila")
    print(metadata.tables.keys())
    # Generate query
    generator = DeepJoinGenerator()
    query = generator.generate_query(metadata)
    print("📄 Generated SQL:\n", query)

    # Run the query
    with engine.connect() as conn:
        result = conn.execute(text(query)).fetchmany(5)
        print("\n🧪 Sample Results (5 rows):")
        for row in result:
            print(dict(row))

from typing import Tuple, Optional
from sqlalchemy import create_engine, MetaData, text
from main.config.db_config import POSTGRES_CONFIG, MYSQL_CONFIG
from main.core.db_compare.query_generator.query_generator_service import QueryGeneratorService

def load_metadata(db_url: str, schema: Optional[str] = None) -> Tuple:
    engine = create_engine(db_url)
    metadata = MetaData()
    metadata.reflect(bind=engine, schema=schema)
    return engine, metadata

def get_db_url(db_type: str) -> str:
    if db_type == "mysql":
        cfg = MYSQL_CONFIG
        return f"mysql+pymysql://{cfg['user']}:{cfg['password']}@{cfg['host']}:{cfg['port']}/{cfg['database']}"
    elif db_type == "postgres":
        cfg = POSTGRES_CONFIG
        return f"postgresql+psycopg2://{cfg['user']}:{cfg['password']}@{cfg['host']}:{cfg['port']}/{cfg['dbname']}"
    else:
        raise ValueError(f"Unsupported db_type: {db_type}")

def run_query(engine, query: str, sample_size: int = 5):
    with engine.connect() as conn:
        results = conn.execute(text(query)).fetchmany(sample_size)
        return [dict(row._mapping) for row in results]

def main(db_type: str, test_type: str, schema: str):
    db_url = get_db_url(db_type)
    engine, metadata = load_metadata(db_url, schema=schema)

    print("✅ Tables loaded:", list(metadata.tables.keys()))

    generator = QueryGeneratorService(test_type, metadata, db_type)
    query = generator.generate()
    print("📄 Generated SQL:\n", query)

    results = run_query(engine, query)
    print("\n🧪 Sample Results (5 rows):")
    for row in results:
        print(row)

if __name__ == '__main__':
    # Change parameters here:
    main(db_type="mysql", test_type="deep_join", schema="sakila")

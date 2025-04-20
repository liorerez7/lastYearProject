rom main.core.db_compare.schema_inspector.postgres_schema_reader import PostgreSQLSchemaReader
from main.config.db_config import POSTGRES_CONFIG

def main():
    reader = PostgreSQLSchemaReader(POSTGRES_CONFIG)

    tables = reader.get_tables()
    print("📄 Tables:")
    for schema, table in tables:
        print(f"{schema}.{table}")

        print(f"\n🔍 Table: {table}")
        columns = reader.get_columns(table)  # תוכל לעדכן גם את זו אם תרצה שתהיה גנרית
        for col in columns:
            print(f" - {col['Field']} ({col['Type']})")

        row_count = reader.get_row_count(schema, table)
        print(f"   → Row count: {row_count}")

    reader.close()

if __name__ == "__main__":
    main()
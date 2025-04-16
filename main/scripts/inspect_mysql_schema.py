from main.core.DBcomare.schema_inspector.mysql_schema_reader import MySQLSchemaReader
from main.config.db_config import MYSQL_CONFIG

def main():
    reader = MySQLSchemaReader(MYSQL_CONFIG)

    print("📄 Tables:")
    tables = reader.get_tables()
    print(tables)

    for table in tables:
        print(f"\n🔍 Table: {table}")
        columns = reader.get_columns(table)
        for col in columns:
            print(f" - {col['Field']} ({col['Type']})")

        row_count = reader.get_row_count(table)
        print(f"   → Row count: {row_count}")

    print("\n🔗 Foreign Keys:")
    fks = reader.get_foreign_keys()
    for fk in fks:
        print(f" - {fk['TABLE_NAME']}.{fk['COLUMN_NAME']} → {fk['REFERENCED_TABLE_NAME']}.{fk['REFERENCED_COLUMN_NAME']}")

    reader.close()

if __name__ == "__main__":
    main()

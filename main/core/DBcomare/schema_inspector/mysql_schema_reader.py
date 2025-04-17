import mysql.connector
from sqlalchemy import create_engine, MetaData
class MySQLSchemaReader:
    def __init__(self, config):
        self.config = config
        self.conn = mysql.connector.connect(**config)
        self.cursor = self.conn.cursor(dictionary=True)

    def get_tables(self):
        self.cursor.execute("""
            SELECT table_schema, table_name 
            FROM information_schema.tables 
            WHERE table_type = 'BASE TABLE'
              AND table_schema NOT IN ('pg_catalog', 'information_schema');
        """)
        return [f"{schema}.{name}" for schema, name in self.cursor.fetchall()]

    def get_columns(self, table_name):
        self.cursor.execute(f"SHOW COLUMNS FROM {table_name};")
        return self.cursor.fetchall()

    def get_row_count(self, table_name):
        self.cursor.execute(f"SELECT COUNT(*) as count FROM {table_name};")
        return self.cursor.fetchone()["count"]

    def get_foreign_keys(self):
        self.cursor.execute("""
            SELECT TABLE_NAME, COLUMN_NAME, CONSTRAINT_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE REFERENCED_TABLE_SCHEMA = %s;
        """, (self.config["database"],))
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.conn.close()

def load_metadata(db_url: str) -> MetaData:
    engine = create_engine(db_url)
    metadata = MetaData()
    metadata.reflect(bind=engine)
    return metadata

import mysql.connector

class MySQLSchemaReader:
    def __init__(self, config):
        self.config = config
        self.conn = mysql.connector.connect(**config)
        self.cursor = self.conn.cursor(dictionary=True)

    def get_tables(self):
        self.cursor.execute("SHOW TABLES;")
        return [row[f'Tables_in_{self.config["database"]}'] for row in self.cursor.fetchall()]

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

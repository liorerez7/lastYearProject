import psycopg2


class PostgreSQLSchemaReader:
    def __init__(self, config):
        self.connection = psycopg2.connect(**config
        )
        self.cursor = self.connection.cursor()

    def get_tables(self):
        self.cursor.execute("""
            SELECT table_schema, table_name 
            FROM information_schema.tables
            WHERE table_type = 'BASE TABLE'
              AND table_schema NOT IN ('pg_catalog', 'information_schema')
            ORDER BY table_schema, table_name;
        """)
        return [(schema, name) for schema, name in self.cursor.fetchall()]

    def get_columns(self, table_name):
        self.cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = %s;
        """, (table_name,))
        return [{"Field": row[0], "Type": row[1]} for row in self.cursor.fetchall()]

    def get_row_count(self, schema, table_name):
        self.cursor.execute(f'SELECT COUNT(*) FROM "{schema}"."{table_name}";')
        return self.cursor.fetchone()[0]

    def get_foreign_keys(self):
        self.cursor.execute("""
            SELECT
              tc.table_name, kcu.column_name,
              ccu.table_name AS referenced_table,
              ccu.column_name AS referenced_column
            FROM 
              information_schema.table_constraints AS tc
              JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
              JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE constraint_type = 'FOREIGN KEY';
        """)
        return [
            {
                "TABLE_NAME": row[0],
                "COLUMN_NAME": row[1],
                "REFERENCED_TABLE_NAME": row[2],
                "REFERENCED_COLUMN_NAME": row[3]
            }
            for row in self.cursor.fetchall()
        ]

    def close(self):
        self.cursor.close()
        self.connection.close()

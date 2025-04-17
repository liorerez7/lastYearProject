from sqlalchemy.schema import MetaData

from main.core.DBcomare.query_generator.base_strategy import QueryGenerationStrategy


class DeepJoinGenerator(QueryGenerationStrategy):
    #TODO: the same query should be generated for both DBs
    def generate_query(self, metadata: MetaData) -> str:
        # בניית גרף קשרים לפי Foreign Keys
        fk_graph = self._build_fk_graph(metadata)
        join_chain = self._find_deep_join_path(fk_graph, limit=4)

        if not join_chain or len(join_chain) < 2:
            raise ValueError("❌ Not enough foreign key depth to generate deep join.")

        # התחלה עם הטבלה הראשונה
        first_table = join_chain[0]
        join_sql = f"SELECT * FROM {first_table}"

        # ביצוע JOIN בין כל טבלה לזו שאחריה בשרשרת
        for i in range(len(join_chain) - 1):
            left = join_chain[i]
            right = join_chain[i + 1]

            join_col = self._get_fk_column(metadata, left, right)
            pk_col = self._get_primary_key_column(metadata, right)

            join_sql += f"\nJOIN {right} ON {left}.{join_col} = {right}.{pk_col}"

        return join_sql + " LIMIT 100;"

    def _build_fk_graph(self, metadata):
        """
        בונה גרף קשרים בין טבלאות עם שמות מלאים (schema.table)
        """
        graph = {}
        for table_name, table in metadata.tables.items():
            graph[table_name] = []
            for fk in table.foreign_keys:
                ref_table = f"{fk.column.table.schema}.{fk.column.table.name}" if fk.column.table.schema else fk.column.table.name
                graph[table_name].append(ref_table)
        return graph

    def _find_deep_join_path(self, graph, limit=4):
        """
        חיפוש עומק (DFS) למציאת מסלול של טבלאות מקושרות עד לעומק מסוים
        """

        def dfs(table, path):
            if len(path) == limit:
                return path
            for neighbor in graph.get(table, []):
                if neighbor not in path:
                    result = dfs(neighbor, path + [neighbor])
                    if result:
                        return result
            return path

        for start in graph:
            path = dfs(start, [start])
            if len(path) >= 2:
                return path
        return []

    def _get_fk_column(self, metadata, from_table, to_table):
        """
        מוצא את שם העמודה בטבלת המקור שמצביעה על טבלת היעד
        """
        table = metadata.tables[from_table]
        for fk in table.foreign_keys:
            ref_table = f"{fk.column.table.schema}.{fk.column.table.name}" if fk.column.table.schema else fk.column.table.name
            if ref_table == to_table:
                return fk.parent.name
        raise ValueError(f"No FK from {from_table} to {to_table}")

    def _get_primary_key_column(self, metadata, table_name):
        """
        מחזיר את שם עמודת ה־Primary Key של טבלה
        """
        table = metadata.tables[table_name]
        pk = list(table.primary_key.columns)
        if not pk:
            raise ValueError(f"No primary key found for table: {table_name}")
        return pk[0].name

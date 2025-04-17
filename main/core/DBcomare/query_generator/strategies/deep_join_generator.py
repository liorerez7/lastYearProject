from sqlalchemy.schema import MetaData

from main.core.DBcomare.query_generator.base_strategy import QueryGenerationStrategy


class DeepJoinGenerator(QueryGenerationStrategy):
    #TODO: the same query should be generated for both DBs
    def generate_query(self, metadata: MetaData, db_type: str) -> str:
        # בניית גרף קשרים לפי Foreign Keys
        fk_graph = self._build_fk_graph(metadata)
        join_chain = self._find_deep_join_path(fk_graph, limit=4)

        if not join_chain or len(join_chain) < 2:
            raise ValueError("❌ Not enough foreign key depth to generate deep join.")

        first_table = join_chain[0]
        if db_type == "mysql":
            first_table = first_table.split(".")[-1]

        quote = "`" if db_type == "mysql" else ""  #depends on mysql or postgresql
        join_sql = f"SELECT * FROM {quote}{first_table}{quote}"

        # ביצוע JOIN בין כל טבלה לזו שאחריה בשרשרת
        for i in range(len(join_chain) - 1):
            left = join_chain[i]
            right = join_chain[i + 1]

            if db_type == "mysql":
                left = left.split(".")[-1]
                right = right.split(".")[-1]

            join_col = self._get_fk_column(metadata, left, right, db_type)
            pk_col = self._get_primary_key_column(metadata, right, db_type)

            join_sql += f"\nJOIN {quote}{right}{quote} ON {quote}{left}{quote}.{quote}{join_col}{quote} = {quote}{right}{quote}.{quote}{pk_col}{quote}"

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

    def _get_fk_column(self, metadata, from_table, to_table, db_type: str):
        """
        מוצא את שם העמודה בטבלת המקור שמצביעה על טבלת היעד
        """
        if db_type == "mysql":
            from_table = from_table.split(".")[-1]
            to_table = to_table.split(".")[-1]

        table_key = from_table
        if db_type == "mysql":
            # חפש את שם הטבלה המלא (כולל סכמה) במידת הצורך
            matching_keys = [k for k in metadata.tables.keys() if k.endswith(f".{from_table}") or k == from_table]
            if not matching_keys:
                raise ValueError(f"❌ Table '{from_table}' not found in metadata.")
            table_key = matching_keys[0]

        table = metadata.tables[table_key]
        for fk in table.foreign_keys:
            ref_table = f"{fk.column.table.schema}.{fk.column.table.name}" if fk.column.table.schema else fk.column.table.name

            if ref_table.endswith(f".{to_table}") or ref_table == to_table:
                return fk.parent.name

        raise ValueError(f"No FK from {from_table} to {to_table}")

    def _get_primary_key_column(self, metadata, table_name, db_type: str):
        """
        מחזיר את שם עמודת ה־Primary Key של טבלה
        """
        original_key = table_name
        if db_type == "mysql":
            # חפש את שם הטבלה שמסתיים בשם הנתון (בלי הסכמה)
            matching_keys = [k for k in metadata.tables.keys() if k.endswith(f".{table_name}") or k == table_name]
            if not matching_keys:
                raise ValueError(f"❌ Table '{table_name}' not found in metadata.")
            original_key = matching_keys[0]

        table = metadata.tables[original_key]
        pk = list(table.primary_key.columns)
        if not pk:
            raise ValueError(f"No primary key found for table: {original_key}")
        return pk[0].name


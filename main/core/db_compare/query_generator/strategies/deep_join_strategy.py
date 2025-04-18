from sqlalchemy.schema import MetaData
from main.core.db_compare.query_generator.base_query_strategy import BaseQueryStrategy
from main.core.db_compare.query_generator.utils.table_utils import (
    build_foreign_key_graph,
    find_deep_join_path,
    get_quote_char,
    normalize_table_name,
    get_foreign_key_column,
    get_primary_key_column,
)


class DeepJoinQueryStrategy(BaseQueryStrategy):
    def generate_query(self, metadata: MetaData, db_type: str) -> str:
        fk_graph = build_foreign_key_graph(metadata)
        join_chain = find_deep_join_path(fk_graph, limit=4)

        if not join_chain or len(join_chain) < 2:
            raise ValueError("❌ Not enough foreign key depth to generate deep join.")

        quote = get_quote_char(db_type)
        first_table = normalize_table_name(join_chain[0], db_type)
        join_sql = f"SELECT * FROM {quote}{first_table}{quote}"

        for i in range(len(join_chain) - 1):
            left_raw = join_chain[i]
            right_raw = join_chain[i + 1]
            left = normalize_table_name(left_raw, db_type)
            right = normalize_table_name(right_raw, db_type)

            join_col = get_foreign_key_column(metadata, left, right, db_type)
            pk_col = get_primary_key_column(metadata, right, db_type)

            join_sql += (
                f"\nJOIN {quote}{right}{quote} "
                f"ON {quote}{left}{quote}.{quote}{join_col}{quote} = "
                f"{quote}{right}{quote}.{quote}{pk_col}{quote}"
            )

        return join_sql + " LIMIT 100;"

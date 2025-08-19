from main.core.query_generation.selector_explorer import SelectorExplorer
from main.core.query_generation.strategies.aggregation_query_strategy import AggregationQueryStrategy
from main.core.query_generation.strategies.basic_select_strategy import BasicSelectQueryStrategy
from main.core.query_generation.strategies.deep_join_strategy import DeepJoinQueryStrategy
from main.core.query_generation.strategies.filtered_query_strategy import FilteredQueryStrategy
from main.core.query_generation.strategies.group_by_query_strategy import GroupByQueryStrategy
from main.core.query_generation.strategies.large_offset_query_strategy import LargeOffsetQueryStrategy
from main.core.query_generation.strategies.pagination_query_strategy import PaginationQueryStrategy
from main.core.query_generation.strategies.pure_count_query_strategy import PureCountQueryStrategy
from main.core.query_generation.strategies.recursive_cte_query_strategy import RecursiveCTEQueryStrategy
from main.core.query_generation.strategies.reverse_join_strategy import ReverseJoinQueryStrategy
from main.core.query_generation.strategies.window_query_strategy import WindowQueryStrategy
from main.core.query_generation.utils.table_access_utils import resolve_table_key
from main.core.schema_analysis.connection.db_connector import DBConnector
from main.core.schema_analysis.table_profiler import get_rowcounts, pick_s_m_l_selectors
from sqlalchemy import text as _text


STRATEGY_SELECTOR_MAP = {
    "deep_join": DeepJoinQueryStrategy,
    "basic_select": BasicSelectQueryStrategy,
    "aggregation": AggregationQueryStrategy,
    "filtered": FilteredQueryStrategy,
    "group_by": GroupByQueryStrategy,
    "reverse_join": ReverseJoinQueryStrategy,
    "pagination": PaginationQueryStrategy,
    "pure_count": PureCountQueryStrategy,
    "window_query": WindowQueryStrategy,
    "large_offset": LargeOffsetQueryStrategy,
    "recursive_cte": RecursiveCTEQueryStrategy,

}


def find_selector_for(test_type: str, schema_metadata, db_type: str) -> int:
    strategy_class = STRATEGY_SELECTOR_MAP.get(test_type)
    if not strategy_class:
        raise ValueError(f"No selector strategy registered for '{test_type}'")

    explorer = SelectorExplorer(strategy_class, schema_metadata, db_type)
    selector = explorer.find_first_valid_selector()

    if selector == -1:
        raise ValueError(f"❌ No valid selector found for test type '{test_type}' on {db_type}")

    return selector

# def get_size_based_selectors(schema: str,
#                              db_type: str = "mysql") -> dict[str, int]:
#     """
#     Compute selectors for small / medium / large tables.
#     Called once before the plan is built.
#     """
#     conn = DBConnector(db_type)
#     engine, metadata = conn.connect(schema)
#     counts = get_rowcounts(engine, schema)
#     return pick_s_m_l_selectors(metadata, db_type, counts)

def get_size_based_selectors(schema: str, db_type: str = "mysql") -> dict[str, int]:
    conn = DBConnector(db_type)
    engine, metadata = conn.connect(schema)

    # --- NEW: make sure Postgres looks at the right schema ---
    if db_type.lower() == "postgres":
        with engine.connect() as c:
            c.execute(_text(f'SET search_path TO "{schema}"'))
        metadata.clear()
        # רפלקציה מפורשת על הסכמה
        metadata.reflect(bind=engine, schema=schema)

    # לוג/בדיקת sanity
    table_keys = sorted(metadata.tables.keys())
    if not table_keys:
        print(f"⚠️ get_size_based_selectors: no tables found for {db_type} schema='{schema}'")
        return {}

    counts = get_rowcounts(engine, schema)
    return pick_s_m_l_selectors(metadata, db_type, counts)








def get_spread_selectors(schema: str,
                         db_type: str = "mysql",
                         sample_count: int = 7) -> dict[str, int]:
    """
    Return {"t1": selector, ..., "tn": selector} based on spread of table sizes.
    """
    conn = DBConnector(db_type)
    engine, metadata = conn.connect(schema)
    rowcounts = get_rowcounts(engine, schema)  # Sorted from largest to smallest

    if not rowcounts:
        return {}

    total_tables = len(rowcounts)
    step = max(1, total_tables // sample_count)
    chosen_tables = rowcounts[::-1][::step][:sample_count]  # from smallest upward

    def selector_for(table_name: str) -> int:
        resolved = resolve_table_key(metadata, table_name)
        if resolved is None:
            raise ValueError(f"Table '{table_name}' not found in metadata")
        table_keys = sorted(metadata.tables.keys())
        return table_keys.index(resolved.key)

    return {f"t{i+1}": selector_for(tbl) for i, (tbl, _) in enumerate(chosen_tables)}


def get_adaptive_selectors(schema: str, db_type: str = "mysql",
                           target_count: int = 7) -> dict[str, int]:
    """
    Return {"t1": selector, ..., "t7": selector} based on table sizes,
    always providing exactly target_count (default 7) selectors.

    Works reliably with any number of tables:
    - Tables are distributed by size from smallest (t1) to largest (t7)
    - If fewer than target_count tables exist, we use a smarter distribution strategy
    - If more than target_count tables exist, we'll sample across the size distribution

    Returns a dict mapping logical table names (t1, t2, ...) to selector values.

    Args:
        schema: Database schema name
        db_type: Database type, e.g. "mysql" or "postgres"
        target_count: Number of selectors to return (default: 7)
    """
    conn = DBConnector(db_type)
    engine, metadata = conn.connect(schema)

    if db_type.lower() == "postgres":
        with engine.connect() as c:
            c.execute(_text(f'SET search_path TO "{schema}"'))
        metadata.clear()
        metadata.reflect(bind=engine, schema=schema)

    table_keys = sorted(metadata.tables.keys())
    if not table_keys:
        print(f"⚠️ get_adaptive_selectors: no tables found for {db_type} schema='{schema}'")
        return {}

    # Get row counts and sort from smallest to largest
    rowcounts = get_rowcounts(engine, schema)
    tables_by_size = [table for table, _ in sorted(rowcounts, key=lambda x: x[1])]
    actual_count = len(tables_by_size)

    # Determine selector for a given table name
    def selector_for(table_name: str) -> int:
        resolved = resolve_table_key(metadata, table_name)
        if resolved is None:
            raise ValueError(f"Table '{table_name}' not found in metadata")
        return table_keys.index(resolved.key)

    result = {}

    if actual_count >= target_count:
        # More than enough tables - sample across the size distribution
        indices = [int(i * (actual_count - 1) / (target_count - 1)) for i in range(target_count)]
        for i, idx in enumerate(indices):
            result[f"t{i + 1}"] = selector_for(tables_by_size[idx])
    else:
        # Not enough tables - create a more intelligent mapping
        if actual_count == 1:
            # If only one table exists, use it for all selectors
            table_selector = selector_for(tables_by_size[0])
            return {f"t{i + 1}": table_selector for i in range(target_count)}

        elif actual_count == 2:
            # If two tables exist (small and large), distribute as:
            # t1, t2, t3 = small
            # t4, t5, t6, t7 = large
            small = selector_for(tables_by_size[0])
            large = selector_for(tables_by_size[1])
            mid_point = target_count // 2

            for i in range(target_count):
                if i < mid_point:
                    result[f"t{i + 1}"] = small
                else:
                    result[f"t{i + 1}"] = large

        elif actual_count == 3:
            # If three tables exist (small, medium, large), distribute evenly:
            # t1, t2 = small
            # t3, t4, t5 = medium
            # t6, t7 = large
            small = selector_for(tables_by_size[0])
            medium = selector_for(tables_by_size[1])
            large = selector_for(tables_by_size[2])

            first_third = target_count // 3
            last_third = 2 * (target_count // 3)

            for i in range(target_count):
                if i < first_third:
                    result[f"t{i + 1}"] = small
                elif i < last_third:
                    result[f"t{i + 1}"] = medium
                else:
                    result[f"t{i + 1}"] = large

        else:
            # For 4-6 tables, distribute them intelligently
            segment_size = target_count / actual_count

            for i in range(target_count):
                # Calculate which segment this position belongs to
                segment = min(int(i / segment_size), actual_count - 1)
                result[f"t{i + 1}"] = selector_for(tables_by_size[segment])

    return result

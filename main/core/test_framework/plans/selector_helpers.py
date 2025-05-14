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
from main.core.schema_analysis.connection.db_connector import DBConnector
from main.core.schema_analysis.table_profiler import get_rowcounts, pick_s_m_l_selectors

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

def get_size_based_selectors(schema: str,
                             db_type: str = "mysql") -> dict[str, int]:
    """
    Compute selectors for small / medium / large tables.
    Called once before the plan is built.
    """
    conn = DBConnector(db_type)
    engine, metadata = conn.connect(schema)
    counts = get_rowcounts(engine, schema)
    return pick_s_m_l_selectors(metadata, db_type, counts)

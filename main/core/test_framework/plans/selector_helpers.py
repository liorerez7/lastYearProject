from main.core.db_compare.query_generator.selector_explorer import SelectorExplorer
from main.core.db_compare.query_generator.strategies.aggregation_query_strategy import AggregationQueryStrategy
from main.core.db_compare.query_generator.strategies.deep_join_strategy import DeepJoinQueryStrategy
from main.core.db_compare.query_generator.strategies.basic_select_strategy import BasicSelectQueryStrategy

STRATEGY_SELECTOR_MAP = {
    "deep_join": DeepJoinQueryStrategy,
    "basic_select": BasicSelectQueryStrategy,
    "aggregation": AggregationQueryStrategy,
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

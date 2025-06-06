# registry_defaults.py
from main.core.query_generation.strategies.aggregation_query_strategy import AggregationQueryStrategy
from main.core.query_generation.strategies.basic_select_strategy import BasicSelectQueryStrategy
from main.core.query_generation.strategies.deep_join_strategy import DeepJoinQueryStrategy
from main.core.query_generation.strategies.filtered_query_strategy import FilteredQueryStrategy
from main.core.query_generation.strategies.group_by_query_strategy import GroupByQueryStrategy
from main.core.query_generation.strategies.pagination_query_strategy import PaginationQueryStrategy
from main.core.query_generation.strategies.pure_count_query_strategy import PureCountQueryStrategy
from main.core.query_generation.strategies.reverse_join_strategy import ReverseJoinQueryStrategy
from main.core.query_generation.strategies.window_query_strategy import WindowQueryStrategy
from main.core.query_generation.strategies.large_offset_query_strategy import LargeOffsetQueryStrategy
from main.core.query_generation.strategies.recursive_cte_query_strategy import RecursiveCTEQueryStrategy
"""
This module contains a registry for different query generation strategies.
The registry maps strategy names to their corresponding classes.
strategy == test type
"""

STRATEGY_CONFIG = {
    "deep_join": {
        "class": DeepJoinQueryStrategy,
        "params": {
            "min_join_size": 2,
            "max_join_size": 5,
            "longest": False
        }
    },
    "basic_select": {
        "class": BasicSelectQueryStrategy,
        "params": {}
    },
    "reverse_join": {
        "class": ReverseJoinQueryStrategy,
        "params": {}
    },
    "filtered": {
        "class": FilteredQueryStrategy,
        "params": {}
    },
    "aggregation": {
        "class": AggregationQueryStrategy,
        "params": {}
    },
    "group_by": {
        "class": GroupByQueryStrategy,
        "params": {}
    },
    "pagination": {
        "class": PaginationQueryStrategy,
        "parms": {}
    },
    "pure_count": {
        "class": PureCountQueryStrategy,
        "params": {}
    },
    "window_query": {
        "class": WindowQueryStrategy,
        "params": {}
    },
    "large_offset": {
        "class": LargeOffsetQueryStrategy,
        "params": {}
    },
    "recursive_cte": {
        "class": RecursiveCTEQueryStrategy,
        "params": {}
    }

}


def build_strategy(test_type: str, override_config: dict = None):
    config = STRATEGY_CONFIG.get(test_type)
    if not config:
        raise ValueError(f"No config found for test type '{test_type}'")

    strategy_class = config["class"]
    default_params = config.get("params", {})
    final_params = {**default_params, **(override_config or {})}

    return strategy_class(**final_params)

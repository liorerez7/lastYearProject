# query_generator_registry_defaults.py
from main.core.db_compare.query_generator.strategies.aggregation_query_strategy import AggregationQueryStrategy
from main.core.db_compare.query_generator.strategies.basic_select_strategy import BasicSelectQueryStrategy
from main.core.db_compare.query_generator.strategies.deep_join_strategy import DeepJoinQueryStrategy
from main.core.db_compare.query_generator.strategies.filtered_query_strategy import FilteredQueryStrategy
from main.core.db_compare.query_generator.strategies.reverse_join_strategy import ReverseJoinStrategy

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
        "class": ReverseJoinStrategy,
        "params": {}
    },
    "filtered": {
        "class": FilteredQueryStrategy,
        "params": {}
    },
    "aggregation": {
        "class": AggregationQueryStrategy,
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

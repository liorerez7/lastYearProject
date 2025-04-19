# query_strategy_registry.py
from main.core.db_compare.query_generator.strategies.basic_select_strategy import SimpleBaseQueryGenerator
from main.core.db_compare.query_generator.strategies.deep_join_strategy import DeepJoinQueryStrategy

"""
This module contains a registry for different query generation strategies.
The registry maps strategy names to their corresponding classes.
strategy == test type
"""
QUERY_GENERATOR_REGISTRY = {
    "deep_join": DeepJoinQueryStrategy,
    "basic_select": SimpleBaseQueryGenerator,
    # "aggregation": AggregationGenerator,
    # ...
}

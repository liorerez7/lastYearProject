# query_strategy_registry.py
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
QUERY_GENERATOR_REGISTRY = {
    "deep_join": DeepJoinQueryStrategy,
    "basic_select": BasicSelectQueryStrategy,
    "reverse_join": ReverseJoinStrategy,  # Placeholder for reverse join strategy
    "filtered": FilteredQueryStrategy,  # Placeholder for filtered query strategy
    " aggregation": AggregationQueryStrategy,  # Placeholder for aggregation query strategy
    # ...
}

# registry.py
from main.core.DBcomare.query_generator.strategies.deep_join_generator import DeepJoinGenerator
"""
This module contains a registry for different query generation strategies.
The registry maps strategy names to their corresponding classes.
strategy == test type
"""
QUERY_GENERATOR_REGISTRY = {
    "deep_join": DeepJoinGenerator,
    # "aggregation": AggregationGenerator,
    # ...
}

from main.core.db_compare.query_generator.query_generator_service import QueryGeneratorService
from main.core.db_compare.query_generator.strategies.deep_join_strategy import DeepJoinQueryStrategy


#TODO: ADD MORE PLANS IDEAS
def deep_join_plan():
    return [
        {
            "label": "Deep Join Test",
            "generator": QueryGeneratorService(test_type="deep_join",
                                               db_type="mysql",
                                               strategy_config={
                                                   "min_join_size": 3,
                                                   "max_join_size": 3,
                                                   "longest": False
                                               }).generator,
            "repeat": 3,
            "delay": 1,
        }
    ]

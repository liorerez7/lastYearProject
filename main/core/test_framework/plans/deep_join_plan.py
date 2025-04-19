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
                                                   "longest": True
                                               }).generator,
            "repeat": 2,
            "delay": 1,
        },
        {
            "label": "Deep Join Test with Custom Config",
            "generator": QueryGeneratorService(test_type="deep_join",
                                               db_type="mysql",
                                               strategy_config={}).generator,
            "repeat": 1,
            "delay": 1,
        },
    ]

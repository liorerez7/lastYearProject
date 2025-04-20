from main.core.db_compare.query_generator.query_generator_service import QueryGeneratorService
from main.core.db_compare.query_generator.strategies.deep_join_strategy import DeepJoinQueryStrategy


#TODO: ADD MORE PLANS IDEAS
def deep_join_longest(db_type: str, selector: int):
    step = {
        "label": "Deep Join Longest Path - 3 Times",
        "generator": QueryGeneratorService("deep_join",
                                           db_type,
                                           {"longest": True}).generator,
        "repeat": 3,
        "delay": 2
    }
    if selector is not None:
        step["selector"] = selector
    return [step]


def deep_join_default(db_type: str, selector: int):
    step ={
            "label": "Deep Join Default - 1 Time",
            "generator": QueryGeneratorService("deep_join", db_type, {"max_join_size": 2}).generator,
            "repeat": 1,
            "delay": 0
        }
    if selector is not None:
        step["selector"] = selector
    return [step]


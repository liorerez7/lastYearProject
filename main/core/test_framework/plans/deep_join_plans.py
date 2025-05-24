from main.core.query_generation.query_generator_service import QueryGeneratorService


#TODO: ADD MORE PLANS IDEAS
def deep_join_longest(db_type: str, selector: int, repeat: int = 1, delay: int = 1):
    step = {
        "label": "Deep Join Longest Path - 3 Times",
        "generator": QueryGeneratorService("deep_join",
                                           db_type,
                                           {"longest": True}).generator,
        "repeat": repeat,
        "delay": int
    }
    if selector is not None:
        step["selector"] = selector
    return [step]


def deep_join_default(db_type: str, selector: int, join_size: int = 2):
    step ={
            "label": "Deep Join Default - 1 Time",
            "generator": QueryGeneratorService("deep_join", db_type, {
                                                                                            "min_join_size": join_size,
                                                                                            "max_join_size": join_size
                                                                                            }).generator,
            "repeat": 1,
            "delay": 0
        }
    if selector is not None:
        step["selector"] = selector
    return [step]


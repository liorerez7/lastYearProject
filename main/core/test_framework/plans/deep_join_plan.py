from main.core.DBcomare.query_generator.strategies.deep_join_generator import DeepJoinGenerator
#TODO: ADD MORE PLANS IDEAS
def deep_join_plan():
    return [
        {
            "label": "Deep Join Test",
            "generator": DeepJoinGenerator(),
            "repeat": 3,
            "delay": 1,

        }
    ]




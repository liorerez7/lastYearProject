from main.core.db_compare.query_generator.strategies.deep_join_strategy import DeepJoinQueryStrategy
#TODO: ADD MORE PLANS IDEAS
def deep_join_plan():
    return [
        {
            "label": "Deep Join Test",
            "generator": DeepJoinQueryStrategy(),
            "repeat": 3,
            "delay": 1,

        }
    ]




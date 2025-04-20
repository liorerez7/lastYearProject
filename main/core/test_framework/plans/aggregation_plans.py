from main.core.db_compare.query_generator.query_generator_service import QueryGeneratorService


def aggregation_test(db_type: str, selector: int):
    return [
        {
            "label": f"Aggregation (selector={selector})",
            "generator": QueryGeneratorService("aggregation", db_type).generator,
            "selector": selector,
            "repeat": 2,
            "delay": 1
        }
    ]
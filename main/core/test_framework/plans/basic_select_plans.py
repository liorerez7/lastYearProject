from main.core.db_compare.query_generator.query_generator_service import QueryGeneratorService

def basic_select(db_type: str, selector: int):
    return [
        {
            "label": f"Basic Select (selector={selector})",
            "generator": QueryGeneratorService("basic_select", db_type).generator,
            "selector": selector,
            "repeat": 1,
            "delay": 0
        }
    ]

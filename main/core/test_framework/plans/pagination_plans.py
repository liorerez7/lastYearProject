from main.core.query_generation.query_generator_service import QueryGeneratorService

def pagination_test(db_type: str, selector: int, *, repeat: int = 2, delay: int = 0):
    return [{
        "label": f"Pagination (selector={selector})",
        "generator": QueryGeneratorService("pagination", db_type).generator,
        "selector": selector,
        "repeat": repeat,
        "delay": delay,
    }]

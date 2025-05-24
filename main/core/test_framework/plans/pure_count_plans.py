from main.core.query_generation.query_generator_service import QueryGeneratorService

def pure_count(db_type: str, selector: int, *, repeat: int = 2, delay: int = 0):
    return [{
        "label": f"Pure COUNT (selector={selector})",
        "generator": QueryGeneratorService("pure_count", db_type).generator,
        "selector": selector,
        "repeat": repeat,
        "delay": delay,
    }]

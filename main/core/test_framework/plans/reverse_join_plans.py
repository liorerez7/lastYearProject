from main.core.query_generation.query_generator_service import QueryGeneratorService

def reverse_join(db_type: str, selector: int, *, repeat: int = 3, delay: int = 1):
    return [{
        "label": f"Reverse Join (selector={selector})",
        "generator": QueryGeneratorService("reverse_join", db_type).generator,
        "selector": selector,
        "repeat": repeat,
        "delay":  delay,
    }]

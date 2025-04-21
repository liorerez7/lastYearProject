from main.core.query_generation.query_generator_service import QueryGeneratorService

def group_by(db_type: str, selector: int, *, repeat: int = 20, delay: int = 0):
    """
    Build a single “Group By” step that runs `repeat` times.
    """
    return [{
        "label": f"Group By (selector={selector})",
        "generator": QueryGeneratorService("group_by", db_type).generator,
        "selector": selector,
        "repeat":   repeat,
        "delay":    delay,
    }]

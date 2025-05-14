from main.core.query_generation.query_generator_service import QueryGeneratorService


def large_offset(db_type: str, selector: int, *, repeat: int = 20, delay: int = 0):
    """
    Build one *step* that will be executed `repeat` times instead of
    cloning the same step 20× in the plan.
    """
    return [{
        "label": f"Basic Select (selector={selector})",
        "generator": QueryGeneratorService("large_offset", db_type).generator,
        "selector": selector,
        "repeat": repeat,
        "delay":  delay,
    }]

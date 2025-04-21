from main.core.query_generation.query_generator_service import QueryGeneratorService


def filtered_test(db_type: str, selector: int, *, repeat: int, delay: int = 0):
    """
    A single step that runs the FilteredQueryStrategy `repeat` times.
    """
    return [{
        "label":       f"Filtered Query (selector={selector})",
        "generator":   QueryGeneratorService("filtered", db_type).generator,
        "selector":    selector,
        "repeat":      repeat,
        "delay":       delay,
    }]
from main.core.query_generation.query_generator_service import QueryGeneratorService


def aggregation_test(db_type: str, selector: int, *, repeat: int, delay: int = 0):

    return [{
        "label":       f"Aggregation (selector={selector})",
        "generator":   QueryGeneratorService("aggregation", db_type).generator,
        "selector":    selector,
        "repeat":      repeat,
        "delay":       delay,
    }]
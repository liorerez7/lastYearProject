class SelectorExplorer:
    """
    Tries to find the first valid selector for a given query strategy,
    using the provided schema metadata and db_type.
    """
    def __init__(self, strategy_class, schema_metadata, db_type):
        self.strategy_class = strategy_class
        self.schema_metadata = schema_metadata
        self.db_type = db_type

    def find_first_valid_selector(self, max_tries: int = 100) -> int:
        for selector in range(max_tries):
            strategy = self.strategy_class()
            query = strategy.generate_query(self.schema_metadata, self.db_type, selector=selector)
            if query and query.strip().lower().startswith("select"):
                return selector
        return -1  # Not found


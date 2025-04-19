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
             # needs to be random from the max selector
             #selector = return random.randint(0, max_selectors - 1)
             #TODO:  depending on the strategy max tries will be max selector's for example for deep join strategy
             # max selector is 	Number of nodes (tables) in the graph
            strategy = self.strategy_class()
            query = strategy.generate_query(self.schema_metadata, self.db_type, selector=selector)
            if query and query.strip().lower().startswith("select"):
                return selector
        return -1  # Not found


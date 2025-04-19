# base_query_strategy.py
from abc import ABC, abstractmethod


class BaseQueryStrategy(ABC):
    @abstractmethod
    def generate_query(self, schema_metadata, db_type: str, selector: int = 0) -> str:
        """
        Given schema metadata and a selector, generate a SQL query.
        The selector is used to produce a different query each time,
        but should generate the same logical query for both DBs.
        """
        pass

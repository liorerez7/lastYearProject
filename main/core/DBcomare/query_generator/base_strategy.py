# base_strategy.py
from abc import ABC, abstractmethod

#TODO: Add more generators for different types of queries
class QueryGenerationStrategy(ABC):
    """
    Base class for query generation strategies.
    strategies meaning the different types of  queries we can generate like
    deep join , simple join etc
    this is how the class\design will look like
    This class defines the interface for generating SQL queries based on schema metadata.
    It serves as a blueprint for all concrete query generation strategies.

    """
    @abstractmethod
    def generate_query(self, schema_metadata) -> str:
        """
        Generate a SQL query based on schema metadata.
        """
        pass
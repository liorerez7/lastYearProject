from abc import ABC, abstractmethod
import random
from sqlalchemy.schema import MetaData


##TODO: here we want to add params that fits to all queries

class BaseQueryStrategy(ABC):

    @abstractmethod
    def generate_query(self, schema_metadata: MetaData, db_type: str, selector: int = None) -> str:
        """
        Generate a SQL query based on the schema metadata and target database type.

        Parameters:
        - schema_metadata: SQLAlchemy MetaData object representing the DB schema
        - db_type: The target DB type (e.g., "mysql", "postgresql")
        - selector: An optional integer seed used to produce predictable variations of queries.
                     If not provided, a random number is used to introduce variety.
        Returns:
        A valid SQL query string
        """
        pass



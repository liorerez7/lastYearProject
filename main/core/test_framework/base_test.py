from abc import ABC, abstractmethod
import time

class BaseTest(ABC):
    def __init__(self):
        self.results = []

    @abstractmethod
    def run(self, engine, metadata):
        pass
    def execute_query(self, engine, query):
        try:
            with engine.connect() as conn:
                result = conn.execute(query)
                return result.fetchall()
        except Exception as e:
            print(f"❌ Query failed: {e}")
            return []
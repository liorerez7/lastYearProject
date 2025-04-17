from abc import ABC, abstractmethod
import time

from sqlalchemy import text


class BaseTest(ABC):
    def __init__(self):
        self.results = []

    @abstractmethod
    def run(self, engine, metadata):
        pass

    def execute_query(self, engine, query):
        try:
            with engine.connect() as conn:
                conn.execute(text(query))  # ✅ wrap the raw SQL
        except Exception as e:
            print(f"❌ Query failed: {e}")

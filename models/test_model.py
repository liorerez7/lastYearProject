from dataclasses import dataclass
from decimal import Decimal
from typing import List, Dict


from dataclasses import dataclass

@dataclass
class TestMetadata:
    test_id: str
    cloud_provider: str
    source_db: str
    destination_db: str
    status: str
    mail: str

    def to_dynamo_item(self) -> dict:
        return {
            "test_id": self.test_id,
            "cloud_provider": self.cloud_provider,
            "source_db": self.source_db,
            "destination_db": self.destination_db,
            "status": self.status,
            "mail": self.mail
        }




@dataclass
class TestExecution:
    test_id: str
    timestamp: str
    db_type: str
    test_type: str
    schema: str
    queries: List[Dict]

    def to_dynamo_item(self) -> dict:
        # המרה של Decimal ל-float בכל queries
        def convert_query(q):
            return {
                "query": q["query"],
                "query_type": q["query_type"],
                "repeat": q["repeat"],
                "selector": q["selector"],
                "durations": [float(d) if isinstance(d, Decimal) else d for d in q["durations"]],
                "stddev": float(q["stddev"]) if isinstance(q["stddev"], Decimal) else q["stddev"]
            }

        return {
            "test_id": self.test_id,
            "timestamp": self.timestamp,
            "db_type": self.db_type,
            "test_type": self.test_type,
            "schema": self.schema,
            "queries": [convert_query(q) for q in self.queries]
        }


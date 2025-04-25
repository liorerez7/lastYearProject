from dataclasses import dataclass
from typing import List, Dict


@dataclass
class TestMetadata:
    test_id: str
    cloud_provider: str
    source_db: str
    destination_db: str
    timestamp: str
    status: str

    def to_dynamo_item(self) -> dict:
        return {
            "test_id": self.test_id,
            "SK": f"metadata#{self.cloud_provider}#{self.source_db}#{self.destination_db}",
            "cloudProvider": self.cloud_provider,
            "sourceDB": self.source_db,
            "destinationDB": self.destination_db,
            "timestamp": self.timestamp,
            "status": self.status
        }


@dataclass
class TestExecution:
    test_id: str
    timestamp: str
    db_type: str
    test_type: str
    schema: str
    queries: List[Dict]  # each dict contains: sql, size, repeat

    def to_dynamo_item(self) -> dict:
        return {
            "test_id": self.test_id,
            "SK": f"execution#{self.db_type}#{self.test_type}",
            "dbType": self.db_type,
            "testType": self.test_type,
            "schema": self.schema,
            "queries": self.queries,
            "timestamp": self.timestamp
        }

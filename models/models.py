from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class TestMetadata(Base):
    __tablename__ = "test_metadata"

    id = Column(String, primary_key=True)
    plan_name = Column(String)
    cloud_provider = Column(String)
    source_db = Column(String)
    destination_db = Column(String)
    mail = Column(String)

    started_at     = Column(DateTime, default=datetime.datetime.utcnow)
    finished_at    = Column(DateTime, nullable=True)
    status         = Column(String, default="pending")  # pending / running / finished / error
    summary_json   = Column(JSON,  nullable=True)
    recommendations = Column(Text, nullable=True)

    executions = relationship("TestExecution", back_populates="test_meta")

    def to_dict(self):
        return {
            "id": self.test_id,
            "query_type": self.query_type,
            "selector": self.selector,
            "mysql_time": self.mysql_time,
            "postgres_time": self.postgres_time,
            "avg": self.avg,
            "p95": self.p95,
            "p99": self.p99,
            "winner": self.winner,
        }

class TestExecution(Base):
    __tablename__ = "test_executions"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    test_id       = Column(String, ForeignKey("test_metadata.id"))
    db_type       = Column(String)
    query_type    = Column(String)
    test_type     = Column(String)
    schema        = Column(String)
    timestamp     = Column(DateTime)
    queries       = Column(JSON)
    selector      = Column(String)
    mysql_time    = Column(Float)
    postgres_time = Column(Float)
    avg           = Column(Float)
    p95           = Column(Float)
    p99           = Column(Float)
    winner        = Column(String)

    # ← כאן השינוי: השם חייב להיות test_meta ולא metadata
    test_meta = relationship("TestMetadata", back_populates="executions")

    def to_dict(self):
        return {
            "test_id": self.test_id,
            "db_type": self.db_type,
            "test_type": self.test_type,
            "schema": self.schema,
            "timestamp": self.timestamp,
            "queries": self.queries,
            "query_type": self.query_type,
            "selector": self.selector,
            "mysql_time": self.mysql_time,
            "postgres_time": self.postgres_time,
            "avg": self.avg,
            "p95": self.p95,
            "p99": self.p99,
            "winner": self.winner,
        }

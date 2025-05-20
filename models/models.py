from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class TestMetadata(Base):
    __tablename__ = "test_metadata"

    id = Column(String, primary_key=True)
    plan_name = Column(String)
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    status = Column(String, default="pending")  # pending / running / finished / error
    summary_json = Column(JSON, nullable=True)
    recommendations = Column(Text, nullable=True)

    executions = relationship("TestExecution", back_populates="metadata")

    def to_dict(self):
        return {
            "id": self.id,
            "plan_name": self.plan_name,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "status": self.status,
            "summary_json": self.summary_json,
            "recommendations": self.recommendations
        }

class TestExecution(Base):
    __tablename__ = "test_executions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_id = Column(String, ForeignKey("test_metadata.id"))
    query_type = Column(String)
    selector = Column(String)
    mysql_time = Column(Float)
    postgres_time = Column(Float)
    avg = Column(Float)
    p95 = Column(Float)
    p99 = Column(Float)
    winner = Column(String)

    metadata = relationship("TestMetadata", back_populates="executions")

    def to_dict(self):
        return {
            "id": self.id,
            "test_id": self.test_id,
            "query_type": self.query_type,
            "selector": self.selector,
            "mysql_time": self.mysql_time,
            "postgres_time": self.postgres_time,
            "avg": self.avg,
            "p95": self.p95,
            "p99": self.p99,
            "winner": self.winner
        }

from abc import ABC, abstractmethod

from main.config.aws_config import aws_config
from main.core.migration.strategies.mysql_to_postgres_strategy import MySQLToPostgresStrategy
from main.core.uploader.awsUploader import awsUploader
from main.config.logger_config import setup_logger

logger = setup_logger(__name__)


# Add more imports as you add strategies

class MigrationPipeline:
    STRATEGY_REGISTRY = {
        ("mysql", "postgres"): MySQLToPostgresStrategy,
        # Add more strategies here...
    }

    def __init__(self, source_db_type, destination_db_type, schema_name):
        self.source_db = source_db_type.lower()
        self.dest_db = destination_db_type.lower()
        self.strategy_class = self._get_strategy_class()
        self.schema_name = schema_name

    def _get_strategy_class(self):
        key = (self.source_db, self.dest_db)
        if key not in self.STRATEGY_REGISTRY:
            raise ValueError(f"🚫 migration from {self.source_db} to {self.dest_db} is not supported.")
        return self.STRATEGY_REGISTRY[key]

    def run(self, source_endpoint, destination_endpoint):
        logger.info(f"🚀 Starting migration from {self.source_db} to {self.dest_db}...")
        migration_strategy = self.strategy_class(self.schema_name)
        migration_strategy.run(source_endpoint, destination_endpoint, self.schema_name)
        logger.info(f"✅ Migration from {self.source_db} to {self.dest_db} completed successfully.")


if __name__ == '__main__':
    uploader = awsUploader()
    endpoints = uploader.get_or_create_endpoints(aws_config)
    print(endpoints)
    pipeline = MigrationPipeline("mysql", "postgres", "extendedEmp")
    pipeline.run(endpoints['source'], endpoints['destination'])

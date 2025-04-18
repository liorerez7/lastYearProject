from abc import ABC, abstractmethod

from main.config.aws_config import aws_config
from main.core.Migration.migrations.mysql_to_postgres_migration import MySQLToPostgresMigration
from main.core.uploader.awsUploader import awsUploader


# Add more imports as you add strategies

class MigrationPipeline:

    STRATEGY_REGISTRY = {
        ("mysql", "postgres"): MySQLToPostgresMigration,
        # Add more strategies here...
    }

    def __init__(self, source_db_type, destination_db_type):
        self.source_db = source_db_type.lower()
        self.dest_db = destination_db_type.lower()
        self.strategy_class = self._get_strategy_class()

    def _get_strategy_class(self):
        key = (self.source_db, self.dest_db)
        if key not in self.STRATEGY_REGISTRY:
            raise ValueError(f"🚫 Migration from {self.source_db} to {self.dest_db} is not supported.")
        return self.STRATEGY_REGISTRY[key]

    def run(self, source_endpoint, destination_endpoint):
        print(f"🚀 Running migration from {self.source_db} to {self.dest_db}")
        migration_strategy = self.strategy_class()
        migration_strategy.run(source_endpoint, destination_endpoint)
        print("✅ Migration completed.")


if __name__ == '__main__':
    uploader = awsUploader()
    endpoints = uploader.get_or_create_endpoints(aws_config)
    print(endpoints)
    pipeline = MigrationPipeline("mysql", "postgres")
    pipeline.run(endpoints['source'], endpoints['destination'])

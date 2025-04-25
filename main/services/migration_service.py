from main.core.uploader.awsUploader import awsUploader
from main.core.migration.migration_pipeline import MigrationPipeline
from main.config.aws_config import aws_config

def run_migration_service(source: str, destination: str, schema_name: str):
    uploader = awsUploader()
    endpoints = uploader.get_or_create_endpoints(aws_config)
    pipeline = MigrationPipeline(source, destination, schema_name)
    result = pipeline.run(endpoints['source'], endpoints['destination'])

    return {
        "status": "done",
        "endpoints": endpoints,
        "result": result
    }

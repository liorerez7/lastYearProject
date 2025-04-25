from http.client import HTTPException

from fastapi import FastAPI
from pydantic import BaseModel
from main.core.uploader.awsUploader import awsUploader
from main.core.migration.migration_pipeline import MigrationPipeline
from main.config.aws_config import aws_config
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS middleware settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MigrationRequest(BaseModel):
    """
    Request model for initiating a migration.

    Attributes:
        source (str): The type of the source database (e.g., 'mysql').
        destination (str): The type of the destination database (e.g., 'postgresql').
        schema_name (str): The name of the schema to migrate.
    """
    source: str
    destination: str
    schema_name: str

@app.post("/run-migration")
def run_migration(request: MigrationRequest):
    """
    Run a database migration from source to destination and return result and endpoints.

    Args:
        request (MigrationRequest): Contains source and destination DB types and schema name.

    Returns:
        dict: A dictionary containing:
            - status (str): Status message.
            - endpoints (dict): AWS RDS endpoint details for both source and destination.
            - result (any): Output returned from the MigrationPipeline's run method.

    Raises:
        HTTPException: If a KeyError, ValueError, RuntimeError, or general Exception occurs during migration.
    """
    try:
        uploader = awsUploader()
        endpoints = uploader.get_or_create_endpoints(aws_config)
        pipeline = MigrationPipeline(request.source, request.destination, request.schema_name)
        result = pipeline.run(endpoints['source'], endpoints['destination'])
        return {"status": "done", "endpoints": endpoints, "result": result}

    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

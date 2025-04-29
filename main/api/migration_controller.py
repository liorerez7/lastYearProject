from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from main.services.migration_service import run_migration_service
import uuid
import boto3

from main.services.upload_migration_files_service import upload_migration_files_service

migrationRouter = APIRouter()


class MigrationRequest(BaseModel):
    source: str
    destination: str
    schema_name: str


@migrationRouter.post("/run-migration")
def run_migration(request: MigrationRequest):
    try:
        return run_migration_service(request.source, request.destination, request.schema_name)
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")


@migrationRouter.post("/upload-migration-files")
async def upload_files(schema_file: UploadFile = File(...), data_file: UploadFile = File(...)):
    return await upload_migration_files_service(schema_file, data_file)

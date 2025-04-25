from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from main.services.migration_service import run_migration_service

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

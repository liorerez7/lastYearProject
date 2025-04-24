from http.client import HTTPException

from fastapi import FastAPI
from pydantic import BaseModel
from main.core.uploader.awsUploader import awsUploader
from main.core.migration.migration_pipeline import MigrationPipeline
from main.config.aws_config import aws_config  # adjust as needed
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MigrationRequest(BaseModel):
    source: str  # optional if you want React to send DB types
    destination: str
    schema_name: str

@app.post("/run-migration")
def run_migration(request: MigrationRequest):
    try:
        uploader = awsUploader()
        endpoints = uploader.get_or_create_endpoints(aws_config)
        pipeline = MigrationPipeline(request.source, request.destination,request.schema_name)
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
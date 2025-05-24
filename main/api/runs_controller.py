from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
from main.services.run_service import fetch_runs, fetch_run
from main.services.supabase_service import get_executions_by_test_id

router = APIRouter()

@router.get("/runs", response_model=List[Dict[str, Any]])
def list_runs(limit: int = 100):
    try:
        return fetch_runs(limit)
    except Exception as e:
        raise HTTPException(500, f"Error: {e}")

@router.get("/runs/{run_id}", response_model=Dict[str, Any])
def get_run(run_id: int):
    try:
        return fetch_run(run_id)
    except Exception as e:
        raise HTTPException(500, f"Error: {e}")

@router.get("/executions", response_model=List[Dict[str, Any]])
def get_executions(test_id: str):
    try:
        return get_executions_by_test_id(test_id).data
    except Exception as e:
        raise HTTPException(500, f"Error fetching executions: {e}")

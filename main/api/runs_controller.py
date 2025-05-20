from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from services.run_service import fetch_runs, fetch_run

router = APIRouter()

@router.get("/runs", response_model=List[Dict[str, Any]])
def list_runs(limit: int = 100):
    try:
        return fetch_runs(limit)
    except Exception as e:
        raise HTTPException(500, f"Error: {e}")

@router.get("/runs/{run_id}", response_model=Dict[str, Any])
def get_run(run_id: str):
    try:
        return fetch_run(run_id)
    except Exception as e:
        raise HTTPException(500, f"Error: {e}")

# from supabase import create_client, Client
#
# # פרטים קבועים של הפרויקט
# SUPABASE_URL = "https://nsfhfmkgwhcfoezuhqpp.supabase.co"
# SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5zZmhmbWtnd2hjZm9lenVocXBwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ4MTI3MjIsImV4cCI6MjA2MDM4ODcyMn0.CkEaR9_eNy_cfmfj4v_CRcAHL7vhwbu0s4krByV4-ZQ"
#
# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
#
# def insert_metadata(item: dict):
#     return supabase.table("test_metadata").insert(item).execute()
#
# def insert_execution(item: dict):
#     return supabase.table("test_executions").insert(item).execute()
#
# def get_executions_by_test_id(test_id: str):
#     return supabase.table("test_executions").select("*").eq("test_id", test_id).execute()

import os, json
from typing import Optional, Dict, Any
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# ─────────────────────────────────────────
def insert_metadata(test_id: str, plan_name: str = "Basic Test Plan"):
    data = {"id": test_id, "plan_name": plan_name, "status": "pending"}
    return supabase.table("test_metadata").insert(data).execute()

def update_metadata_status(
    test_id: str,
    status: str,
    summary_json: Optional[Dict] = None,
    recommendations: Optional[str] = None,
    finished_at: Optional[str] = None
):
    data: Dict[str, Any] = {"status": status}
    if summary_json is not None:
        data["summary_json"] = summary_json        # dict → JSONB
    if recommendations:
        data["recommendations"] = recommendations
    if finished_at:
        data["finished_at"] = finished_at
    return supabase.table("test_metadata").update(data).eq("id", test_id).execute()

def insert_execution(**fields):
    return supabase.table("test_executions").insert(fields).execute()

def get_executions_by_test_id(test_id: str):
    return supabase.table("test_executions").select("*").eq("test_id", test_id).execute()

# ───────── fetch helpers for API ─────────
def fetch_runs(limit: int = 100):
    return supabase.table("test_metadata") \
        .select("id,plan_name,started_at,status") \
        .order("started_at", desc=True) \
        .limit(limit).execute()

def fetch_run(run_id: str):
    meta = supabase.table("test_metadata").select("*").eq("id", run_id).single().execute()
    execs = supabase.table("test_executions").select("*").eq("test_id", run_id).execute()
    return {"metadata": meta.data, "executions": execs.data}

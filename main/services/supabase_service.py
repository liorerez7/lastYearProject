import os, json
from typing import Optional, Dict, Any
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)


def insert_metadata(data: Dict[str, Any]) -> int:
    try:
        resp = supabase.table("test_metadata").insert(data).execute()
        inserted = resp.data  # list of inserted rows
        print("✅ Metadata inserted:", inserted)

        if not inserted or "id" not in inserted[0]:
            raise Exception("Missing 'id' in insert response!")

        return inserted[0]["id"]

    except Exception as e:
        print("❌ Supabase insert exception:", e)
        raise


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

# def insert_execution(**fields):
#     return supabase.table("test_executions").insert(fields).execute()

def insert_execution(**fields):
    try:
        print("\n📤 Inserting execution to Supabase:")
        print(json.dumps(fields, indent=2, default=str))

        resp = supabase.table("test_executions").insert(fields).execute()
        print("✅ Inserted execution:", resp.data)
        return resp

    except Exception as e:
        print("❌ Supabase execution insert error:", e)
        raise


def get_executions_by_test_id(test_id: str):
    return supabase.table("test_executions").select("*").eq("test_id", test_id).execute()

# ───────── fetch helpers for API ─────────
def fetch_runs(limit: int = 100):
    return supabase.table("test_metadata") \
        .select("id,plan_name,started_at,status") \
        .order("started_at", desc=True) \
        .limit(limit).execute()

def fetch_run(run_id: int):
    meta = (
        supabase.table("test_metadata")
        .select("*")
        .eq("id", run_id)
        .single()
        .execute()
    )
    execs = (
        supabase.table("test_executions")
        .select("*")
        .eq("test_id", run_id)  # FK → int
        .execute()
    )
    return {"metadata": meta.data, "executions": execs.data}

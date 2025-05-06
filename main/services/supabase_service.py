from supabase import create_client, Client

# פרטים קבועים של הפרויקט
SUPABASE_URL = "https://nsfhfmkgwhcfoezuhqpp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5zZmhmbWtnd2hjZm9lenVocXBwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ4MTI3MjIsImV4cCI6MjA2MDM4ODcyMn0.CkEaR9_eNy_cfmfj4v_CRcAHL7vhwbu0s4krByV4-ZQ"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def insert_metadata(item: dict):
    return supabase.table("test_metadata").insert(item).execute()

def insert_execution(item: dict):
    return supabase.table("test_executions").insert(item).execute()

def get_executions_by_test_id(test_id: str):
    return supabase.table("test_executions").select("*").eq("test_id", test_id).execute()

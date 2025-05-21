from typing import List, Dict, Any
from collections import defaultdict
from main.services.supabase_service import fetch_runs as sb_fetch_runs, fetch_run as sb_fetch_run


# ---------- public ----------

def fetch_run(run_id: int) -> Dict[str, Any]:
    pack = sb_fetch_run(run_id)
    meta = pack["metadata"]

    return {
        "id": meta["id"],
        "plan_name": meta["plan_name"],
        "started_at": meta["started_at"],
        "finished_at": meta.get("finished_at"),
        "status": meta["status"],
        "cloud_provider": meta.get("cloud_provider", "failed to load"),
        "source_db": meta.get("source_db", "failed to load"),
        "destination_db": meta.get("destination_db", "failed to load"),
        "recommendations": meta.get("recommendations", "failed to load")
    }


def fetch_runs(limit: int = 100) -> List[Dict[str, Any]]:
    return sb_fetch_runs(limit).data

# ---------- helpers ----------
def _compute_category_results(execs):
    bucket = defaultdict(list)
    for e in execs:
        bucket[e["query_type"]].append(e)

    cat = {}
    for q, group in bucket.items():
        mw = sum(1 for e in group if e["winner"] == "mysql")
        pw = sum(1 for e in group if e["winner"] == "postgres")
        cat[q] = {
            "mysql_wins": mw,
            "postgres_wins": pw,
            "total": len(group),
            "winner": "mysql" if mw > pw else "postgres" if pw > mw else "tie"
        }
    return cat

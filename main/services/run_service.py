from typing import List, Dict, Any
from collections import defaultdict
from main.services.supabase_service import fetch_runs as sb_fetch_runs, fetch_run as sb_fetch_run


# ---------- public ----------
def fetch_runs(limit: int = 100) -> List[Dict[str, Any]]:
    return sb_fetch_runs(limit).data

def fetch_run(run_id: int) -> Dict[str, Any]:
    pack = sb_fetch_run(run_id)  # SELECT * WHERE id = run_id
    meta, execs = pack["metadata"], pack["executions"]

    # format results
    results = [
        {
            "id": e["id"],
            "name": f'{e["query_type"]} – sel {e["selector"]}',
            "description": e["query_type"],
            "mysql_time": e["mysql_time"],
            "postgres_time": e["postgres_time"],
            "winner": e["winner"]
        }
        for e in execs
    ]

    # calc category summary if missing
    cat = meta.get("summary_json", {}).get("category_results") if meta else None
    if cat is None:
        cat = _compute_category_results(execs)

    return {
        "id": meta["id"],
        "plan_name": meta["plan_name"],
        "started_at": meta["started_at"],
        "finished_at": meta.get("finished_at"),
        "status": meta["status"],
        "results": results,
        "category_results": cat,
        "recommendations": meta.get("recommendations", "")
    }

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

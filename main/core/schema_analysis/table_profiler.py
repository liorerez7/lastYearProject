# main/core/schema_analysis/table_profiler.py
from sqlalchemy import inspect, text

from main.core.query_generation.utils.table_access_utils import resolve_table_key
from main.core.schema_analysis.connection.db_connector import DBConnector

def _fast_rowcount(engine, table_fullname: str) -> int:
    with engine.connect() as conn:
        return conn.execute(text(f"SELECT COUNT(*) FROM {table_fullname}")).scalar_one()

def get_rowcounts(engine, schema: str) -> list[tuple[str, int]]:
    insp = inspect(engine)
    tables = insp.get_table_names(schema=schema)
    stats = [
        (tbl, _fast_rowcount(engine, f"{schema}.{tbl}"))
        for tbl in tables
    ]
    # largest first
    return sorted(stats, key=lambda x: x[1], reverse=True)

def pick_s_m_l_selectors(metadata, db_type: str,
                         rowcounts: list[tuple[str,int]]) -> dict[str, int]:
    """
    Return {"small": sel, "medium": sel, "large": sel}
    where sel is the deterministic selector for that table.
    """
    if not rowcounts:
        return {}

    large_tbl  = rowcounts[0][0]
    medium_tbl = rowcounts[len(rowcounts)//2][0]
    small_tbl  = rowcounts[-1][0]

    table_keys = list(sorted(metadata.tables.keys()))  # same order selector uses

    def selector_for(table_name: str) -> int:
        """Return deterministic selector that matches BasicSelectStrategy."""
        # resolve_table_key() handles both "sakila.actor" and "actor"
        resolved = resolve_table_key(metadata, table_name)
        if resolved is None:
            raise ValueError(f"Table '{table_name}' not found in metadata")
        table_keys = sorted(metadata.tables.keys())
        return table_keys.index(resolved.key)

    return {
        "large":  selector_for(large_tbl),
        "medium": selector_for(medium_tbl),
        "small":  selector_for(small_tbl),
    }

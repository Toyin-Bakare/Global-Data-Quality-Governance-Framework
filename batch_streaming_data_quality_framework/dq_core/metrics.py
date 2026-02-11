from __future__ import annotations
from typing import Any, Dict, List

def null_rate(records: List[Dict[str, Any]], field: str) -> float:
    if not records:
        return 0.0
    nulls = sum(1 for r in records if r.get(field) in (None, "", "null"))
    return nulls / len(records)

def allowed_values_rate(records: List[Dict[str, Any]], field: str, allowed: List[Any]) -> float:
    if not records:
        return 1.0
    allowed_set = set(allowed)
    ok = sum(1 for r in records if r.get(field) in allowed_set)
    return ok / len(records)

def within_range_rate(records: List[Dict[str, Any]], field: str, min_v: float, max_v: float) -> float:
    if not records:
        return 1.0
    ok = 0
    for r in records:
        try:
            v = float(r.get(field))
            if min_v <= v <= max_v:
                ok += 1
        except Exception:
            pass
    return ok / len(records)

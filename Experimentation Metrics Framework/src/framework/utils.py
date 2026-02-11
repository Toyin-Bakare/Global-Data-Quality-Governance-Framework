from datetime import datetime

def parse_ts(ts: str) -> datetime:
    # expects ISO like 2026-01-01T00:00:00Z
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))

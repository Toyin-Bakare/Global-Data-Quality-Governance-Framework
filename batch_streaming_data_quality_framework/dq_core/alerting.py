from __future__ import annotations
from typing import Any, Dict, List
import requests

def build_slack_payload(title: str, severity: str, run_url: str, failing_rules: List[Dict[str, Any]]) -> Dict[str, Any]:
    lines = [f"*{title}*", f"Severity: *{severity.upper()}*", f"Run: {run_url}"]
    if failing_rules:
        lines.append("*Failing rules:*")
        for r in failing_rules[:10]:
            lines.append(f"- `{r['rule_id']}` ({r['rule_type']}) field={r.get('field')}")
    return {"text": "\n".join(lines)}

def send_slack(webhook_url: str, payload: Dict[str, Any]) -> None:
    r = requests.post(webhook_url, json=payload, timeout=5)
    r.raise_for_status()

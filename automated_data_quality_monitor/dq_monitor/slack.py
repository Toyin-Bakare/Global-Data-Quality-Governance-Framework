from __future__ import annotations
from typing import Any, Dict
import requests

def build_slack_payload(run_id: str, checkpoint_name: str, validation: Dict[str, Any], dashboard_url: str | None = None) -> Dict[str, Any]:
    success = bool(validation.get("success", False))
    stats = validation.get("statistics") or {}
    total = stats.get("evaluated_expectations")
    passed = stats.get("successful_expectations")

    failures = []
    for r in (validation.get("results") or []):
        if not r.get("success", False):
            exp = (r.get("expectation_config") or {})
            exp_type = exp.get("expectation_type")
            kwargs = exp.get("kwargs") or {}
            col = kwargs.get("column")
            failures.append(f"- {exp_type} (column={col})")

    text = f"*DQ {'PASSED' if success else 'FAILED'}* for checkpoint `{checkpoint_name}`\nRun: `{run_id}`"
    if isinstance(total, int) and isinstance(passed, int):
        text += f"\nExpectations: {passed}/{total} passed"
    if failures:
        text += "\n*Failures:*\n" + "\n".join(failures[:12])
        if len(failures) > 12:
            text += f"\n…and {len(failures)-12} more"
    if dashboard_url:
        text += f"\nDashboard: {dashboard_url}"

    return {"attachments": [{"color": "good" if success else "danger", "text": text}]}

def send_slack(webhook_url: str, payload: Dict[str, Any]) -> None:
    r = requests.post(webhook_url, json=payload, timeout=5)
    r.raise_for_status()

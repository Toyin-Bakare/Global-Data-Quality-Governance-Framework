from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import yaml
import os

@dataclass(frozen=True)
class Rule:
    id: str
    type: str
    field: Optional[str]
    params: Dict[str, Any]
    severity: str = "medium"

@dataclass(frozen=True)
class Contract:
    name: str
    entity: str
    rules: List[Rule]

def load_contract(path: str) -> Contract:
    with open(path, "r", encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    rules = [
        Rule(
            id=r["id"],
            type=r["type"],
            field=r.get("field"),
            params=r.get("params") or {},
            severity=r.get("severity", "medium"),
        )
        for r in doc.get("rules", [])
    ]
    return Contract(name=doc["name"], entity=doc["entity"], rules=rules)

def load_contracts(dir_path: str) -> List[Contract]:
    out: List[Contract] = []
    for fn in sorted(os.listdir(dir_path)):
        if fn.endswith((".yaml", ".yml")):
            out.append(load_contract(os.path.join(dir_path, fn)))
    return out

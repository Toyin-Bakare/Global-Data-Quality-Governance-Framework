from dataclasses import dataclass
from typing import Any, Dict
import yaml

@dataclass
class JobConfig:
    raw: Dict[str, Any]

    @staticmethod
    def load(path: str) -> "JobConfig":
        with open(path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)
        return JobConfig(raw=raw)

    def get(self, *keys, default=None):
        cur = self.raw
        for k in keys:
            if cur is None or k not in cur:
                return default
            cur = cur[k]
        return cur

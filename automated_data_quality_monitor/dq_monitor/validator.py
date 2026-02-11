from __future__ import annotations
from typing import Any, Dict
import os
import uuid

def new_run_id() -> str:
    return str(uuid.uuid4())

def run_checkpoint(checkpoint_name: str = "daily_checkpoint") -> Dict[str, Any]:
    """Run a Great Expectations checkpoint and return JSON dict.

    Note: Great Expectations is installed in the Airflow container for the full stack.
    """
    import great_expectations as ge  # noqa: F401
    from great_expectations.data_context import FileDataContext

    root = os.getenv("GE_ROOT_DIR", "/opt/great_expectations")
    ctx = FileDataContext(context_root_dir=root)
    result = ctx.run_checkpoint(checkpoint_name=checkpoint_name)
    return result.to_json_dict()

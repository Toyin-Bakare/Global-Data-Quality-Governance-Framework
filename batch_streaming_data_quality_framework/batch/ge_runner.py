from __future__ import annotations
from typing import Any, Dict
import os
from dq_core.contracts import Contract

def run_contract_against_postgres(contract: Contract, query: str) -> Dict[str, Any]:
    import great_expectations as ge  # noqa
    from great_expectations.data_context import FileDataContext

    ge_root = os.getenv("GE_ROOT_DIR", "/opt/great_expectations")
    ctx = FileDataContext(context_root_dir=ge_root)

    batch_request = {
        "datasource_name": "pg_dq",
        "data_connector_name": "default_runtime_data_connector_name",
        "data_asset_name": contract.entity,
        "runtime_parameters": {"query": query},
        "batch_identifiers": {"default_identifier_name": "default_id"},
    }

    suite_name = f"{contract.name}_suite"
    try:
        suite = ctx.get_expectation_suite(suite_name)
    except Exception:
        suite = ctx.add_expectation_suite(expectation_suite_name=suite_name)

    suite.expectations = []

    for r in contract.rules:
        if r.type == "not_null":
            suite.add_expectation("expect_column_values_to_not_be_null", kwargs={"column": r.field})
        elif r.type == "range":
            suite.add_expectation("expect_column_values_to_be_between",
                                  kwargs={"column": r.field, "min_value": r.params["min"], "max_value": r.params["max"]})
        elif r.type == "allowed_values":
            suite.add_expectation("expect_column_values_to_be_in_set",
                                  kwargs={"column": r.field, "value_set": r.params["allowed"]})

    ctx.save_expectation_suite(suite)
    v = ctx.get_validator(batch_request=batch_request, expectation_suite_name=suite_name)
    return v.validate().to_json_dict()

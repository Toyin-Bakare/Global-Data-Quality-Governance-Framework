from dq_monitor.slack import build_slack_payload

def test_slack_payload_contains_failures():
    validation = {
        "success": False,
        "statistics": {"evaluated_expectations": 2, "successful_expectations": 1},
        "results": [
            {"success": False, "expectation_config": {"expectation_type":"expect_column_values_to_not_be_null","kwargs":{"column":"customer_id"}}, "result": {}},
        ]
    }
    payload = build_slack_payload("run1", "daily_checkpoint", validation, "http://dash")
    text = payload["attachments"][0]["text"]
    assert "FAILED" in text
    assert "customer_id" in text

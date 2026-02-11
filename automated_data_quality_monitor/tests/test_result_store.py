from dq_monitor.result_store import json_dumps

def test_json_dumps_smoke():
    sample = {"a": 1, "b": {"c": "x"}}
    s = json_dumps(sample)
    assert '"a"' in s

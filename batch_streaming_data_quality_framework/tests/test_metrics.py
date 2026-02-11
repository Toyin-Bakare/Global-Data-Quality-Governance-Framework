from dq_core.metrics import null_rate, allowed_values_rate, within_range_rate

def test_metrics():
    recs = [{"a": 1}, {"a": None}, {"a": ""}]
    assert abs(null_rate(recs, "a") - 2/3) < 1e-9
    assert allowed_values_rate([{"c":"USD"},{"c":"XXX"}], "c", ["USD"]) == 0.5
    assert within_range_rate([{"x": 5},{"x": 100},{"x":"nope"}], "x", 0, 50) == 1/3

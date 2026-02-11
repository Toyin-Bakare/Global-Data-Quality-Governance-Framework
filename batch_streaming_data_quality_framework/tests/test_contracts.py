from dq_core.contracts import load_contract

def test_contract_loads():
    c = load_contract("contracts/orders.yaml")
    assert c.entity == "orders"
    assert len(c.rules) >= 3

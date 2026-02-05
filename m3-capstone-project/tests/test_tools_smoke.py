from agent_humancapital.tools.governance_tools import pii_redactor, rbac_enforcer

def test_pii_redaction():
    s = "email me at test@example.com or call +62 812-3456-7890"
    r = pii_redactor(s)
    assert "example.com" not in r
    assert "812" not in r

def test_rbac():
    ok, _ = rbac_enforcer("guest", "retrieve")
    assert ok is False
    ok2, _ = rbac_enforcer("hr", "retrieve")
    assert ok2 is True

"""
Tests for Institutional Security Headers (Issue #41).
Verifies that all API responses include defense-in-depth headers:
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- Strict-Transport-Security: max-age=31536000; includeSubDomains
- Content-Security-Policy: strict default-src 'none' for JSON API, scoped for /demo
"""

def test_api_responses_include_mandatory_security_headers(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.headers["x-content-type-options"] == "nosniff"
    assert resp.headers["x-frame-options"] == "DENY"
    assert "max-age=31536000" in resp.headers["strict-transport-security"]
    assert "default-src 'none'" in resp.headers["content-security-policy"]
    assert "frame-ancestors 'none'" in resp.headers["content-security-policy"]


def test_demo_route_has_scoped_content_security_policy(client):
    resp = client.get("/demo")
    assert resp.status_code == 200
    assert resp.headers["x-content-type-options"] == "nosniff"
    assert resp.headers["x-frame-options"] == "DENY"
    assert "max-age=31536000" in resp.headers["strict-transport-security"]
    csp = resp.headers["content-security-policy"]
    assert "default-src 'self'" in csp
    assert "'unsafe-inline'" in csp
    assert "frame-ancestors 'none'" in csp


def test_error_responses_still_contain_security_headers(client):
    # 404 Not Found
    resp = client.get("/nonexistent-endpoint-404")
    assert resp.status_code == 404
    assert resp.headers["x-content-type-options"] == "nosniff"
    assert resp.headers["x-frame-options"] == "DENY"
    assert "max-age=31536000" in resp.headers["strict-transport-security"]
    assert "default-src 'none'" in resp.headers["content-security-policy"]

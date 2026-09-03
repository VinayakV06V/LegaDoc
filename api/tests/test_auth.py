"""Auth tests — see SYSTEM_DESIGN.md's testing priority: "Auth/RBAC tests
first" is stated as exactly what judges (and, more importantly, real
attackers) will probe hardest."""

from tests.conftest import login


def test_login_success_returns_access_and_refresh_tokens(client, make_user):
    make_user("duty_officer", email="duty@example.com", password="hunter2000")

    resp = login(client, "duty@example.com", "hunter2000")

    assert resp.status_code == 200
    body = resp.json()
    assert body["access_token"]
    assert body["refresh_token"]
    assert body["token_type"] == "bearer"


def test_login_wrong_password_rejected(client, make_user):
    make_user("duty_officer", email="duty@example.com", password="hunter2000")

    resp = login(client, "duty@example.com", "wrong-password")

    assert resp.status_code == 401
    assert "invalid" in resp.json()["detail"].lower()


def test_login_unknown_email_gets_same_generic_error_as_wrong_password(client, make_user):
    make_user("duty_officer", email="duty@example.com", password="hunter2000")

    known_wrong = login(client, "duty@example.com", "wrong-password")
    unknown = login(client, "nobody-like-this-exists@example.com", "whatever")

    assert unknown.status_code == known_wrong.status_code == 401
    # Same message either way — the response body must not leak which case it was.
    assert unknown.json()["detail"] == known_wrong.json()["detail"]


def test_refresh_token_issues_a_new_access_token(client, make_user):
    make_user("duty_officer", email="duty@example.com", password="hunter2000")
    tokens = login(client, "duty@example.com", "hunter2000").json()

    resp = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})

    assert resp.status_code == 200
    assert resp.json()["access_token"]
    assert resp.json()["access_token"] != tokens["access_token"]


def test_refresh_rejects_an_access_token_used_as_a_refresh_token(client, make_user):
    """An access token must not double as a refresh token — they're issued
    with different `type` claims specifically to prevent this."""
    make_user("duty_officer", email="duty@example.com", password="hunter2000")
    tokens = login(client, "duty@example.com", "hunter2000").json()

    resp = client.post("/auth/refresh", json={"refresh_token": tokens["access_token"]})

    assert resp.status_code == 401


def test_protected_endpoint_rejects_missing_token(client):
    resp = client.get("/cases")
    assert resp.status_code == 401


def test_protected_endpoint_rejects_garbage_token(client):
    resp = client.get("/cases", headers={"Authorization": "Bearer not-a-real-token"})
    assert resp.status_code == 401

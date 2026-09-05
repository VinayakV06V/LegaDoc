"""Case lifecycle + the CRITICAL cross-case access fix.

The single most important test in this file is
test_unassigned_io_cannot_read_other_ios_case — it's the automated,
permanent version of the finding "any IO officer could browse any sensitive
case across the state." A regression here is a real, dangerous leak, not a
cosmetic bug.
"""

from tests.conftest import login, auth_headers


def _register_fir(client, token, crime_type="Theft"):
    resp = client.post(
        "/cases",
        json={"crime_type": crime_type, "complaint_text": "Something was stolen."},
        headers=auth_headers(token),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_duty_officer_can_register_a_fir(client, make_user):
    make_user("duty_officer", email="duty@example.com", password="pw")
    token = login(client, "duty@example.com", "pw").json()["access_token"]

    case = _register_fir(client, token, crime_type="Theft")

    assert case["crime_type"] == "Theft"
    assert case["investigation_status"] == "FIR_Registered"
    assert case["case_number"].startswith("THE-")


def test_only_duty_officer_can_register_a_fir(client, make_user):
    make_user("io", email="io@example.com", password="pw")
    token = login(client, "io@example.com", "pw").json()["access_token"]

    resp = client.post(
        "/cases",
        json={"crime_type": "Theft", "complaint_text": "..."},
        headers=auth_headers(token),
    )

    assert resp.status_code == 403


def test_sho_can_assign_io_and_assigned_io_can_then_read_the_case(client, make_user):
    duty = make_user("duty_officer", email="duty@example.com", password="pw")
    sho = make_user("sho", email="sho@example.com", password="pw", org=duty.organization)
    io = make_user("io", email="io@example.com", password="pw", org=duty.organization)

    duty_token = login(client, "duty@example.com", "pw").json()["access_token"]
    case = _register_fir(client, duty_token)

    sho_token = login(client, "sho@example.com", "pw").json()["access_token"]
    assign_resp = client.post(
        f"/cases/{case['id']}/assign-io",
        json={"io_user_id": str(io.id)},
        headers=auth_headers(sho_token),
    )
    assert assign_resp.status_code == 201, assign_resp.text

    io_token = login(client, "io@example.com", "pw").json()["access_token"]
    get_resp = client.get(f"/cases/{case['id']}", headers=auth_headers(io_token))

    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == case["id"]


def test_unassigned_io_cannot_read_other_ios_case(client, make_user):
    """THE critical regression test. An IO with zero connection to a case
    must get 403, not the case file, no matter how the request is shaped."""
    duty = make_user("duty_officer", email="duty@example.com", password="pw")
    sho = make_user("sho", email="sho@example.com", password="pw", org=duty.organization)
    assigned_io = make_user("io", email="io1@example.com", password="pw", org=duty.organization)
    other_io = make_user("io", email="io2@example.com", password="pw", org=duty.organization)

    duty_token = login(client, "duty@example.com", "pw").json()["access_token"]
    case = _register_fir(client, duty_token, crime_type="SexualAssault")

    sho_token = login(client, "sho@example.com", "pw").json()["access_token"]
    client.post(
        f"/cases/{case['id']}/assign-io",
        json={"io_user_id": str(assigned_io.id)},
        headers=auth_headers(sho_token),
    )

    other_io_token = login(client, "io2@example.com", "pw").json()["access_token"]
    resp = client.get(f"/cases/{case['id']}", headers=auth_headers(other_io_token))

    assert resp.status_code == 403


def test_io_list_cases_only_shows_assigned_cases(client, make_user):
    duty = make_user("duty_officer", email="duty@example.com", password="pw")
    sho = make_user("sho", email="sho@example.com", password="pw", org=duty.organization)
    io = make_user("io", email="io@example.com", password="pw", org=duty.organization)

    duty_token = login(client, "duty@example.com", "pw").json()["access_token"]
    assigned_case = _register_fir(client, duty_token, crime_type="Theft")
    unassigned_case = _register_fir(client, duty_token, crime_type="Robbery")

    sho_token = login(client, "sho@example.com", "pw").json()["access_token"]
    client.post(
        f"/cases/{assigned_case['id']}/assign-io",
        json={"io_user_id": str(io.id)},
        headers=auth_headers(sho_token),
    )

    io_token = login(client, "io@example.com", "pw").json()["access_token"]
    resp = client.get("/cases", headers=auth_headers(io_token))

    assert resp.status_code == 200
    ids = {c["id"] for c in resp.json()}
    assert assigned_case["id"] in ids
    assert unassigned_case["id"] not in ids


def test_config_admin_sees_every_case_regardless_of_assignment(client, make_user):
    duty = make_user("duty_officer", email="duty@example.com", password="pw")
    make_user("config_admin", email="admin@example.com", password="pw", org=duty.organization)

    duty_token = login(client, "duty@example.com", "pw").json()["access_token"]
    case = _register_fir(client, duty_token)

    admin_token = login(client, "admin@example.com", "pw").json()["access_token"]
    resp = client.get(f"/cases/{case['id']}", headers=auth_headers(admin_token))

    assert resp.status_code == 200


def test_police_specialist_cannot_read_unassigned_case(client, make_user):
    """Police specialist roles (women_cell, cyber_cell, traffic_police, etc.)
    cannot view a case without an active CaseAssignment record (closes RBAC security hole)."""
    duty = make_user("duty_officer", email="duty@example.com", password="pw")
    make_user("sho", email="sho@example.com", password="pw", org=duty.organization)
    specialist = make_user("women_cell", email="wc@example.com", password="pw", org=duty.organization)

    duty_token = login(client, "duty@example.com", "pw").json()["access_token"]
    case = _register_fir(client, duty_token)

    specialist_token = login(client, "wc@example.com", "pw").json()["access_token"]
    resp = client.get(f"/cases/{case['id']}", headers=auth_headers(specialist_token))

    assert resp.status_code == 403
    assert resp.json()["detail"] == "Not assigned to this case"


def test_police_specialist_can_read_assigned_case(client, make_user):
    """Police specialist assigned to a case via CaseAssignment can read case details."""
    duty = make_user("duty_officer", email="duty@example.com", password="pw")
    sho = make_user("sho", email="sho@example.com", password="pw", org=duty.organization)
    cyber_officer = make_user("cyber_cell", email="cyber@example.com", password="pw", org=duty.organization)

    duty_token = login(client, "duty@example.com", "pw").json()["access_token"]
    case = _register_fir(client, duty_token)

    sho_token = login(client, "sho@example.com", "pw").json()["access_token"]
    client.post(
        f"/cases/{case['id']}/assign-io",
        json={"io_user_id": str(cyber_officer.id)},
        headers=auth_headers(sho_token),
    )

    cyber_token = login(client, "cyber@example.com", "pw").json()["access_token"]
    resp = client.get(f"/cases/{case['id']}", headers=auth_headers(cyber_token))

    assert resp.status_code == 200
    assert resp.json()["id"] == case["id"]


def test_assigned_io_can_add_and_list_case_diary_entries(client, make_user):
    duty = make_user("duty_officer", email="duty_cd@example.com", password="pw")
    sho = make_user("sho", email="sho_cd@example.com", password="pw", org=duty.organization)
    io = make_user("io", email="io_cd@example.com", password="pw", org=duty.organization)

    duty_token = login(client, "duty_cd@example.com", "pw").json()["access_token"]
    case = _register_fir(client, duty_token)

    sho_token = login(client, "sho_cd@example.com", "pw").json()["access_token"]
    client.post(
        f"/cases/{case['id']}/assign-io",
        json={"io_user_id": str(io.id)},
        headers=auth_headers(sho_token),
    )

    io_token = login(client, "io_cd@example.com", "pw").json()["access_token"]

    # IO adds diary entry
    cd_resp = client.post(
        f"/cases/{case['id']}/case-diary",
        json={"text": "Visited scene of crime at 10:30 AM. Recovered suspicious tool."},
        headers=auth_headers(io_token),
    )
    assert cd_resp.status_code == 201
    entry = cd_resp.json()
    assert entry["case_id"] == case["id"]
    assert entry["status"] == "ready"
    assert "Visited scene" in entry["text"]

    # IO lists diary entries
    list_resp = client.get(f"/cases/{case['id']}/case-diary", headers=auth_headers(io_token))
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1


def test_unassigned_io_cannot_add_or_list_case_diary(client, make_user):
    duty = make_user("duty_officer", email="duty_cd2@example.com", password="pw")
    io_assigned = make_user("io", email="io_assigned@example.com", password="pw", org=duty.organization)
    io_unassigned = make_user("io", email="io_unassigned@example.com", password="pw", org=duty.organization)

    duty_token = login(client, "duty_cd2@example.com", "pw").json()["access_token"]
    case = _register_fir(client, duty_token)

    sho = make_user("sho", email="sho_cd2@example.com", password="pw", org=duty.organization)
    sho_token = login(client, "sho_cd2@example.com", "pw").json()["access_token"]
    client.post(
        f"/cases/{case['id']}/assign-io",
        json={"io_user_id": str(io_assigned.id)},
        headers=auth_headers(sho_token),
    )

    unassigned_token = login(client, "io_unassigned@example.com", "pw").json()["access_token"]

    # Cannot add entry
    add_fail = client.post(
        f"/cases/{case['id']}/case-diary",
        json={"text": "Unauthorized note"},
        headers=auth_headers(unassigned_token),
    )
    assert add_fail.status_code == 403

    # Cannot list entries
    list_fail = client.get(f"/cases/{case['id']}/case-diary", headers=auth_headers(unassigned_token))
    assert list_fail.status_code == 403


def test_empty_case_diary_entry_rejected(client, make_user):
    duty = make_user("duty_officer", email="duty_cd3@example.com", password="pw")
    io = make_user("io", email="io_cd3@example.com", password="pw", org=duty.organization)

    duty_token = login(client, "duty_cd3@example.com", "pw").json()["access_token"]
    case = _register_fir(client, duty_token)

    sho = make_user("sho", email="sho_cd3@example.com", password="pw", org=duty.organization)
    sho_token = login(client, "sho_cd3@example.com", "pw").json()["access_token"]
    client.post(
        f"/cases/{case['id']}/assign-io",
        json={"io_user_id": str(io.id)},
        headers=auth_headers(sho_token),
    )

    io_token = login(client, "io_cd3@example.com", "pw").json()["access_token"]

    bad_resp = client.post(
        f"/cases/{case['id']}/case-diary",
        json={"text": "   "},
        headers=auth_headers(io_token),
    )
    assert bad_resp.status_code == 400

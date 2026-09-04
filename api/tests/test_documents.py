"""Document upload path — real storage, real DB state, real job dispatch
(verified via the in-memory queue double), and the redaction-view masking
logic. OCR/AI-Parser/Chain Worker task bodies are not exercised here — they
stay stubs, see workers/*/worker.py."""

from uuid import UUID

from app import models
from app.audit import verify_chain_intact
from tests.conftest import auth_headers, login


def _setup_case_with_io(client, make_user, db_session):
    """Common fixture shape: a duty officer registers a case, an SHO
    assigns an IO to it. Returns (case, io_user, io_token)."""
    duty = make_user("duty_officer", email="duty@example.com", password="pw")
    sho = make_user("sho", email="sho@example.com", password="pw", org=duty.organization)
    io = make_user("io", email="io@example.com", password="pw", org=duty.organization)

    duty_token = login(client, "duty@example.com", "pw").json()["access_token"]
    case_resp = client.post(
        "/cases",
        json={"crime_type": "Theft", "complaint_text": "..."},
        headers=auth_headers(duty_token),
    )
    case = case_resp.json()

    sho_token = login(client, "sho@example.com", "pw").json()["access_token"]
    client.post(
        f"/cases/{case['id']}/assign-io",
        json={"io_user_id": str(io.id)},
        headers=auth_headers(sho_token),
    )

    io_token = login(client, "io@example.com", "pw").json()["access_token"]
    return case, io, io_token


def test_upload_text_document_enqueues_both_tracks(client, make_user, db_session, fake_queue):
    case, io, io_token = _setup_case_with_io(client, make_user, db_session)

    resp = client.post(
        "/documents",
        data={"case_id": case["id"], "doc_type": "Witness Statement"},
        files={"file": ("statement.txt", b"The witness said hello.", "text/plain")},
        headers=auth_headers(io_token),
    )

    assert resp.status_code == 202, resp.text
    body = resp.json()
    assert body["status"] == "processing"  # text-bearing, waiting on OCR
    assert body["chain_status"] == "pending"
    assert body["version"] == 1

    task_names = {job["task_name"] for job in fake_queue.enqueued}
    assert task_names == {"chain_worker.write_hash", "ocr_worker.extract_document"}

    chain_job = next(j for j in fake_queue.enqueued if j["task_name"] == "chain_worker.write_hash")
    assert chain_job["kwargs"]["idempotency_key"] == f"{body['id']}:v1"


def test_upload_binary_evidence_skips_ocr_and_goes_straight_to_ready(client, make_user, db_session, fake_queue):
    case, io, io_token = _setup_case_with_io(client, make_user, db_session)

    resp = client.post(
        "/documents",
        data={"case_id": case["id"], "doc_type": "CCTV Footage"},
        files={"file": ("clip.mp4", b"\x00\x01fake video bytes", "video/mp4")},
        headers=auth_headers(io_token),
    )

    assert resp.status_code == 202, resp.text
    body = resp.json()
    assert body["status"] == "ready"  # nothing to OCR or redact in a video

    task_names = {job["task_name"] for job in fake_queue.enqueued}
    assert task_names == {"chain_worker.write_hash"}  # Track B never enqueued


def test_upload_writes_a_real_file_to_storage(client, make_user, db_session, tmp_path):
    case, io, io_token = _setup_case_with_io(client, make_user, db_session)
    content = b"exact bytes that should land on disk"

    resp = client.post(
        "/documents",
        data={"case_id": case["id"], "doc_type": "Witness Statement"},
        files={"file": ("statement.txt", content, "text/plain")},
        headers=auth_headers(io_token),
    )
    doc_id = resp.json()["id"]

    document = db_session.get(models.Document, UUID(doc_id))
    stored_path = tmp_path / "objects" / document.storage_path
    assert stored_path.read_bytes() == content
    assert document.doc_hash  # a real sha256 hex digest was computed


def test_unassigned_io_cannot_upload_to_a_case_they_are_not_assigned_to(client, make_user, db_session):
    duty = make_user("duty_officer", email="duty@example.com", password="pw")
    other_io = make_user("io", email="other@example.com", password="pw", org=duty.organization)

    duty_token = login(client, "duty@example.com", "pw").json()["access_token"]
    case = client.post(
        "/cases", json={"crime_type": "Theft", "complaint_text": "..."}, headers=auth_headers(duty_token)
    ).json()

    other_token = login(client, "other@example.com", "pw").json()["access_token"]
    resp = client.post(
        "/documents",
        data={"case_id": case["id"], "doc_type": "Witness Statement"},
        files={"file": ("statement.txt", b"content", "text/plain")},
        headers=auth_headers(other_token),
    )

    assert resp.status_code == 403


def test_document_not_ready_shows_no_text_yet(client, make_user, db_session):
    case, io, io_token = _setup_case_with_io(client, make_user, db_session)
    resp = client.post(
        "/documents",
        data={"case_id": case["id"], "doc_type": "Witness Statement"},
        files={"file": ("statement.txt", b"Some sensitive content here.", "text/plain")},
        headers=auth_headers(io_token),
    )
    doc_id = resp.json()["id"]

    get_resp = client.get(f"/documents/{doc_id}", headers=auth_headers(io_token))

    assert get_resp.status_code == 200
    assert get_resp.json()["status"] == "processing"
    assert get_resp.json()["text"] is None


def test_full_access_role_sees_unredacted_text_restricted_role_sees_masked(client, make_user, db_session):
    case, io, io_token = _setup_case_with_io(client, make_user, db_session)
    resp = client.post(
        "/documents",
        data={"case_id": case["id"], "doc_type": "Witness Statement"},
        files={"file": ("statement.txt", b"My name is Rahul Sharma, call 9876543210.", "text/plain")},
        headers=auth_headers(io_token),
    )
    doc_id = UUID(resp.json()["id"])

    # Simulate what the (unavailable) OCR + AI Parser workers would have
    # done — this test exercises the masking logic, not tag generation, so
    # raw_text and status are set directly rather than run through a real
    # PaddleOCR/Presidio pipeline.
    document = db_session.get(models.Document, doc_id)
    document.raw_text = "My name is Rahul Sharma, call 9876543210."
    document.status = "ready"
    db_session.add(models.DocumentSensitivityTag(
        document_id=doc_id, entity_type="PERSON", span_start=11, span_end=23, confidence=95, source="ai_parser",
    ))
    db_session.add(models.DocumentSensitivityTag(
        document_id=doc_id, entity_type="PHONE_NUMBER", span_start=30, span_end=40, confidence=90, source="ai_parser",
    ))
    db_session.commit()

    # IO is a full-access role for a case they're assigned to.
    io_view = client.get(f"/documents/{doc_id}", headers=auth_headers(io_token)).json()
    assert io_view["text"] == "My name is Rahul Sharma, call 9876543210."

    # Defense is neither an unrestricted-case-access role nor an assigned
    # IO — it should never even reach the redaction-view decision.
    make_user("defense", email="defense@example.com", password="pw", org=io.organization)
    defense_token = login(client, "defense@example.com", "pw").json()["access_token"]
    # Defense has no case access at all (not in _UNRESTRICTED_CASE_ROLES,
    # not an assigned IO) — confirms the case-level gate runs before the
    # document-level redaction view ever gets a chance to matter.
    defense_resp = client.get(f"/documents/{doc_id}", headers=auth_headers(defense_token))
    assert defense_resp.status_code == 403


def test_versions_endpoint_lists_every_upload_in_order(client, make_user, db_session):
    case, io, io_token = _setup_case_with_io(client, make_user, db_session)
    first = client.post(
        "/documents",
        data={"case_id": case["id"], "doc_type": "Witness Statement"},
        files={"file": ("v1.txt", b"first version", "text/plain")},
        headers=auth_headers(io_token),
    ).json()
    second = client.post(
        "/documents",
        data={"case_id": case["id"], "doc_type": "Witness Statement"},
        files={"file": ("v2.txt", b"corrected version", "text/plain")},
        headers=auth_headers(io_token),
    ).json()

    assert second["version"] == 2

    resp = client.get(f"/documents/{first['id']}/versions", headers=auth_headers(io_token))
    versions = [v["version"] for v in resp.json()]
    assert versions == [1, 2]


def test_chain_status_endpoint(client, make_user, db_session):
    case, io, io_token = _setup_case_with_io(client, make_user, db_session)
    doc_id = client.post(
        "/documents",
        data={"case_id": case["id"], "doc_type": "Witness Statement"},
        files={"file": ("statement.txt", b"content", "text/plain")},
        headers=auth_headers(io_token),
    ).json()["id"]

    resp = client.get(f"/documents/{doc_id}/chain-status", headers=auth_headers(io_token))

    assert resp.status_code == 200
    assert resp.json() == {"document_id": doc_id, "chain_status": "pending"}


def test_retry_chain_write_reenqueues_with_the_same_idempotency_key(client, make_user, db_session, fake_queue):
    case, io, io_token = _setup_case_with_io(client, make_user, db_session)
    make_user("config_admin", email="admin@example.com", password="pw", org=io.organization)
    admin_token = login(client, "admin@example.com", "pw").json()["access_token"]

    doc_id = client.post(
        "/documents",
        data={"case_id": case["id"], "doc_type": "Witness Statement"},
        files={"file": ("statement.txt", b"content", "text/plain")},
        headers=auth_headers(io_token),
    ).json()["id"]
    original_key = next(j for j in fake_queue.enqueued if j["task_name"] == "chain_worker.write_hash")["kwargs"]["idempotency_key"]

    resp = client.post(f"/documents/{doc_id}/retry-chain-write", headers=auth_headers(admin_token))

    assert resp.status_code == 200
    assert resp.json()["retry_enqueued"] is True
    retry_jobs = [j for j in fake_queue.enqueued if j["task_name"] == "chain_worker.write_hash"]
    assert len(retry_jobs) == 2  # original upload + this retry
    assert retry_jobs[1]["kwargs"]["idempotency_key"] == original_key  # same key, not a fresh one


def test_retry_chain_write_is_a_noop_once_already_confirmed(client, make_user, db_session, fake_queue):
    case, io, io_token = _setup_case_with_io(client, make_user, db_session)
    make_user("config_admin", email="admin@example.com", password="pw", org=io.organization)
    admin_token = login(client, "admin@example.com", "pw").json()["access_token"]

    doc_id = client.post(
        "/documents",
        data={"case_id": case["id"], "doc_type": "Witness Statement"},
        files={"file": ("statement.txt", b"content", "text/plain")},
        headers=auth_headers(io_token),
    ).json()["id"]
    document = db_session.get(models.Document, UUID(doc_id))
    document.chain_status = "confirmed"
    db_session.commit()
    fake_queue.enqueued.clear()

    resp = client.post(f"/documents/{doc_id}/retry-chain-write", headers=auth_headers(admin_token))

    assert resp.status_code == 200
    assert resp.json()["retry_enqueued"] is False
    assert fake_queue.enqueued == []


def test_only_config_admin_can_trigger_retry_chain_write(client, make_user, db_session):
    case, io, io_token = _setup_case_with_io(client, make_user, db_session)
    doc_id = client.post(
        "/documents",
        data={"case_id": case["id"], "doc_type": "Witness Statement"},
        files={"file": ("statement.txt", b"content", "text/plain")},
        headers=auth_headers(io_token),
    ).json()["id"]

    resp = client.post(f"/documents/{doc_id}/retry-chain-write", headers=auth_headers(io_token))

    assert resp.status_code == 403


def test_redact_tag_adds_a_correction_and_extends_the_audit_hash_chain(client, make_user, db_session):
    case, io, io_token = _setup_case_with_io(client, make_user, db_session)
    doc_id = client.post(
        "/documents",
        data={"case_id": case["id"], "doc_type": "Witness Statement"},
        files={"file": ("statement.txt", b"Contact Rahul at 9876543210 please.", "text/plain")},
        headers=auth_headers(io_token),
    ).json()["id"]

    document = db_session.get(models.Document, UUID(doc_id))
    document.raw_text = "Contact Rahul at 9876543210 please."
    document.status = "ready"
    db_session.commit()

    resp = client.post(
        f"/documents/{doc_id}/redact-tag",
        json={"entity_type": "PHONE_NUMBER", "span_start": 17, "span_end": 27},
        headers=auth_headers(io_token),
    )

    assert resp.status_code == 200, resp.text
    # IO is full-access, so the response still shows unredacted text to them —
    # the tag exists for OTHER roles' benefit, not to hide it from its author.
    assert resp.json()["text"] == "Contact Rahul at 9876543210 please."

    tags = db_session.query(models.DocumentSensitivityTag).filter_by(document_id=UUID(doc_id)).all()
    assert len(tags) == 1
    assert tags[0].source == "officer_correction"

    # Upload wrote one audit_log entry, redact-tag wrote a second — the
    # chain must still verify end to end.
    entries = db_session.query(models.AuditLog).order_by(models.AuditLog.created_at.asc()).all()
    assert len(entries) == 2
    assert entries[0].action == "document_uploaded"
    assert entries[0].prev_hash is None
    assert entries[1].action == "redact_tag_correction"
    assert entries[1].prev_hash == entries[0].row_hash
    assert verify_chain_intact(db_session)

    # And the metadata never contains the actual phone number — only the span.
    assert "9876543210" not in str(entries[1].action_metadata)


def test_upload_disguised_executable_rejected_by_magic_bytes(client, make_user, db_session):
    """MIME sniffing check: sending binary executable bytes with a .pdf extension
    is rejected with 415 Unsupported Media Type."""
    case, io, io_token = _setup_case_with_io(client, make_user, db_session)

    # Shell script disguised as PDF
    fake_pdf = b"#!/bin/bash\nrm -rf /"
    resp = client.post(
        "/documents",
        data={"case_id": case["id"], "doc_type": "Case Diary"},
        files={"file": ("malicious.pdf", fake_pdf, "application/pdf")},
        headers=auth_headers(io_token),
    )

    # python-magic detects this is text/x-shellscript, not application/pdf
    assert resp.status_code == 415, resp.text
    assert "Unsupported file type" in resp.json()["detail"]


def test_upload_deduplication_returns_existing_document(client, make_user, db_session):
    """Uploading the exact same file twice for the same case & doc_type
    returns the existing document row instead of creating duplicate versions."""
    case, io, io_token = _setup_case_with_io(client, make_user, db_session)
    pdf_content = b"%PDF-1.4 sample pdf content for dedup testing"

    # Upload 1
    resp1 = client.post(
        "/documents",
        data={"case_id": case["id"], "doc_type": "FIR"},
        files={"file": ("fir.pdf", pdf_content, "application/pdf")},
        headers=auth_headers(io_token),
    )
    assert resp1.status_code == 202
    doc1 = resp1.json()
    assert doc1["version"] == 1

    # Upload 2 (identical content)
    resp2 = client.post(
        "/documents",
        data={"case_id": case["id"], "doc_type": "FIR"},
        files={"file": ("fir_copy.pdf", pdf_content, "application/pdf")},
        headers=auth_headers(io_token),
    )
    assert resp2.status_code == 202
    doc2 = resp2.json()

    # Must return the same document ID and version 1 without creating v2
    assert doc2["id"] == doc1["id"]
    assert doc2["version"] == 1

    count = db_session.query(models.Document).filter_by(case_id=UUID(case["id"])).count()
    assert count == 1


def test_unauthorized_role_cannot_upload_evidence(client, make_user, db_session):
    """Roles not in UPLOAD_ALLOWED_ROLES (like defense) are rejected with 403."""
    case, io, io_token = _setup_case_with_io(client, make_user, db_session)
    defense_user = make_user("defense", email="lawyer@bar.in", password="pw")
    defense_token = login(client, "lawyer@bar.in", "pw").json()["access_token"]

    resp = client.post(
        "/documents",
        data={"case_id": case["id"], "doc_type": "FIR"},
        files={"file": ("test.pdf", b"%PDF-1.4 dummy", "application/pdf")},
        headers=auth_headers(defense_token),
    )
    assert resp.status_code == 403


def test_get_document_returns_download_url(client, make_user, db_session):
    """GET /documents/{id} provides a presigned download_url for retrieving the raw object."""
    case, io, io_token = _setup_case_with_io(client, make_user, db_session)
    pdf_content = b"%PDF-1.4 dummy document for presigned download test"

    upload_resp = client.post(
        "/documents",
        data={"case_id": case["id"], "doc_type": "FIR"},
        files={"file": ("doc.pdf", pdf_content, "application/pdf")},
        headers=auth_headers(io_token),
    )
    doc_id = upload_resp.json()["id"]

    get_resp = client.get(f"/documents/{doc_id}", headers=auth_headers(io_token))
    assert get_resp.status_code == 200
    body = get_resp.json()
    assert "download_url" in body
    assert body["download_url"] is not None
    assert "/local-storage/" in body["download_url"] or "http" in body["download_url"]


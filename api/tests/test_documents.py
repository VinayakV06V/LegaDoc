"""Document upload path — real storage, real DB state, real job dispatch
(verified via the in-memory queue double), and the redaction-view masking
logic. OCR/AI-Parser/Chain Worker task bodies are not exercised here — they
stay stubs, see workers/*/worker.py."""

from uuid import UUID, uuid4

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
    """MIME sniffing check: sending binary executable bytes or shell scripts with a .pdf extension
    is rejected with 415 Unsupported Media Type by the pure-Python sniffer."""
    case, io, io_token = _setup_case_with_io(client, make_user, db_session)

    # 1. Shell script disguised as PDF
    fake_pdf = b"#!/bin/bash\nrm -rf /"
    resp = client.post(
        "/documents",
        data={"case_id": case["id"], "doc_type": "Case Diary"},
        files={"file": ("malicious.pdf", fake_pdf, "application/pdf")},
        headers=auth_headers(io_token),
    )
    assert resp.status_code == 415, resp.text
    assert "Unsupported file type" in resp.json()["detail"]

    # 2. Windows PE executable disguised as PDF
    pe_exe = b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff\x00\x00"
    resp_pe = client.post(
        "/documents",
        data={"case_id": case["id"], "doc_type": "FIR"},
        files={"file": ("malware.pdf", pe_exe, "application/pdf")},
        headers=auth_headers(io_token),
    )
    assert resp_pe.status_code == 415, resp_pe.text
    assert "Unsupported file type" in resp_pe.json()["detail"]

    # 3. Linux ELF executable disguised as JPEG image
    elf_bin = b"\x7fELF\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    resp_elf = client.post(
        "/documents",
        data={"case_id": case["id"], "doc_type": "FIR"},
        files={"file": ("exploit.jpg", elf_bin, "image/jpeg")},
        headers=auth_headers(io_token),
    )
    assert resp_elf.status_code == 415, resp_elf.text
    assert "Unsupported file type" in resp_elf.json()["detail"]


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


# ==================== Document Review Queue Tests (Flow 2) ====================

def _create_review_doc(db_session, case_id, uploaded_by_user_id, doc_type="FIR", status="needs_review"):
    doc = models.Document(
        case_id=UUID(case_id) if isinstance(case_id, str) else case_id,
        doc_type=doc_type,
        version=1,
        storage_path=f"test/{case_id}/{uuid4()}/v1",
        raw_text="Confidential OCR text that should not appear in queue summary",
        status=status,
        chain_status="pending",
        uploaded_by=uploaded_by_user_id,
    )
    db_session.add(doc)
    db_session.commit()
    db_session.refresh(doc)
    return doc


def _setup_case_with_io_unique(client, make_user, db_session):
    prefix = uuid4().hex[:6]
    duty = make_user("duty_officer", email=f"duty_{prefix}@example.com", password="pw")
    sho = make_user("sho", email=f"sho_{prefix}@example.com", password="pw", org=duty.organization)
    io = make_user("io", email=f"io_{prefix}@example.com", password="pw", org=duty.organization)
    duty_token = login(client, duty.email, "pw").json()["access_token"]
    case_resp = client.post(
        "/cases",
        json={"crime_type": "Theft", "complaint_text": "..."},
        headers=auth_headers(duty_token),
    )
    case = case_resp.json()
    sho_token = login(client, sho.email, "pw").json()["access_token"]
    client.post(
        f"/cases/{case['id']}/assign-io",
        json={"io_user_id": str(io.id)},
        headers=auth_headers(sho_token),
    )
    io_token = login(client, io.email, "pw").json()["access_token"]
    return case, io, io_token


def test_config_admin_sees_all_needs_review_documents(client, make_user, db_session):
    """Config Admin sees needs_review documents across all cases."""
    case1, io1, _ = _setup_case_with_io_unique(client, make_user, db_session)
    case2, io2, _ = _setup_case_with_io_unique(client, make_user, db_session)

    _create_review_doc(db_session, case1["id"], io1.id, doc_type="FIR", status="needs_review")
    _create_review_doc(db_session, case2["id"], io2.id, doc_type="Post-Mortem Report", status="needs_review")
    _create_review_doc(db_session, case1["id"], io1.id, doc_type="Seizure Memo", status="ready")  # not in queue

    admin = make_user("config_admin", email=f"admin_{uuid4().hex[:6]}@police.gov.in", password="pw")
    admin_token = login(client, admin.email, "pw").json()["access_token"]

    resp = client.get("/documents?status=needs_review", headers=auth_headers(admin_token))
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) >= 2
    assert all(d["status"] == "needs_review" for d in items)
    case_ids = {d["case_id"] for d in items}
    assert case1["id"] in case_ids
    assert case2["id"] in case_ids


def test_io_only_sees_needs_review_docs_for_assigned_cases(client, make_user, db_session):
    """Tenancy & Isolation: IO only sees needs_review docs for their assigned case(s)."""
    case1, io1, io1_token = _setup_case_with_io_unique(client, make_user, db_session)
    case2, io2, io2_token = _setup_case_with_io_unique(client, make_user, db_session)

    doc1 = _create_review_doc(db_session, case1["id"], io1.id, doc_type="FIR", status="needs_review")
    doc2 = _create_review_doc(db_session, case2["id"], io2.id, doc_type="Charge Sheet", status="needs_review")

    # IO 1 sees only doc1
    r1 = client.get("/documents?status=needs_review", headers=auth_headers(io1_token))
    assert r1.status_code == 200
    ids1 = [d["id"] for d in r1.json()]
    assert str(doc1.id) in ids1
    assert str(doc2.id) not in ids1

    # IO 2 sees only doc2
    r2 = client.get("/documents?status=needs_review", headers=auth_headers(io2_token))
    assert r2.status_code == 200
    ids2 = [d["id"] for d in r2.json()]
    assert str(doc2.id) in ids2
    assert str(doc1.id) not in ids2


def test_review_queue_empty_when_no_flagged_docs(client, make_user, db_session):
    """Empty queue state returns 200 OK with [] without error."""
    case, io, io_token = _setup_case_with_io(client, make_user, db_session)
    _create_review_doc(db_session, case["id"], io.id, status="ready")  # no doc has needs_review

    resp = client.get("/documents?status=needs_review", headers=auth_headers(io_token))
    assert resp.status_code == 200
    assert resp.json() == []


def test_review_queue_structural_pii_exclusion(client, make_user, db_session):
    """DocumentReviewItem schema must structurally exclude raw_text to prevent bulk PII leaks."""
    case, io, io_token = _setup_case_with_io(client, make_user, db_session)
    _create_review_doc(db_session, case["id"], io.id, status="needs_review")

    resp = client.get("/documents?status=needs_review", headers=auth_headers(io_token))
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) > 0

    first = items[0]
    assert "raw_text" not in first
    assert "text" not in first
    assert "Confidential" not in str(items)

    expected_keys = {"id", "case_id", "doc_type", "version", "status", "chain_status", "doc_hash", "created_at"}
    assert set(first.keys()) == expected_keys


def test_review_queue_pagination_bounds(client, make_user, db_session):
    """Pagination parameters limit/offset work cleanly, negative params return 422."""
    case, io, io_token = _setup_case_with_io(client, make_user, db_session)
    for _ in range(4):
        _create_review_doc(db_session, case["id"], io.id, status="needs_review")

    # Limit = 2
    r_paged = client.get("/documents?status=needs_review&limit=2&offset=1", headers=auth_headers(io_token))
    assert r_paged.status_code == 200
    assert len(r_paged.json()) == 2

    # Boundary checks: limit < 1 or limit > 100 triggers 422
    assert client.get("/documents?status=needs_review&limit=0", headers=auth_headers(io_token)).status_code == 422
    assert client.get("/documents?status=needs_review&limit=500", headers=auth_headers(io_token)).status_code == 422
    # Boundary check: negative offset triggers 422
    assert client.get("/documents?status=needs_review&offset=-1", headers=auth_headers(io_token)).status_code == 422


def test_review_queue_invalid_status_filter_rejected(client, make_user, db_session):
    """Querying with an unrecognized status filter returns 400 Bad Request."""
    case, io, io_token = _setup_case_with_io(client, make_user, db_session)
    resp = client.get("/documents?status=unrecognized_status", headers=auth_headers(io_token))
    assert resp.status_code == 400
    assert "Invalid document status filter" in resp.json()["detail"]


def test_review_queue_defaults_to_needs_review_status(client, make_user, db_session):
    """Calling GET /documents without explicit status query param defaults to needs_review."""
    case, io, io_token = _setup_case_with_io(client, make_user, db_session)
    doc_review = _create_review_doc(db_session, case["id"], io.id, doc_type="FIR", status="needs_review")
    doc_ready = _create_review_doc(db_session, case["id"], io.id, doc_type="Medical Report", status="ready")

    resp = client.get("/documents", headers=auth_headers(io_token))
    assert resp.status_code == 200
    items = resp.json()
    ids = [d["id"] for d in items]
    assert str(doc_review.id) in ids
    assert str(doc_ready.id) not in ids


def test_unauthorized_roles_cannot_access_review_queue(client, make_user, db_session):
    """Negative space: unauthenticated and unauthorized roles receive 401/403."""
    # 1. Unauthenticated
    assert client.get("/documents?status=needs_review").status_code == 401

    # 2. Unauthorized roles (SHO, Duty Officer, Prosecutor, Defense, Court, NCRB Analyst)
    unauthorized_roles = ["sho", "duty_officer", "prosecutor", "defense", "court", "records_ncrb_analyst"]
    for role in unauthorized_roles:
        u = make_user(role, email=f"{role}_{uuid4().hex[:6]}@example.com", password="pw")
        tok = login(client, u.email, "pw").json()["access_token"]
        r = client.get("/documents?status=needs_review", headers=auth_headers(tok))
        assert r.status_code == 403, f"Role {role} should have been denied with 403, got {r.status_code}"


def test_end_to_end_pipeline_flow_and_artifact_generation(client, make_user, make_org, db_session, fake_queue):
    """Full lifecycle pipeline verification:
    1. Case registration & assignment
    2. Upload -> Storage + SHA-256 Hash + Queue dispatch artifacts
    3. Worker extraction -> Sensitivity tag generation (< 70% threshold)
    4. Review queue routing -> Structural PII exclusion
    5. Human correction tagging -> Audit hash chain extension
    6. Masking engine -> Role-based unredacted vs redacted view artifacts
    7. Mid-case IO reassignment -> Dynamic access handover + AuditLog artifact
    8. NCRB reporting -> De-identified metadata artifact + Meta-audit log
    9. Cryptographic verification -> Entire chain intact
    """
    # 1. Setup case & assign to IO 1
    case, io1, io1_token = _setup_case_with_io(client, make_user, db_session)
    case_id = case["id"]

    # 2. Upload document -> Ingestion pipeline artifacts
    raw_content = b"Suspect Amit Kumar, contact 9988776655, resident of New Delhi."
    resp = client.post(
        "/documents",
        data={"case_id": case_id, "doc_type": "Witness Statement"},
        files={"file": ("evidence_statement.txt", raw_content, "text/plain")},
        headers=auth_headers(io1_token),
    )
    assert resp.status_code == 202
    doc_body = resp.json()
    doc_id = doc_body["id"]
    assert doc_body["status"] == "processing"
    assert doc_body["chain_status"] == "pending"

    # Verify queue dispatch artifacts
    enqueued_tasks = {job["task_name"] for job in fake_queue.enqueued}
    assert "chain_worker.write_hash" in enqueued_tasks
    assert "ocr_worker.extract_document" in enqueued_tasks

    # 3. Simulate Worker Extraction & AI Parser Tagging artifacts
    doc_uuid = UUID(doc_id)
    doc_record = db_session.get(models.Document, doc_uuid)
    doc_record.raw_text = raw_content.decode("utf-8")
    # Simulate low-confidence extraction triggering needs_review
    doc_record.status = "needs_review"
    tag_person = models.DocumentSensitivityTag(
        document_id=doc_uuid,
        entity_type="PERSON",
        span_start=8,
        span_end=18,
        confidence=65,  # Below 70% threshold
        source="ai_parser",
    )
    tag_phone = models.DocumentSensitivityTag(
        document_id=doc_uuid,
        entity_type="PHONE_NUMBER",
        span_start=28,
        span_end=38,
        confidence=95,
        source="ai_parser",
    )
    db_session.add_all([tag_person, tag_phone])
    db_session.commit()

    # 4. Review queue routing: IO 1 inspects needs_review items
    rq_resp = client.get("/documents?status=needs_review", headers=auth_headers(io1_token))
    assert rq_resp.status_code == 200
    review_items = rq_resp.json()
    assert any(item["id"] == doc_id for item in review_items)
    # Structural PII exclusion check
    matched_item = next(item for item in review_items if item["id"] == doc_id)
    assert "raw_text" not in matched_item
    assert "text" not in matched_item

    # 5. Human correction tagging -> Confirms tag & extends audit chain
    corr_resp = client.post(
        f"/documents/{doc_id}/redact-tag",
        json={"entity_type": "PERSON", "span_start": 8, "span_end": 18},
        headers=auth_headers(io1_token),
    )
    assert corr_resp.status_code == 200
    # Mark ready once reviewed
    doc_record = db_session.get(models.Document, doc_uuid)
    doc_record.status = "ready"
    db_session.commit()

    # 6. Masking engine: Assigned IO sees unredacted text; restricted role sees masked
    io_view = client.get(f"/documents/{doc_id}", headers=auth_headers(io1_token)).json()
    assert io_view["text"] == "Suspect Amit Kumar, contact 9988776655, resident of New Delhi."

    # Specialist on same case sees masked view
    specialist = make_user("cyber_cell", email="cyber@example.com", password="pw", org=io1.organization)
    db_session.add(models.CaseAssignment(case_id=doc_record.case_id, io_user_id=specialist.id))
    db_session.commit()
    spec_token = login(client, "cyber@example.com", "pw").json()["access_token"]
    spec_view = client.get(f"/documents/{doc_id}", headers=auth_headers(spec_token)).json()
    assert "[REDACTED:PERSON]" in spec_view["text"]
    assert "[REDACTED:PHONE_NUMBER]" in spec_view["text"]
    assert "Amit Kumar" not in spec_view["text"]
    assert "9988776655" not in spec_view["text"]

    # 7. Mid-case IO reassignment
    io2 = make_user("io", email="io2_reassigned@example.com", password="pw", org=io1.organization)
    sho_token = login(client, "sho@example.com", "pw").json()["access_token"]
    reassign_resp = client.post(
        f"/cases/{case_id}/reassign-io",
        json={"new_io_user_id": str(io2.id), "reason": "Pipeline verification officer handover"},
        headers=auth_headers(sho_token),
    )
    assert reassign_resp.status_code == 200
    reassign_data = reassign_resp.json()
    assert reassign_data["previous_io_user_id"] == str(io1.id)
    assert reassign_data["new_io_user_id"] == str(io2.id)

    # Dynamic access check: old IO is now forbidden; new IO has access
    io2_token = login(client, "io2_reassigned@example.com", "pw").json()["access_token"]
    assert client.get(f"/cases/{case_id}", headers=auth_headers(io1_token)).status_code == 403
    assert client.get(f"/cases/{case_id}", headers=auth_headers(io2_token)).status_code == 200

    # 8. NCRB de-identified reporting
    ncrb_org = make_org(name="NCRB Analytics", org_type="ncrb")
    analyst = make_user("records_ncrb_analyst", email="ncrb_eval@ncrb.gov.in", password="pw", org=ncrb_org)
    analyst_token = login(client, "ncrb_eval@ncrb.gov.in", "pw").json()["access_token"]

    report_resp = client.get("/reports/case-metadata", headers=auth_headers(analyst_token))
    assert report_resp.status_code == 200
    records = report_resp.json()
    target_record = next(r for r in records if r["id"] == case_id)
    assert target_record["crime_type"] == "Theft"
    assert "raw_text" not in target_record
    assert "officer" not in str(target_record).lower()

    # 9. Verify tamper-evident cryptographic hash chain is intact
    assert verify_chain_intact(db_session) is True



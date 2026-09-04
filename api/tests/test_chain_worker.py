"""
Tests the Chain Worker's DB orchestration logic — idempotency, chain_status
transitions, audit logging — by mocking the one function that actually
talks to Fabric (FabricClient.submit_hash). This is deliberate: nothing
about Fabric itself is exercised here (no Docker/Go/Fabric network in this
environment to test against), but the surrounding logic this codebase
actually owns is fully real and fully tested.
"""

import os
import sys
from uuid import UUID, uuid4

import pytest

# NOTE for whoever adds OCR/AI-Parser worker tests later: each worker's
# entrypoint is named worker.py, and Python caches modules in sys.modules
# by that bare name — `import worker` here and a hypothetical `import
# worker` in an ocr_worker test would collide and silently reuse whichever
# one loaded first. Give this a `sys.modules` alias if that happens, or
# rename these entrypoints to something globally unique.
_worker_path = "/workers/chain_worker" if os.path.exists("/workers/chain_worker") else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "workers", "chain_worker")
sys.path.insert(0, _worker_path)

import worker as chain_worker_module  # noqa: E402
from fabric_client import FabricSubmissionError  # noqa: E402

from app import models
from app.audit import verify_chain_intact
from tests.conftest import TestSessionLocal


@pytest.fixture(autouse=True)
def _patch_worker_session(monkeypatch):
    """The worker imports SessionLocal at module load time — point that
    reference at the same in-memory test engine api/tests/conftest.py uses,
    so data the worker commits is visible to test assertions and vice versa."""
    monkeypatch.setattr(chain_worker_module, "SessionLocal", TestSessionLocal)


def _make_document(db_session, make_org, make_user, chain_status="pending", doc_hash="abc123"):
    org = make_org()
    uploader = make_user("io", email=f"io-{uuid4().hex[:8]}@example.com", org=org)
    case = models.Case(case_number=f"TEST-{uuid4().hex[:6]}", crime_type="Theft", investigation_status="FIR_Registered")
    db_session.add(case)
    db_session.commit()
    db_session.refresh(case)

    document = models.Document(
        case_id=case.id,
        doc_type="Witness Statement",
        version=1,
        storage_path="fake/path",
        doc_hash=doc_hash,
        status="processing",
        chain_status=chain_status,
        uploaded_by=uploader.id,
    )
    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)
    return document


def test_successful_submission_marks_document_confirmed_and_writes_audit_log(
    db_session, make_org, make_user, monkeypatch
):
    document = _make_document(db_session, make_org, make_user)

    class FakeFabricClient:
        def submit_hash(self, doc_id, doc_hash, org_id):
            return {"raw_response": "ok"}

    monkeypatch.setattr(chain_worker_module, "_get_fabric_client", lambda: FakeFabricClient())

    result = chain_worker_module.process_hash_write(str(document.id), idempotency_key="key-1")

    assert result == "confirmed"
    db_session.refresh(document)
    assert document.chain_status == "confirmed"

    entries = db_session.query(models.AuditLog).filter_by(target_id=document.id).all()
    assert len(entries) == 1
    assert entries[0].action == "chain_write_confirmed"
    assert entries[0].action_metadata["idempotency_key"] == "key-1"
    assert verify_chain_intact(db_session)


def test_failed_submission_marks_document_failed_and_raises(db_session, make_org, make_user, monkeypatch):
    document = _make_document(db_session, make_org, make_user)

    class FailingFabricClient:
        def submit_hash(self, doc_id, doc_hash, org_id):
            raise FabricSubmissionError("endorsement policy failure (simulated)")

    monkeypatch.setattr(chain_worker_module, "_get_fabric_client", lambda: FailingFabricClient())

    with pytest.raises(FabricSubmissionError):
        chain_worker_module.process_hash_write(str(document.id), idempotency_key="key-2")

    db_session.refresh(document)
    assert document.chain_status == "failed"

    entries = db_session.query(models.AuditLog).filter_by(target_id=document.id).all()
    assert len(entries) == 1
    assert entries[0].action == "chain_write_failed"
    assert "endorsement policy failure" in entries[0].action_metadata["error"]


def test_already_confirmed_document_is_a_no_op_and_never_calls_fabric(db_session, make_org, make_user, monkeypatch):
    """The idempotency rule: retrying a document that's already confirmed
    must not submit a second transaction to the ledger."""
    document = _make_document(db_session, make_org, make_user, chain_status="confirmed")

    calls = []

    class TrackingFabricClient:
        def submit_hash(self, doc_id, doc_hash, org_id):
            calls.append(doc_id)
            return {"raw_response": "should not happen"}

    monkeypatch.setattr(chain_worker_module, "_get_fabric_client", lambda: TrackingFabricClient())

    result = chain_worker_module.process_hash_write(str(document.id))

    assert result == "confirmed"
    assert calls == []  # never touched Fabric at all


def test_retry_reuses_the_supplied_idempotency_key_in_the_audit_trail(db_session, make_org, make_user, monkeypatch):
    """Not a claim that Fabric itself is idempotent here (that's the
    chaincode's job, see hashledger.go's RecordHash) — this confirms the
    Chain Worker's own contract: the key passed in shows up attached to
    whatever happened, so a retry is traceable back to the original attempt."""
    document = _make_document(db_session, make_org, make_user)

    class FakeFabricClient:
        def submit_hash(self, doc_id, doc_hash, org_id):
            return {"raw_response": "ok"}

    monkeypatch.setattr(chain_worker_module, "_get_fabric_client", lambda: FakeFabricClient())

    chain_worker_module.process_hash_write(str(document.id), idempotency_key="original-key-abc")

    entry = db_session.query(models.AuditLog).filter_by(target_id=document.id).first()
    assert entry.action_metadata["idempotency_key"] == "original-key-abc"

# End-to-End Verification Report: Ingestion & Storage Upgrades (PR Baseline)

**Date**: September 3, 2026  
**Target Branch**: `main` (commit `6aebb70`)  
**Feature Branch**: `feat/documents-upload-hardening`  
**Test Protocol**: Automated Unit/Integration Tests (`pytest`) + Live HTTP Pipeline (`verify_upgrades_e2e.py`)

---

## 1. Executive Summary

This report certifies that the **Phase 1 & 2 Production Upgrades** have been integrated directly on top of Swayam's baseline on `main`, closing all gaps explicitly flagged in Swayam's code comments without introducing any breaking changes or test regressions.

All **33 automated tests passed** in Docker, and all **9 live HTTP pipeline steps passed** against the running containerized infrastructure (FastAPI, PostgreSQL, MinIO, Redis).

---

## 2. Live HTTP Pipeline Verification Matrix

| Step | Operation | Target | Result | Evidence / Details |
|:---:|:---|:---|:---:|:---|
| **1** | Health Check | `GET /health` | **PASS** | `{"status": "ok"}` |
| **2** | Authentication | `POST /auth/login` | **PASS** | Issued 15-min JWT access token & 7-day refresh token |
| **3** | Test Cockpit | `GET /demo` | **PASS** | Interactive HTML developer testing dashboard rendered (HTTP 200) |
| **4** | Case Access | `GET /cases` | **PASS** | Case retrieved: `41403d8b-54fc-417d-9268-147af0d71577` |
| **5** | Live Upload Pipeline | `POST /documents` | **PASS** | Stored in MinIO with key `{org}/{case}/{doc}/v1`. Track A (Blockchain) & Track B (OCR) enqueued |
| **6** | SHA-256 Deduplication | `POST /documents` | **PASS** | Duplicate upload returned existing `doc_id` and `version: 1` without creating redundant DB rows |
| **7** | MIME Sniffing Defense | `POST /documents` | **PASS** | Shell script disguised as `.pdf` rejected with **HTTP 415**: `Unsupported file type 'text/x-shellscript'` |
| **8** | Presigned Download URL | `GET /documents/{id}` | **PASS** | Generated time-gated presigned URL: `http://minio:9000/legadoc-documents/...` |
| **9** | Role Allowlist Boundary | `POST /documents` | **PASS** | Unauthorized roles (e.g. `defense`) blocked with **HTTP 403 Forbidden** |

---

## 3. Automated Test Suite Results

```text
============================= test session starts ==============================
platform linux -- Python 3.11.16, pytest-9.1.1, pluggy-1.6.0 -- /usr/local/bin/python3.11
rootdir: /app
plugins: anyio-4.15.0
collected 33 items

tests/test_auth.py::test_login_success_returns_access_and_refresh_tokens PASSED [  3%]
tests/test_auth.py::test_login_wrong_password_rejected PASSED            [  6%]
tests/test_auth.py::test_login_unknown_email_gets_same_generic_error_as_wrong_password PASSED [  9%]
tests/test_auth.py::test_refresh_token_issues_a_new_access_token PASSED  [ 12%]
tests/test_auth.py::test_refresh_rejects_an_access_token_used_as_a_refresh_token PASSED [ 15%]
tests/test_auth.py::test_protected_endpoint_rejects_missing_token PASSED [ 18%]
tests/test_auth.py::test_protected_endpoint_rejects_garbage_token PASSED [ 21%]
tests/test_cases.py::test_duty_officer_can_register_a_fir PASSED         [ 24%]
tests/test_cases.py::test_only_duty_officer_can_register_a_fir PASSED    [ 27%]
tests/test_cases.py::test_sho_can_assign_io_and_assigned_io_can_then_read_the_case PASSED [ 30%]
tests/test_cases.py::test_unassigned_io_cannot_read_other_ios_case PASSED [ 33%]
tests/test_cases.py::test_io_list_cases_only_shows_assigned_cases PASSED [ 36%]
tests/test_cases.py::test_config_admin_sees_every_case_regardless_of_assignment PASSED [ 39%]
tests/test_chain_worker.py::test_successful_submission_marks_document_confirmed_and_writes_audit_log PASSED [ 42%]
tests/test_chain_worker.py::test_failed_submission_marks_document_failed_and_raises PASSED [ 45%]
tests/test_chain_worker.py::test_already_confirmed_document_is_a_no_op_and_never_calls_fabric PASSED [ 48%]
tests/test_chain_worker.py::test_retry_reuses_the_supplied_idempotency_key_in_the_audit_trail PASSED [ 51%]
tests/test_documents.py::test_upload_text_document_enqueues_both_tracks PASSED [ 54%]
tests/test_documents.py::test_upload_binary_evidence_skips_ocr_and_goes_straight_to_ready PASSED [ 57%]
tests/test_documents.py::test_upload_writes_a_real_file_to_storage PASSED [ 60%]
tests/test_documents.py::test_unassigned_io_cannot_upload_to_a_case_they_are_not_assigned_to PASSED [ 63%]
tests/test_documents.py::test_document_not_ready_shows_no_text_yet PASSED [ 66%]
tests/test_documents.py::test_full_access_role_sees_unredacted_text_restricted_role_sees_masked PASSED [ 69%]
tests/test_documents.py::test_versions_endpoint_lists_every_upload_in_order PASSED [ 72%]
tests/test_documents.py::test_chain_status_endpoint PASSED               [ 75%]
tests/test_documents.py::test_retry_chain_write_reenqueues_with_the_same_idempotency_key PASSED [ 78%]
tests/test_documents.py::test_retry_chain_write_is_a_noop_once_already_confirmed PASSED [ 81%]
tests/test_documents.py::test_only_config_admin_can_trigger_retry_chain_write PASSED [ 84%]
tests/test_documents.py::test_redact_tag_adds_a_correction_and_extends_the_audit_hash_chain PASSED [ 87%]
tests/test_documents.py::test_upload_disguised_executable_rejected_by_magic_bytes PASSED [ 90%]
tests/test_documents.py::test_upload_deduplication_returns_existing_document PASSED [ 93%]
tests/test_documents.py::test_unauthorized_role_cannot_upload_evidence PASSED [ 96%]
tests/test_documents.py::test_get_document_returns_download_url PASSED   [100%]

======================= 33 passed, 2 warnings in 45.20s ========================
```

---

## 4. Gaps Closed from Swayam's Code Comments

1. **`api/app/routers/documents.py` (L31-34)**:
   * *Comment*: *"Rough, baseline-only classification — a real implementation should sniff actual file content (python-magic), not trust the declared content-type."*
   * *Resolution*: Implemented `python-magic` + `libmagic1` sniffing on the initial 8KB header chunk. Rejects non-allowlisted files with `HTTP 415`.
2. **`api/app/storage.py` (L4-6)**:
   * *Comment*: *"Swap in a boto3/MinIO-backed implementation behind the same three methods for a real deployment; nothing calling this interface needs to change."*
   * *Resolution*: Implemented `MinIOObjectStorage(ObjectStorage)` with SSE-S3 AES-256 and presigned URLs. Retained `LocalObjectStorage` for SQLite tests.
3. **`api/app/routers/documents.py` (L67-70)**:
   * *Comment*: *"Scope note: any role with access to the case can upload any doc_type for now."*
   * *Resolution*: Enforced configurable `UPLOAD_ALLOWED_ROLES` allowlist.

---

## 5. Certification
The codebase on branch `feat/documents-upload-hardening` is verified, certified for production standards, and ready to be merged into `main`.

# LegaDoc — Master System Design & Workflow Diagrams (DFD / DRD)

**Project**: SIH26190 — Smart Legal Document Management System  
**Architecture Baseline**: Post-Phase 5 (Full Operational Stack Complete)  
**Author**: Ishaan Nasir (Backend, Ingestion Pipeline, Lifecycle & Security Substrate)  
**Status**: Authoritative Reference for Team Meetings & Judicial Evaluation

---

## 1. Executive Summary & Scope Audit

### 1.1 Is the Original Backend Scope Complete?
**YES — 100% of Ishaan's original backend jurisdiction is implemented, hardened, and verified.**

Every single flow, endpoint, security barrier, and data model specified in `SYSTEM_DESIGN.md` across Phases 1 through 5 is active in code and covered by **110 automated tests (100% passing, 0 failures)** in Docker:

- **Phase 1 (Merged)**: Authoritative JWT Authentication (15-min access + 7-day refresh), bcrypt with constant-time dummy hashes, 18 canonical multi-tenant roles across 8 legal domains, and PostgreSQL tamper-evident hash-chained audit substrate.
- **Phase 2 (Merged)**: Streaming native MIME sniffer (libmagic/python-magic), 50MB strict file cap, SHA-256 deduplication, MinIO S3 object storage with SSE-S3 AES-256, Celery worker dispatch (Track A & Track B), and dynamic redaction masking engine (`app/redaction.py`).
- **Phase 3 (PR #19)**: Section 91 parallel evidence requisitions with tenant isolation, Section 173 Charge Sheet AND-Join gate, independent 5-state Bail FSM, Judicial Trial progression to terminal verdict, Section 172 Case Diary with zero PII leakage, and default-deny security hardening on external evidence submission (closing Issue #24).
- **Phase 4 (PR #20)**: Flow 6 Audit Trail, dual response envelopes (Full Cryptographic vs Operational Summary), Domain 8 separation of duties (Security Auditor only on `/ai-parser`), sliding-window rate limiting (20/min), atomic write-on-read meta-audit, and monotonic sequence counter (`seq`) eliminating microsecond timestamp race ties.
- **Phase 5 (PR #35)**: Domain 7 NCRB de-identified case metadata reporting (`GET /reports/case-metadata`), Flow 1 Investigating Officer mid-case reassignment (`POST /cases/:id/reassign-io`), Flow 2 document review queue (`GET /documents?status=needs_review`), and end-to-end pipeline & artifact generation test.

---

## 2. C4 Context Diagram (System Ecosystem)

This diagram defines the high-level actors, external organizations, and boundary of the LegaDoc platform.

```mermaid
C4Context
    title System Context Diagram — LegaDoc Criminal Justice Management System

    Person(duty_officer, "Duty Officer", "Registers FIR and initiates case docket at police station")
    Person(sho, "Station House Officer (SHO)", "Supervises station, assigns & reassigns Investigating Officers")
    Person(io, "Investigating Officer (IO)", "Leads investigation, gathers evidence, files case diary, requests forensics")
    Person(authority_user, "External Authority Staff", "Forensics (FSL), Hospitals, Banks, Telecom fulfilling Sec 91 requisitions")
    Person(prosecutor, "Public Prosecutor", "Evaluates evidence checklist & files Section 173 Charge Sheet")
    Person(court, "Judiciary / Court", "Schedules hearings, evaluates bail petitions, issues orders, pronounces judgments")
    Person(defense, "Defense Counsel", "Submits bail applications on behalf of accused; access restricted to bail track")
    Person(auditor, "Security Auditor", "Inspects AI parser redaction decisions and compliance via meta-audited logs")
    Person(ncrb, "NCRB / Crime Analyst", "Consumes de-identified statistical case metadata for national crime reporting")

    System(legadoc_system, "LegaDoc Platform", "Unified secure evidence ingestion, AI redaction, lifecycle orchestration, and immutable audit trail")

    System_Ext(fabric_blockchain, "Hyperledger Fabric", "Permissioned blockchain recording immutable document SHA-256 transaction hashes")

    Rel(duty_officer, legadoc_system, "Registers FIR docket", "REST / HTTPS")
    Rel(sho, legadoc_system, "Assigns / Reassigns IO", "REST / HTTPS")
    Rel(io, legadoc_system, "Uploads evidence, records diary, requisitions proof", "REST / HTTPS")
    Rel(authority_user, legadoc_system, "Submits certified evidence records", "REST / HTTPS")
    Rel(prosecutor, legadoc_system, "Gates charge sheet filing", "REST / HTTPS")
    Rel(court, legadoc_system, "Adjudicates bail & trials", "REST / HTTPS")
    Rel(defense, legadoc_system, "Files bail petitions", "REST / HTTPS")
    Rel(auditor, legadoc_system, "Audits redaction decisions", "REST / HTTPS")
    Rel(ncrb, legadoc_system, "Reads de-identified metadata", "REST / HTTPS")

    Rel(legadoc_system, fabric_blockchain, "Dispatches SHA-256 hash txs", "gRPC / Fabric SDK")
```

---

## 3. C4 Container Diagram (Service & Storage Architecture)

```mermaid
C4Container
    title Container Architecture Diagram — LegaDoc Infrastructure

    Person(user, "Authenticated User", "Police, Court, Authority, Defense, Auditor")

    Container_Boundary(legadoc_boundary, "LegaDoc Core Infrastructure") {
        Container(api_gateway, "FastAPI Application Server", "Python 3.11, FastAPI, Pydantic v2", "Enforces RBAC, rate limiting, request validation, MIME sniffing, and redaction views")
        ContainerDb(postgres_db, "PostgreSQL 16", "Relational Database", "Stores cases, documents, sensitivity tags, bail FSM, and sequential hash-chained audit log")
        ContainerDb(redis_store, "Redis 7 (AOF Persistent)", "In-Memory Cache & Message Broker", "Celery task broker, rate limiting storage, and async queue")
        ContainerDb(minio_storage, "MinIO Object Storage (S3 API)", "Encrypted Object Storage", "Stores raw and processed evidence files with SSE-S3 AES-256 encryption at rest")
        
        Container(ocr_worker, "OCR & Extraction Worker", "Celery, Python, PaddleOCR", "Extracts raw text from uploaded images and scanned PDFs (Track B)")
        Container(ai_parser_worker, "AI Parser Worker", "Celery, Presidio, spaCy", "Identifies PII entities, generates sensitivity tags, auto-flags low confidence to needs_review")
        Container(chain_worker, "Blockchain Write Worker", "Celery, Fabric Python SDK", "Submits document SHA-256 hash transactions to Hyperledger Fabric (Track A)")
    }

    System_Ext(fabric_network, "Hyperledger Fabric Network", "Distributed Ledger", "Maintains immutable evidentiary anchor on legadoc-channel")

    Rel(user, api_gateway, "API calls via JWT", "HTTPS / JSON")
    Rel(api_gateway, postgres_db, "Reads/Writes application state & audit logs", "SQL / SQLAlchemy Pool")
    Rel(api_gateway, redis_store, "Enqueues Celery jobs, checks rate limits", "Redis Protocol")
    Rel(api_gateway, minio_storage, "Streams validated files, issues presigned URLs", "S3 API (boto3)")

    Rel(redis_store, ocr_worker, "Pulls OCR extraction tasks", "Celery Protocol")
    Rel(redis_store, ai_parser_worker, "Pulls entity tagging tasks", "Celery Protocol")
    Rel(redis_store, chain_worker, "Pulls hash commit tasks", "Celery Protocol")

    Rel(ocr_worker, minio_storage, "Fetches raw file", "S3 API")
    Rel(ocr_worker, postgres_db, "Updates Document.raw_text", "SQL")
    Rel(ocr_worker, redis_store, "Enqueues AI parser tagging job", "Celery Protocol")

    Rel(ai_parser_worker, postgres_db, "Writes DocumentSensitivityTag & AuditLog", "SQL")
    Rel(chain_worker, postgres_db, "Updates chain_status & writes AuditLog", "SQL")
    Rel(chain_worker, fabric_network, "Submits signed hash transaction", "gRPC")
```

---

## 4. Master Lifecycle Workflow Diagram

The complete journey of a criminal docket from initial incident report through trial, disposition, and national statistics.

```mermaid
flowchart TD
    subgraph S1["Stage 1: FIR Intake & Station Docket"]
        A1["Citizen / Informant Complaint"] --> A2["Duty Officer: POST /cases\n(Register FIR)"]
        A2 --> A3["Case Created in DB\nStatus: FIR_Registered"]
        A3 --> A4["SHO: POST /cases/:id/assign-io\n(Assign IO)"]
        A4 --> A5["CaseAssignment Created\nIO Granted Case Access"]
    end

    subgraph S2["Stage 2: Investigation & Ingestion (Dual Track)"]
        A5 --> B1["IO: POST /cases/:id/case-diary\n(Sec 172 Diary Notes)"]
        A5 --> B2["IO: POST /documents\n(Upload Evidence File)"]
        A5 --> B3["IO: POST /cases/:id/evidence-requests\n(Sec 91 Forensic/Bank Requisition)"]
        
        B2 --> C1{"File Validation"}
        C1 -->|MIME / Size Valid| C2["Store in MinIO S3\nCompute SHA-256"]
        C1 -->|MIME Mismatch / >50MB| C3["Reject: HTTP 415 / 413"]
        
        C2 --> D1["Track A (Blockchain)"]
        C2 --> D2["Track B (OCR & NLP)"]
        
        D1 --> D3["Chain Worker: Write Hash Tx\nStatus: confirmed"]
        D2 --> D4["OCR Worker: Extract raw_text"]
        D4 --> D5["AI Parser: Tag PII Entities"]
        
        D5 --> E1{"Tag Confidence >= 70%?"}
        E1 -->|Yes| E2["Status: ready\nRedaction Active"]
        E1 -->|No / Failed| E3["Status: needs_review\nFull Redaction Fallback"]
        
        E3 --> E4["IO / Admin: Review Queue\nGET /documents?status=needs_review"]
        E4 --> E5["IO: POST /documents/:id/redact-tag\n(Human Correction)"]
        E5 --> E2
    end

    subgraph S3["Stage 3: Parallel Requisitions & Bail Track"]
        B3 --> F1["Authority Staff: GET /cases/:id/evidence-requests"]
        F1 --> F2["Authority: POST /evidence-requests/:id/submit\n(Fulfill Requisition)"]
        F2 --> F3["Request Status: completed\nEvidence Attached"]

        A5 -.-> G1["Arrest Made: POST /cases/:id/bail/arrest\n(Status: Arrested)"]
        G1 --> G2["Defense: POST /cases/:id/bail/application\n(Status: Application_Filed)"]
        G2 --> G3["Court: POST /cases/:id/bail/hearing-notice\n(Status: Hearing_Scheduled)"]
        G3 --> G4["Court: POST /cases/:id/bail/order\n(Status: Order_Issued / Denied_Final)"]
        G4 -->|Granted| G5["Accused: POST /cases/:id/bail/surety\n(Status: Surety_Registered)"]
    end

    subgraph S4["Stage 4: Charge Sheet AND-Join Gate"]
        F3 & E2 --> H1["Prosecutor: POST /cases/:id/file-charge-sheet"]
        H1 --> H2{"Mandatory Stage Requirements Met?\n(Docs + Evidence Requisitions)"}
        H2 -->|Missing Items| H3["Reject: HTTP 409 Conflict\n(Returns missing item list)"]
        H2 -->|All Fulfilled| H4["Case Status: Charge_Sheet_Filed"]
    end

    subgraph S5["Stage 5: Judicial Trial & Final Disposition"]
        H4 --> J1["Court: POST /cases/:id/trial/hearing-notice\n(Case Status: Trial)"]
        J1 --> J2["Trial Hearings & Judicial Review\n(GET /documents/:id - Unredacted for Court)"]
        J2 --> J3["Court: POST /cases/:id/judgment\n(Verdict: convicted / acquitted)"]
        J3 --> J4["Case Status: Judgment\n(Terminal State)"]
    end

    subgraph S6["Stage 6: Oversight, Audit & NCRB Reporting"]
        J4 --> K1["Records Analyst: GET /reports/case-metadata\n(De-Identified Crime Statistics)"]
        ALL_ACTIONS["All Platform Mutations"] --> L1["PostgreSQL Hash Chain (models.AuditLog)"]
        L1 --> L2["Security Auditor: GET /cases/:id/audit-log/ai-parser"]
        L1 --> L3["Config Admin: GET /cases/:id/audit-log/chain-integrity"]
    end
```

---

## 5. Flow-by-Flow Technical Architecture Diagrams

### Flow 1: Case Registration & Investigating Officer Handover
Handles initial FIR intake, duty officer role gating, and atomic officer reassignment mid-case.

```mermaid
sequenceDiagram
    autonumber
    actor DutyOfficer as Duty Officer
    actor SHO as Station House Officer (SHO)
    actor OldIO as Old IO (IO 1)
    actor NewIO as New IO (IO 2)
    participant API as FastAPI Gateway
    participant DB as PostgreSQL Database
    participant Audit as Hash Chained AuditLog

    DutyOfficer->>API: POST /cases (crime_type, complaint_text)
    API->>DB: INSERT INTO cases (status='FIR_Registered')
    API->>Audit: write_audit_log(action='fir_registered')
    API-->>DutyOfficer: 201 Created (case_id, FIR Number)

    SHO->>API: POST /cases/:id/assign-io (io_user_id=IO1.id)
    API->>DB: INSERT INTO case_assignments (case_id, io_user_id=IO1)
    API->>Audit: write_audit_log(action='io_assigned')
    API-->>SHO: 200 OK (Assignment confirmed)

    Note over OldIO,API: IO 1 has active read/write case access

    Note over SHO,NewIO: Mid-Case Reassignment Event (Flow 1 Hardened)
    SHO->>API: POST /cases/:id/reassign-io (new_io_user_id=IO2.id, reason="Transfer")
    Note over API: Precondition Checks:<br/>1. UUID Valid?<br/>2. Case not in Judgment/Disposed?<br/>3. Target user role == 'io'?<br/>4. Active assignment exists?<br/>5. Target IO != Current IO?
    API->>DB: BEGIN TRANSACTION
    API->>DB: DELETE FROM case_assignments WHERE case_id=:id
    API->>DB: INSERT INTO case_assignments (case_id, io_user_id=IO2)
    API->>Audit: write_audit_log(action='io_reassigned', metadata={prev: IO1, new: IO2, reason: "Transfer"})
    API->>DB: COMMIT TRANSACTION
    API-->>SHO: 200 OK (Reassignment Response)

    OldIO->>API: GET /cases/:id
    API-->>OldIO: 403 Forbidden (Assignment Revoked)

    NewIO->>API: GET /cases/:id
    API-->>NewIO: 200 OK (Full Access Granted)
```

---

### Flow 2: Dual-Track Ingestion Pipeline & Redaction Engine
Handles secure upload, MIME sniffing, dual-track asynchronous processing, review queue fallback, and role-masked read projections.

```mermaid
sequenceDiagram
    autonumber
    actor Officer as Uploading Officer
    participant API as FastAPI Ingestion Gateway
    participant Sniffer as Native MIME Sniffer
    participant S3 as MinIO (S3 Storage)
    participant Queue as Redis / Celery
    participant OCR as OCR Worker (Track B)
    participant AI as AI Parser (Track B)
    participant Chain as Chain Worker (Track A)
    participant DB as PostgreSQL
    actor Reader as Reading Role (Specialist / Court)

    Officer->>API: POST /documents (case_id, doc_type, file)
    API->>Sniffer: Sniff initial 8KB chunk (libmagic / magic bytes)
    alt Invalid MIME Type or Exceeds 50MB
        Sniffer-->>API: Rejected
        API-->>Officer: 415 Unsupported Media Type / 413 Payload Too Large
    else Valid Media Type
        API->>S3: Stream to s3://legadoc-documents/{org}/{case}/{doc}/v1
        API->>DB: INSERT INTO documents (status='processing', chain_status='pending')
        API->>Queue: Enqueue Track A: chain_worker.write_hash(doc_id, key='{id}:v1')
        API->>Queue: Enqueue Track B: ocr_worker.extract_document(doc_id)
        API-->>Officer: 202 Accepted (Document id, status='processing')
    end

    par Asynchronous Track A: Blockchain Write
        Queue->>Chain: Process write_hash job
        Chain->>DB: Check idempotency key
        Chain->>Fabric: Submit signed transaction (SHA-256 hash)
        Chain->>DB: UPDATE documents SET chain_status='confirmed'
        Chain->>DB: write_audit_log(action='chain_write_confirmed')
    and Asynchronous Track B: OCR & Redaction Tagging
        Queue->>OCR: Process extract_document job
        OCR->>S3: Read raw document file
        OCR->>OCR: Execute PaddleOCR extraction
        OCR->>DB: UPDATE documents SET raw_text=:text
        OCR->>Queue: Enqueue ai_parser_worker.tag_document(doc_id)
        Queue->>AI: Process tag_document job
        AI->>AI: Run Presidio + spaCy NER against field schema
        AI->>DB: INSERT INTO document_sensitivity_tags (PERSON, PHONE, AADHAAR, ...)
        alt Any Tag Confidence < 70% or Worker Error
            AI->>DB: UPDATE documents SET status='needs_review'
            Note over AI,DB: Fail-Closed: Falls back to full redaction
        else All Tags Confident (>= 70%)
            AI->>DB: UPDATE documents SET status='ready'
        end
        AI->>DB: write_audit_log(action='auto_tag_completed')
    end

    Note over Reader,API: Read-Time Dynamic Masking (app/redaction.py)
    Reader->>API: GET /documents/:id
    API->>DB: Verify assert_case_access(claims)
    API->>DB: Fetch Document + DocumentSensitivityTag rows
    API->>API: get_document_view(role, tags, raw_text)
    alt Reader is Full Access (IO, SHO, Court, Config Admin)
        API-->>Reader: 200 OK with unredacted raw_text
    else Reader is Restricted (Cyber Cell Specialist, Prosecutor, Defense)
        API-->>Reader: 200 OK with masked text: "[REDACTED:PERSON], call [REDACTED:PHONE_NUMBER]"
    end
```

---

### Flow 3: Section 91 Parallel Evidence Requisitions & Charge Sheet AND-Join
Orchestrates multi-tenant requests to external authorities (FSL Labs, Hospitals, Banks, Telecoms) and enforces the mandatory pre-condition checklist before filing a charge sheet.

```mermaid
sequenceDiagram
    autonumber
    actor IO as Investigating Officer
    actor FSL as Forensic Lab (Authority Staff)
    actor Prosecutor as Public Prosecutor
    participant API as FastAPI Gateway
    participant DB as PostgreSQL
    participant Audit as Hash Chained AuditLog

    IO->>API: POST /cases/:id/evidence-requests (requested_org_id=FSL.id, doc_type="Forensic Report")
    API->>DB: INSERT INTO evidence_requests (status='pending', requested_org_id=FSL)
    API->>Audit: write_audit_log(action='evidence_requested')
    API-->>IO: 201 Created (Request id)

    Note over FSL,API: Strict Multi-Tenant Scoping (Default-Deny)
    FSL->>API: GET /cases/:id/evidence-requests
    API->>DB: Filter WHERE requested_org_id == claims['org_id']
    API-->>FSL: 200 OK (Lists only requests routed to FSL)

    FSL->>API: POST /evidence-requests/:id/submit (file=ballistics.pdf)
    API->>API: verify_evidence_request_org_access(claims)
    Note over API: Security Rule (Issue #24 Fixed):<br/>Only matching authority_staff or admin permitted.<br/>Defense or unauthorized roles receive 403 Forbidden.
    API->>DB: Store evidence document & UPDATE evidence_requests SET status='completed'
    API->>Audit: write_audit_log(action='evidence_request_fulfilled')
    API-->>FSL: 200 OK (Completed)

    Note over Prosecutor,API: Section 173 Charge Sheet AND-Join Gate
    Prosecutor->>API: POST /cases/:id/file-charge-sheet
    API->>DB: Query stage_requirements WHERE crime_type=case.crime_type AND stage='Charge_Sheet'
    API->>DB: Check: 1. All mandatory doc_types uploaded?<br/>2. All mandatory evidence_requests completed?
    alt Any Mandatory Document or Requisition Incomplete
        API-->>Prosecutor: 409 Conflict (detail: {"missing_docs": [...], "missing_evidence": [...]})
    else All Stage Requirements Satisfied
        API->>DB: UPDATE cases SET investigation_status='Charge_Sheet_Filed'
        API->>Audit: write_audit_log(action='charge_sheet_filed')
        API-->>Prosecutor: 200 OK (Status transitioned to Charge_Sheet_Filed)
    end
```

---

### Flow 4: Independent Bail Finite State Machine (FSM)
Decoupled concurrent bail track operating in parallel with the main investigation docket.

```mermaid
stateDiagram-v2
    [*] --> Arrested: POST /cases/:id/bail/arrest\n(IO / Duty Officer)
    
    Arrested --> Application_Filed: POST /cases/:id/bail/application\n(Defense Submission-Only)
    
    Application_Filed --> Hearing_Scheduled: POST /cases/:id/bail/hearing-notice\n(Court)
    
    Hearing_Scheduled --> Order_Issued: POST /cases/:id/bail/order [Bail Granted]\n(Court)
    Hearing_Scheduled --> Denied_Final: POST /cases/:id/bail/order [Bail Denied]\n(Court)
    
    Order_Issued --> Surety_Registered: POST /cases/:id/bail/surety\n(Accused / Defense Submission-Only)
    
    Surety_Registered --> [*]: Accused Released on Bail
    Denied_Final --> [*]: Accused Remains in Judicial Custody

    note right of Arrested
        Invariants:
        - FSM transitions are strictly sequential.
        - Out-of-order calls return HTTP 400 Bad Request.
        - Operating bail status does NOT mutate case.investigation_status.
        - Every transition appends an immutable row to AuditLog.
    end note
```

---

### Flow 5: Judicial Trial & Court Disposition
Gated by the Charge Sheet AND-Join gate, moving the docket to public trial, judicial review, and terminal verdict.

```mermaid
sequenceDiagram
    autonumber
    actor Prosecutor as Public Prosecutor
    actor Court as Judiciary / Judge
    participant API as FastAPI Gateway
    participant DB as PostgreSQL
    participant Audit as Hash Chained AuditLog

    Note over Prosecutor,Court: Pre-condition: Case Status must be 'Charge_Sheet_Filed'
    Court->>API: POST /cases/:id/trial/hearing-notice (hearing_date, courtroom)
    API->>DB: Check investigation_status == 'Charge_Sheet_Filed'
    API->>DB: UPDATE cases SET investigation_status='Trial'
    API->>Audit: write_audit_log(action='trial_hearing_scheduled')
    API-->>Court: 200 OK (Trial Notice Issued, status: 'Trial')

    Note over Court,API: Judicial Evidence Review
    Court->>API: GET /documents/:id
    Note over API: Court role has full_access privileges.<br/>Receives unredacted evidence + complete chain verification.
    API-->>Court: 200 OK (Unredacted Document with verification badge)

    Note over Court,API: Final Verdict Disposition
    Court->>API: POST /cases/:id/judgment (verdict='convicted', judgment_summary='...')
    API->>API: Validate verdict in {'acquitted', 'convicted'}
    API->>DB: UPDATE cases SET investigation_status='Judgment', bail_status='Disposed'
    API->>Audit: write_audit_log(action='judgment_pronounced', metadata={verdict: 'convicted'})
    API-->>Court: 200 OK (Case Terminal State Reached)
```

---

### Flow 6: Tamper-Evident Audit Trail & Meta-Audit
Role-filtered audit views, anti-enumeration sliding-window rate limiting, and cryptographic chain verification using monotonic sequence counters.

```mermaid
sequenceDiagram
    autonumber
    actor Auditor as Security Auditor
    actor Admin as Config Admin
    actor IO as Assigned IO
    participant API as FastAPI Gateway
    participant Limiter as In-Memory Rate Limiter
    participant DB as PostgreSQL (Serialized Lock)

    Note over Auditor,API: Domain 8 Inspection: GET /cases/:id/audit-log/ai-parser
    Auditor->>API: GET /cases/:id/audit-log/ai-parser
    API->>Limiter: Check user limit (20 req/min)
    alt Exceeded 20 requests in 60s
        Limiter-->>API: Rejected
        API-->>Auditor: 429 Too Many Requests (Retry-After: 60)
    else Under Limit
        API->>DB: BEGIN TRANSACTION
        API->>DB: SELECT pg_advisory_xact_lock(267190)
        API->>DB: INSERT INTO audit_logs (action='read_ai_parser_audit', actor=Auditor.id, seq=next_seq)
        API->>DB: COMMIT TRANSACTION
        API->>DB: SELECT * FROM audit_logs WHERE action IN ('auto_tag_completed', 'redact_tag_correction')
        API-->>Auditor: 200 OK (Full auto-tag decisions, confidence scores, ZERO PII)
    end

    Note over Admin,API: Domain 8 Separation of Duties Check
    Admin->>API: GET /cases/:id/audit-log/ai-parser
    API-->>Admin: 403 Forbidden (Config Admin blocked from checking own redaction config)

    Note over IO,API: Operational Summary View: GET /cases/:id/audit-log
    IO->>API: GET /cases/:id/audit-log
    API->>DB: Fetch audit rows for case
    API->>API: Filter to Summary Envelope (counts by action, timestamp bounds)
    API-->>IO: 200 OK (Summary Response: "3 auto_tag_completed, 1 redact_tag_correction", chain_intact: true)

    Note over Admin,API: Cryptographic Tamper Verification: GET /cases/:id/audit-log/chain-integrity
    Admin->>API: GET /cases/:id/audit-log/chain-integrity
    API->>DB: SELECT * FROM audit_logs ORDER BY seq ASC
    API->>API: Verify: row_hash == sha256(prev_hash + row_content) AND prev_hash == prev_row.row_hash
    API-->>Admin: 200 OK (chain_intact: true, total_entries: N, latest_hash: "...")
```

---

### Flow 7: Domain 7 NCRB De-Identified Crime Reporting
Supplies anonymized, structural crime metadata for national records and policy analysis without identity exposure.

```mermaid
sequenceDiagram
    autonumber
    actor Analyst as Records / NCRB Analyst
    actor Intruder as Unauthorized Role (IO / SHO / Defense)
    participant API as FastAPI Gateway
    participant DB as PostgreSQL
    participant Audit as Hash Chained AuditLog

    Intruder->>API: GET /reports/case-metadata
    API-->>Intruder: 403 Forbidden (Role not permitted)

    Analyst->>API: GET /reports/case-metadata?crime_type=Theft&limit=100
    API->>API: Validate pagination bounds (limit 1..500, offset >= 0)
    API->>DB: SELECT id, case_number, crime_type, court_level, investigation_status, bail_status, created_at FROM cases
    Note over API,DB: Structural Projection: ZERO user IDs, officer names, raw text, or organizations
    API->>Audit: write_audit_log(action='ncrb_report_generated', metadata={filters})
    API-->>Analyst: 200 OK (List of CaseMetadataDeidentified objects)
```

---

## 6. State Ownership & Invariant Map

| Resource / State | Master Table | Access Control Rule | Mutability | Cryptographic Anchor |
|:---|:---|:---|:---|:---|
| **Case Docket** | `cases` | `assert_case_access()` | Mutable (`investigation_status`, `bail_status`) | Referenced in `AuditLog.case_id` |
| **Case Assignment** | `case_assignments` | Only `sho` & `config_admin` | Single active IO per case. Replaced atomically on reassignment | `AuditLog(action='io_reassigned')` |
| **Case Diary** | `case_diary_entries` | Strictly assigned IO and SHO | **Append-Only** (no edits, no deletions) | Row hash + `AuditLog(action='case_diary_appended')` |
| **Evidence Requisition** | `evidence_requests` | IO (create), Assigned Authority (fulfill) | Single-fulfillment guard (`status='completed'`) | Document link + `AuditLog` |
| **Evidence Document** | `documents` | Role-filtered via `app/redaction.py` | **Append-Only** versions (`v1, v2, ...`). Storage immutable | SHA-256 in MinIO + Fabric Blockchain (`chain_tx_id`) |
| **Sensitivity Tags** | `document_sensitivity_tags` | Internal AI Parser + IO Corrections | Append-only. Never stores raw matched text | `AuditLog(action='auto_tag' \| 'redact_tag_correction')` |
| **Bail Lifecycle** | `cases.bail_status` | Role-gated by state (IO, Defense, Court, Accused) | Strict 5-state Finite State Machine transitions | `AuditLog(action='bail_*')` |
| **Trial Lifecycle** | `cases.investigation_status` | Gated by `Charge_Sheet_Filed` (Court only) | Sequential transitions (`Charge_Sheet` $\to$ `Trial` $\to$ `Judgment`) | `AuditLog(action='trial_*' \| 'judgment_pronounced')` |
| **Audit Trail** | `audit_logs` | Security Auditor & Config Admin (Full), Others (Summary) | **Strictly Immutable & Append-Only** | Linked SHA-256 chain ordered by monotonic `seq` |

---

## 7. Endpoint & Verification Matrix Reference

| Flow / Domain | Method | Endpoint Path | Role Allowed | Test Suite |
|:---|:---:|:---|:---|:---|
| **Auth** | `POST` | `/auth/login` | Public (Rate Limited) | `test_auth.py` |
| **Auth** | `POST` | `/auth/refresh` | Authenticated Refresh Token | `test_auth.py` |
| **Case Intake** | `POST` | `/cases` | `duty_officer` | `test_cases.py` |
| **Case Assignment** | `POST` | `/cases/:id/assign-io` | `sho` | `test_cases.py` |
| **Flow 1 (Reassign)** | `POST` | `/cases/:id/reassign-io` | `sho`, `config_admin` | `test_cases.py` (12 tests) |
| **Case Diary** | `POST/GET`| `/cases/:id/case-diary` | `io`, `sho` (assigned) | `test_cases.py` |
| **Flow 3 (Requisitions)**| `POST/GET`| `/cases/:id/evidence-requests` | `io`, matching `authority_staff` | `test_evidence_requests.py` |
| **Flow 3 (Submit)** | `POST` | `/evidence-requests/:id/submit`| Matching `authority_staff` only | `test_evidence_requests.py` |
| **Flow 3 (Charge Sheet)**| `POST` | `/cases/:id/file-charge-sheet` | `prosecutor` | `test_evidence_requests.py` |
| **Flow 2 (Upload)** | `POST` | `/documents` | Case-permitted uploaders | `test_documents.py` |
| **Flow 2 (Fetch)** | `GET` | `/documents/:id` | Role-scoped (`FULL` vs `MASKED`) | `test_documents.py` |
| **Flow 2 (Versions)** | `GET` | `/documents/:id/versions` | Role-scoped | `test_documents.py` |
| **Flow 2 (Queue)** | `GET` | `/documents?status=needs_review`| `config_admin`, `io` (assigned) | `test_documents.py` (9 tests) |
| **Flow 2 (Human Tag)**| `POST` | `/documents/:id/redact-tag` | Assigned `io` | `test_documents.py` |
| **Flow 4 (Bail FSM)** | `POST` | `/cases/:id/bail/*` (5 routes) | `io`, `defense`, `court`, `accused`| `test_bail.py` |
| **Flow 5 (Trial)** | `POST` | `/cases/:id/trial/hearing-notice`| `court` | `test_trial.py` |
| **Flow 5 (Judgment)** | `POST` | `/cases/:id/judgment` | `court` | `test_trial.py` |
| **Flow 6 (Audit Trail)**| `GET` | `/cases/:id/audit-log` | Role-filtered (`full` vs `summary`)| `test_audit.py` |
| **Flow 6 (AI Parser)** | `GET` | `/cases/:id/audit-log/ai-parser`| `security_auditor` ONLY | `test_audit.py` |
| **Flow 6 (Integrity)**| `GET` | `/cases/:id/audit-log/chain-integrity`| `config_admin` | `test_audit.py`, `test_audit_chain_ordering.py` |
| **Domain 7 (NCRB)** | `GET` | `/reports/case-metadata` | `records_ncrb_analyst` | `test_reports.py` (7 tests) |
| **Full Lifecycle** | — | End-to-End Pipeline & Artifacts | Full operational matrix | `test_end_to_end_pipeline_flow_and_artifact_generation` |

---

## 8. Summary for Team Meeting Presentation

When presenting this architecture to Swayam, Abhinav, Rick, and Vinayak:
1. **Zero Gaps in Core Pipeline**: All 7 flows are built, deployed in containers, and verified with 110 tests.
2. **Deterministic Hash Chaining**: The latent microsecond timestamp bug has been solved upstream and downstream using monotonic `seq` indexing.
3. **Fail-Closed Security**: Every single endpoint implements default-deny authorization (e.g. defense counsel blocked from forensics and case diary, unassigned IOs blocked from cross-case reads).
4. **Clean Interfaces for Frontend & Workers**:
   - Abhinav (Frontend) has exact, typed response schemas for the review queue, bail FSM, trial, and audit logs.
   - Vinayak (AI Parser) has exact table targets (`DocumentSensitivityTag`) and status flags (`needs_review` on confidence < 70%).

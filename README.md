# SIH26190 — Secure Digital Document Management System

A multi-organization case management system for law enforcement, forensic,
medical, and judicial bodies — FIR through investigation, parallel evidence
collection, an independently-running bail track, charge sheet filing, and
court disposition, with AI-assisted redaction and blockchain-based tamper
evidence.

## Start here

- **[SYSTEM_DESIGN.md](SYSTEM_DESIGN.md)** — the full architecture: every
  diagram, every connection between components (with failure modes and
  tooling), every flow end-to-end, every domain's view into the platform,
  the complete API contract, and the build/security checklist. This is the
  **single source of truth** — if code and this document disagree, the
  document wins until it's deliberately updated. Keep it that way: when you
  change a decision in code, update this file in the same change, not later.

A readable Word version and a point-in-time audit report exist but aren't
kept in this repo — regenerating a full Word doc (17 rendered diagrams) on
every edit isn't worth the overhead while this is still under active,
parallel development. Ask if you need either regenerated.

## Current build status

This is a **baseline scaffold**, not a working product yet. Every endpoint
in `api/app/routers/` exists as a real route with the correct method, path,
role restriction, and docstring — but returns `501 Not Implemented`. Every
worker has a real Celery task registered with a docstring describing exactly
what it needs to do. Nothing has business logic wired in yet. That's
intentional: this is the shape for each domain to build into, not a finished
skeleton to work around.

| Piece | Status |
|---|---|
| API routes | Stubbed, matches the endpoint table 1:1 |
| DB models | Defined, matches the State Ownership Map |
| Workers (OCR / AI Parser / Chain) | Celery tasks registered, logic not implemented |
| Fabric network | Not stood up yet — see `fabric-network/README.md`, this is the first real milestone |
| Web frontend | Routed by domain, pages are placeholders |
| Auth / RBAC | JWT issue/verify works; the login flow itself (`POST /auth/login`) is not implemented |

## Repository layout

```
api/                 FastAPI backend — one router file per resource group
  app/
    models.py         SQLAlchemy models — one class per State Ownership Map entry
    routers/           One file per endpoint-table resource group
    security.py         JWT + the one shared RBAC dependency every route uses
workers/
  ocr_worker/          PaddleOCR extraction — Flow 2, Track B
  ai_parser_worker/    Presidio + spaCy auto-redaction — Flow 2, Track B / Flow 6
  chain_worker/        Fabric hash-write — Flow 2, Track A (build/verify this first)
web/                  React (Vite) — routed by domain, not by individual role
fabric-network/       Where the Fabric connection profile & local crypto material go
db/                   No Alembic yet — see db/README.md
scripts/              setup.sh (local bring-up), seed_demo_data.py (placeholder)
```

## Running it locally

```bash
./scripts/setup.sh
```

This copies `.env.example` to `.env`, builds and starts every container, and
creates the database tables. Then:

- API: http://localhost:8000/health
- API docs (FastAPI auto-generated): http://localhost:8000/docs
- Web: http://localhost:5173
- MinIO console: http://localhost:9001

## How to add to this without breaking someone else's work

1. **New endpoint or resource?** Add it to SYSTEM_DESIGN.md's Interface
   Contracts / State Ownership Map first, then add the route/model here.
   Don't invent an endpoint or a table ad hoc — this is exactly what keeps
   multiple people's domains (backend, frontend, AI/ML, Fabric) consistent
   with each other as everyone pushes in parallel.
2. **Filling in a stub?** Replace the `raise HTTPException(501, ...)` /
   `raise NotImplementedError(...)` with real logic. The docstring on every
   stub says what it needs to do and which section of SYSTEM_DESIGN.md to
   check for the exact behavior (fail-safe rules, idempotency rules, RBAC
   scoping) — read it before writing the implementation.
3. **Changing a decision?** SYSTEM_DESIGN.md's "Open Questions" section
   tracks what's still genuinely undecided. Everything else in it is meant
   to be treated as settled unless you have a specific reason to reopen it —
   raise that with the team, don't silently diverge from the doc in code.

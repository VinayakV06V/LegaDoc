"""
Blockchain Write Worker — Python / fabric-sdk-py, submitting signed hash
transactions to Hyperledger Fabric. See SYSTEM_DESIGN.md Flow 2 Track A and
the System Connections table, arrows #8/#13/#14.

This is the single highest-setup-risk component in the system (per the Build
Prompt Seed) — stand this up and confirm one signed transaction end-to-end
in isolation before wiring anything else to it.
"""

from celery import Celery

app = Celery(
    "chain_worker",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/1",
)


@app.task(name="chain_worker.write_hash", bind=True, max_retries=5)
def write_hash(self, document_id: str, idempotency_key: str = None):
    """
    TODO:
      1. Read the document's hash from the DB (arrow #13).
      2. Sign it with the submitting org's Fabric MSP identity.
      3. Submit the signed transaction via the Fabric Gateway (arrow #14).
      4. On confirmation, update chain_status="confirmed".

    idempotency_key: pass the ORIGINAL key when this task is invoked via
    POST /documents/:id/retry-chain-write — never mint a new one. If Fabric
    actually confirmed the transaction before a prior crash, reusing the key
    is what prevents a duplicate ledger entry.

    On repeated endorsement failure: set chain_status="failed" for manual
    review via the retry-chain-write endpoint. There is no inbound webhook
    from Fabric — confirmation is read back by polling, deliberately.
    """
    raise NotImplementedError("Fill in against SYSTEM_DESIGN.md Flow 2 Track A")

"""
The one place this worker actually talks to Hyperledger Fabric. Isolated
into its own small class specifically so the orchestration logic in
worker.py (idempotency, retry, DB state transitions) can be tested against
a mock of THIS class, without needing a live Fabric network — see
tests/test_worker_logic.py.

HONESTY NOTE, read before trusting this file: fabric-sdk-py (the `hfc`
package) is the community-maintained SDK SYSTEM_DESIGN.md deliberately
chose for stack consistency, with its lower maturity explicitly accepted as
a risk. This module is written against that library's documented usage
pattern from training knowledge — there was no Go compiler, no Docker, and
no live Fabric network available to actually install `hfc` and exercise
this code against in the environment where it was written. Treat the
overall shape (constructor args, async invoke/query split, response
handling) as a solid starting point, and treat every exact method/parameter
name as something to verify against the actual installed package's
examples directory before trusting it in a real submission.
"""

import asyncio
from pathlib import Path
from typing import Optional


class FabricSubmissionError(Exception):
    """Raised for any failure submitting to or querying the ledger —
    worker.py catches this one exception type rather than needing to know
    hfc's own exception hierarchy."""


class FabricClient:
    def __init__(
        self,
        connection_profile_path: str,
        msp_id: str,
        org_name: str,
        user_name: str,
        channel_name: str,
        chaincode_name: str = "hashledger",
        peers: Optional[list] = None,
    ):
        if not Path(connection_profile_path).exists():
            raise FabricSubmissionError(
                f"Fabric connection profile not found at {connection_profile_path} — "
                "see fabric-network/README.md to generate one from a running test network."
            )
        self.connection_profile_path = connection_profile_path
        self.msp_id = msp_id
        self.org_name = org_name
        self.user_name = user_name
        self.channel_name = channel_name
        self.chaincode_name = chaincode_name
        # Defaulting to a single peer name is a real simplification — a
        # production consortium submits to enough peers to satisfy the
        # channel's endorsement policy, not just one.
        self.peers = peers or [f"peer0.{org_name}"]
        self._client = None
        self._user = None

    def _ensure_client(self):
        """Lazy import + init — so importing this module doesn't require
        `hfc` to be installed unless a worker actually tries to use it
        (keeps the rest of the codebase, and its tests, independent of
        this one heavy, hard-to-verify dependency)."""
        if self._client is not None:
            return
        try:
            from hfc.fabric import Client as HFCClient  # type: ignore
        except ImportError as e:
            raise FabricSubmissionError(
                "fabric-sdk-py (hfc) is not installed. `pip install fabric-sdk-py` "
                "and confirm the import path/class name still matches — this "
                "package's API has shifted across versions."
            ) from e

        self._client = HFCClient(net_profile=self.connection_profile_path)
        # VERIFY: get_user's exact signature/kwargs against the installed
        # hfc version — this is the pattern documented in fabric-sdk-py's
        # own README examples as of this writing.
        self._user = self._client.get_user(org_name=self.org_name, name=self.user_name)

    async def _submit_hash_async(self, doc_id: str, doc_hash: str, org_id: str) -> dict:
        self._ensure_client()
        try:
            response = await self._client.chaincode_invoke(
                requestor=self._user,
                channel_name=self.channel_name,
                peers=self.peers,
                args=[doc_id, doc_hash, org_id],
                cc_name=self.chaincode_name,
                fcn="RecordHash",
                wait_for_event=True,
            )
        except Exception as e:  # noqa: BLE001 — hfc's own exception types aren't stable API to depend on
            raise FabricSubmissionError(f"RecordHash failed for docID {doc_id}: {e}") from e
        return {"raw_response": response}

    async def _get_hash_async(self, doc_id: str) -> dict:
        self._ensure_client()
        try:
            response = await self._client.chaincode_query(
                requestor=self._user,
                channel_name=self.channel_name,
                peers=self.peers,
                args=[doc_id],
                cc_name=self.chaincode_name,
                fcn="GetHash",
            )
        except Exception as e:  # noqa: BLE001
            raise FabricSubmissionError(f"GetHash failed for docID {doc_id}: {e}") from e
        return response

    def submit_hash(self, doc_id: str, doc_hash: str, org_id: str) -> dict:
        """Sync wrapper — Celery tasks are plain sync functions; hfc's API
        is asyncio-based underneath."""
        return asyncio.run(self._submit_hash_async(doc_id, doc_hash, org_id))

    def get_hash(self, doc_id: str) -> dict:
        return asyncio.run(self._get_hash_async(doc_id))

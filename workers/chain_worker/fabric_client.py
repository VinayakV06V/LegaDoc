"""
The one place this worker actually talks to Hyperledger Fabric. Isolated
into its own small class specifically so the orchestration logic in
worker.py (idempotency, retry, DB state transitions) can be tested against
a mock of THIS class, without needing a live Fabric network — see
tests/test_worker_logic.py.

VERIFIED, not just written from memory: every method/parameter name below
was checked directly against hyperledger/fabric-sdk-py's actual source
(hfc/fabric/client.py) and its own tutorial — `Client(net_profile=...)`,
`get_user(org_name, name)` (sync), and `chaincode_invoke`/`chaincode_query`
(both async, both take `fcn=` as a real keyword for the chaincode function
name, `chaincode_invoke` also takes `wait_for_event=`). This still can't
install here (`pysha3`, one of hfc's transitive deps, needs a native
compiler this machine doesn't have — this is expected to work fine inside
WSL/Docker, which do have one), so no actual network call has run against
it. The call *shapes* are confirmed correct; only a live network can
confirm the calls actually succeed end-to-end.

One thing intentionally NOT hardened here: `chaincode_query`'s return
value's exact type (raw bytes vs. decoded str) wasn't confirmed from the
source in the time available — get_hash() below returns whatever hfc
hands back unmodified. Decode/parse it explicitly the first time something
actually consumes GetHash's response, don't assume either shape.
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
                "— this needs a native compiler (one of hfc's own deps, pysha3, "
                "builds a C extension), which WSL/Docker have and bare Windows "
                "usually doesn't. Run this inside the chain_worker container or "
                "WSL, not a native Windows Python."
            ) from e

        self._client = HFCClient(net_profile=self.connection_profile_path)
        # Signature confirmed against hfc/fabric/client.py: get_user(org_name, name), sync.
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

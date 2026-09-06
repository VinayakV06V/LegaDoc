# Fabric Network

The first build milestone (see SYSTEM_DESIGN.md, Build Prompt Seed): stand
this up and confirm the Chain Worker can submit and confirm one signed hash
transaction end-to-end, in isolation, before wiring anything else to it.
This is the highest-setup-risk component in the whole system — do it first,
not last, and budget real time for it.

**Read this before starting**: everything in this folder and in
`workers/chain_worker/` was written without access to Docker, a Go
compiler, or a running Fabric network — still true. What's changed since:
`fabric_client.py`'s method calls have since been checked directly against
fabric-sdk-py's actual source (not just training knowledge), so the SDK
call shapes are confirmed correct — see that file's docstring. What's
*still* unverified, because it genuinely requires a live network to check,
is everything downstream of that: does the network come up cleanly, does
the chaincode deploy, does a real signed transaction actually confirm. You
(whoever picks this up) will be the first person to find that out.

## What's here

```
fabric-network/
  chaincode/hashledger/
    hashledger.go   — the smart contract: RecordHash, GetHash, VerifyHash
    go.mod
  connection-profile.example.json  — template; copy to connection-profile.json once generated for real
  scripts/
    setup-test-network.sh  — brings up a local network and deploys the chaincode
```

## The chaincode

Deliberately narrow — not a generic asset-transfer sample. Three functions:

- **`RecordHash(docID, docHash, orgID)`** — writes a hash record once. If
  the same `docID` already has the *same* hash recorded, this succeeds as a
  no-op (that's what makes the Chain Worker's retry safe). If it already has
  a *different* hash, this fails loudly — a hash changing value after the
  fact is exactly what this whole system exists to make impossible.
- **`GetHash(docID)`** — read the stored record.
- **`VerifyHash(docID, hashToCheck)`** — the direct support for the
  strongest demo moment this architecture can produce: recompute a
  document's hash locally, ask the ledger if it matches, get a live
  yes/no. Do this on an untouched document, then again after deliberately
  editing the stored file, live, in front of whoever you're demoing to.

## Setting up a local test network

1. **Get `fabric-samples` and the Fabric binaries/images.** Don't hand-roll
   the network topology — Hyperledger's own bootstrap script does this
   correctly and is what `scripts/setup-test-network.sh` assumes exists:

   ```bash
   curl -sSL https://raw.githubusercontent.com/hyperledger/fabric/main/scripts/bootstrap.sh | bash -s
   ```

   This downloads `fabric-samples` (including its `test-network` script)
   plus the `peer`/`configtxgen`/`cryptogen` binaries and pulls the Fabric
   Docker images. Requires Docker running.

2. **Bring up the network and deploy the chaincode:**

   ```bash
   cd fabric-network/scripts
   ./setup-test-network.sh
   ```

   This script (a) starts `fabric-samples/test-network`'s standard 2-org
   network, (b) creates a channel named `legadoc-channel` (matching
   `workers/chain_worker/worker.py`'s `_get_fabric_client()`), and
   (c) packages and deploys `chaincode/hashledger`.

   **This design's Container Diagram names 5 orgs** (Police / FSL /
   Hospital-Medical / Court / External-Verifiers). `test-network` only
   stands up 2 by default. Getting from 2 orgs to 5 is real, separate work
   (each additional org needs its own MSP, CA, and peer, and the channel
   config needs updating to add them) — do NOT treat that as done because
   the 2-org network comes up cleanly. Confirm the single end-to-end
   transaction first (below), then extend to 5 orgs as its own step.

3. **Generate a connection profile** for the org the Chain Worker will
   submit as (matching `FABRIC_MSP_ID` in `.env`). `test-network` writes
   these under `fabric-samples/test-network/organizations/peerOrganizations/<org>/connection-<org>.json`
   — copy the relevant one to `fabric-network/connection-profile.json`
   (gitignored; never commit real crypto material or a profile pointing at
   a real deployment's peers).

4. **Confirm one signed transaction end-to-end** before building anything
   else on top:

   ```bash
   cd workers/chain_worker
   python -c "
   from fabric_client import FabricClient
   client = FabricClient(
       connection_profile_path='../../fabric-network/connection-profile.json',
       msp_id='Org1MSP',
       org_name='org1.example.com',
       user_name='Admin',
       channel_name='legadoc-channel',
   )
   print(client.submit_hash(doc_id='test-doc-1', doc_hash='deadbeef', org_id='org1'))
   print(client.get_hash(doc_id='test-doc-1'))
   "
   ```

   `fabric_client.py`'s method calls (`chaincode_invoke`/`chaincode_query`'s
   `fcn=`/`wait_for_event=` kwargs, `get_user(org_name, name)`) have been
   checked directly against fabric-sdk-py's own source, so if this fails
   it's more likely the network/connection-profile/identity than the SDK
   call shapes — check those first. `pysha3` (one of `hfc`'s dependencies)
   needs a native compiler to install — run this inside the chain_worker
   container or WSL, not bare Windows Python.

## Never commit here

Local dev crypto material (MSP identities, private keys) belongs in this
folder for local testing only, and is gitignored — see the repo's
`.gitignore`. A real production identity should never touch this
repository at all, local or otherwise; production keys come from the
secrets manager named in SYSTEM_DESIGN.md's "Key management" section.

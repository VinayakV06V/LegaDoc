# Fabric Network

The first build milestone (see SYSTEM_DESIGN.md, Build Prompt Seed) is:
stand up this network and confirm the Chain Worker can submit and confirm
one signed hash transaction end-to-end, in isolation, before wiring anything
else to it. This is the highest-setup-risk component in the system — do it
first, not last.

## What goes here

- `connection-profile.json` — the Fabric Gateway connection profile the
  Chain Worker reads (path set by `FABRIC_CONNECTION_PROFILE` in `.env`).
- Crypto material / MSP identities for local dev (5 peer orgs: Police, FSL,
  Hospital-Medical, Court, External-Verifiers — see SYSTEM_DESIGN.md's
  Container Diagram). **Never commit real production signing keys here** —
  local dev crypto material only, and even that shouldn't be a real identity
  reused anywhere else.
- Chaincode (the smart contract that accepts a signed hash + org identity and
  writes it to the ledger) once it exists.

## Suggested approach for local dev

Use the `fabric-samples` `test-network` script as a starting point rather
than hand-rolling the network topology — it gives you a working 2-org network
you can extend to 5 orgs, with the connection profile and crypto material
already generated in the right shape.

## Getting it running

1. Bring up a local Fabric test network (5 peer orgs, per the Container
   Diagram).
2. Generate/export its connection profile to `connection-profile.json`.
3. Confirm `chain_worker.write_hash` (see `workers/chain_worker/worker.py`)
   can sign and submit one transaction and read back a confirmation.
4. Only then wire the rest of Flow 2 (Track A) to it.

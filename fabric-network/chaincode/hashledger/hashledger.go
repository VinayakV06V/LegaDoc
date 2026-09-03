// Package main implements the chaincode SYSTEM_DESIGN.md's Chain Worker
// talks to. Deliberately narrow — this is not a generic asset-transfer
// contract, it does exactly one job: record a document's hash once,
// immutably, and let anyone verify it later. That's the entire
// tamper-evidence guarantee this system makes.
//
// UNVERIFIED: written against the documented fabric-contract-api-go API
// from training knowledge, with no Go compiler available to build or test
// it in the environment this was written in. Treat this as a strong first
// draft, not proven-correct code — `go build` it and run the chaincode
// unit-test pattern fabric-samples uses before trusting it on a real
// network.
package main

import (
	"encoding/json"
	"fmt"

	"github.com/hyperledger/fabric-contract-api-go/contractapi"
)

// HashLedgerContract implements the chaincode. One struct, three
// functions — RecordHash, GetHash, VerifyHash. Nothing else.
type HashLedgerContract struct {
	contractapi.Contract
}

// DocumentHashRecord is what actually lives on the ledger, keyed by docID
// (which is this system's Document.id — already globally unique per
// version, since every re-upload gets a brand-new UUID row rather than
// reusing one. No separate version field needed on the ledger side.)
type DocumentHashRecord struct {
	DocID       string `json:"docId"`
	DocHash     string `json:"docHash"`
	OrgID       string `json:"orgId"`
	SubmittedBy string `json:"submittedBy"` // the calling client's identity, from ctx.GetClientIdentity()
	Timestamp   string `json:"timestamp"`   // RFC3339 — from the transaction's own timestamp, not time.Now()
}

// RecordHash writes a new hash record. Called once per document by the
// Chain Worker after a successful upload.
//
// Idempotency, matching SYSTEM_DESIGN.md's retry-chain-write rule: if this
// exact docID already has a record with the SAME hash, this succeeds
// without writing anything new — that's what makes it safe for the Chain
// Worker to retry a submission it isn't sure landed. If the docID already
// has a record with a DIFFERENT hash, that's either a serious bug upstream
// or actual tampering, and this must fail loudly rather than silently
// overwrite — a hash record changing value after the fact is exactly the
// thing this whole system exists to make impossible.
func (c *HashLedgerContract) RecordHash(ctx contractapi.TransactionContextInterface, docID string, docHash string, orgID string) error {
	existing, err := c.getRecordIfExists(ctx, docID)
	if err != nil {
		return err
	}
	if existing != nil {
		if existing.DocHash == docHash {
			return nil // idempotent retry — already recorded, nothing to do
		}
		return fmt.Errorf("docID %s already has a different hash recorded — refusing to overwrite (existing=%s, submitted=%s)", docID, existing.DocHash, docHash)
	}

	// GetTxTimestamp, not time.Now() — every endorsing peer must compute
	// the identical value for the transaction to reach endorsement
	// agreement. A wall-clock call here would make that impossible.
	txTimestamp, err := ctx.GetStub().GetTxTimestamp()
	if err != nil {
		return fmt.Errorf("failed to read transaction timestamp: %w", err)
	}

	clientID, err := ctx.GetClientIdentity().GetID()
	if err != nil {
		return fmt.Errorf("failed to read calling client identity: %w", err)
	}

	record := DocumentHashRecord{
		DocID:       docID,
		DocHash:     docHash,
		OrgID:       orgID,
		SubmittedBy: clientID,
		Timestamp:   txTimestamp.AsTime().Format("2006-01-02T15:04:05Z07:00"),
	}

	recordJSON, err := json.Marshal(record)
	if err != nil {
		return fmt.Errorf("failed to marshal hash record: %w", err)
	}

	if err := ctx.GetStub().PutState(docID, recordJSON); err != nil {
		return fmt.Errorf("failed to write hash record to ledger: %w", err)
	}

	// Cheap to emit, useful if anyone ever wants to listen for confirmations
	// instead of polling — not currently consumed by anything (this design
	// deliberately polls, see SYSTEM_DESIGN.md), but costs nothing to have.
	return ctx.GetStub().SetEvent("HashRecorded", recordJSON)
}

// GetHash returns the stored record for a docID, or an error if none exists.
func (c *HashLedgerContract) GetHash(ctx contractapi.TransactionContextInterface, docID string) (*DocumentHashRecord, error) {
	record, err := c.getRecordIfExists(ctx, docID)
	if err != nil {
		return nil, err
	}
	if record == nil {
		return nil, fmt.Errorf("no hash record found for docID %s", docID)
	}
	return record, nil
}

// VerifyHash is the direct support for the single most convincing demo
// moment this architecture can show: recompute a document's hash locally
// and ask the ledger "does this match what was recorded?" A live "yes" on
// an untouched document and a live "no" after deliberately editing the
// stored file is worth more than any slide.
func (c *HashLedgerContract) VerifyHash(ctx contractapi.TransactionContextInterface, docID string, hashToCheck string) (bool, error) {
	record, err := c.getRecordIfExists(ctx, docID)
	if err != nil {
		return false, err
	}
	if record == nil {
		return false, fmt.Errorf("no hash record found for docID %s", docID)
	}
	return record.DocHash == hashToCheck, nil
}

func (c *HashLedgerContract) getRecordIfExists(ctx contractapi.TransactionContextInterface, docID string) (*DocumentHashRecord, error) {
	data, err := ctx.GetStub().GetState(docID)
	if err != nil {
		return nil, fmt.Errorf("failed to read ledger state for docID %s: %w", docID, err)
	}
	if data == nil {
		return nil, nil
	}
	var record DocumentHashRecord
	if err := json.Unmarshal(data, &record); err != nil {
		return nil, fmt.Errorf("failed to unmarshal existing record for docID %s: %w", docID, err)
	}
	return &record, nil
}

func main() {
	chaincode, err := contractapi.NewChaincode(&HashLedgerContract{})
	if err != nil {
		panic(fmt.Sprintf("failed to create hashledger chaincode: %v", err))
	}
	if err := chaincode.Start(); err != nil {
		panic(fmt.Sprintf("failed to start hashledger chaincode: %v", err))
	}
}

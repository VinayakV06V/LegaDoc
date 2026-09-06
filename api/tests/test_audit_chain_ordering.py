"""Regression test for a real bug found while reviewing PR #20: multiple
write_audit_log() calls issued back-to-back can land with an IDENTICAL
created_at (proven in practice on this stack — not a hypothetical clock-
resolution worry). Ordering/linking the chain by created_at silently
corrupted prev_hash for every write after the first tied one. The fix is
models.AuditLog.seq — a plain monotonic counter assigned inside the same
locked critical section, independent of wall-clock resolution.

This test forces the exact failure condition (identical created_at across
several writes) rather than hoping the real clock ties on its own, so it
stays a reliable regression check regardless of the machine running it.
"""

from unittest.mock import patch
from datetime import datetime, timezone

from app.audit import write_audit_log, verify_chain_intact


def test_chain_survives_identical_timestamps_across_writes(db_session, make_org, make_user):
    """Five audit-log writes that would all share one frozen timestamp must
    still chain correctly via seq, not silently corrupt via created_at ties."""
    org = make_org()
    user = make_user("io", org=org)

    frozen = datetime(2026, 1, 1, tzinfo=timezone.utc)
    with patch("app.audit.datetime") as mock_dt:
        mock_dt.now.return_value = frozen
        for i in range(5):
            write_audit_log(
                db_session,
                action=f"test_action_{i}",
                actor_user_id=user.id,
                target_type="case",
                target_id=user.id,
                metadata={"i": i},
            )

    assert verify_chain_intact(db_session) is True


def test_seq_is_strictly_increasing_and_never_ties(db_session, make_org, make_user):
    org = make_org()
    user = make_user("io", org=org)

    frozen = datetime(2026, 1, 1, tzinfo=timezone.utc)
    entries = []
    with patch("app.audit.datetime") as mock_dt:
        mock_dt.now.return_value = frozen
        for i in range(4):
            entries.append(
                write_audit_log(db_session, action=f"a{i}", actor_user_id=user.id)
            )

    seqs = [e.seq for e in entries]
    assert seqs == sorted(seqs)
    assert len(set(seqs)) == len(seqs)  # no ties, unlike created_at above
    # And the chain actually links seq N to seq N-1's row_hash, not to
    # whatever the DB happened to return first under a timestamp tie.
    for prev_e, e in zip(entries, entries[1:]):
        assert e.prev_hash == prev_e.row_hash

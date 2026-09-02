import re

from linear_ceiling import REPO_ROOT
from linear_ceiling.ledger_check import (
    REQUIRED_IDS, VERDICTS, chain_hash, check, committed_manifest_sha, parse_ledger,
)

GOOD = """# Ledger
| id | statement | decided by | verdict |
|---|---|---|---|
| H-S1 | s | E1 | unresolved |
| H-S2 | s | E0 | unresolved |
| H-S3 | s | E2 | unresolved |
| H-S4 | s | E4 | unresolved |
| H-E7a | s | E7 | unresolved |
| H-E7b | s | E7 | unresolved |
| H-E8 | s | E8 | unresolved |
| H-E9 | s | E9 | unresolved |
## Entries
### 0001 — 2026-08-26 — first
### 0002 — 2026-08-26 — second
"""


def test_parse_finds_entries_and_verdicts():
    d = parse_ledger(GOOD)
    assert d["entries"] == [1, 2]
    assert d["hypotheses"] == {
        "H-S1": "unresolved",
        "H-S2": "unresolved",
        "H-S3": "unresolved",
        "H-S4": "unresolved",
        "H-E7a": "unresolved",
        "H-E7b": "unresolved",
        "H-E8": "unresolved", "H-E9": "unresolved",
    }


def test_check_accepts_good():
    assert check(GOOD) == []


def test_check_flags_duplicate_entry_and_bad_verdict():
    bad = GOOD.replace("### 0002", "### 0001").replace("| E0 | unresolved |", "| E0 | probably |")
    problems = check(bad)
    assert any("duplicate" in p for p in problems) and any("verdict" in p for p in problems)


def test_check_requires_all_registered_ids():
    # H-S3 is one of the four ids (H-S3, H-S4, H-E7a, H-E7b) that the previously narrowed
    # REQUIRED_IDS = ("H-S1", "H-S2") would have silently let go missing — exactly the
    # regression this lint exists to catch. Removing it (rather than H-S2) proves the fix.
    problems = check(GOOD.replace("| H-S3 | s | E2 | unresolved |\n", ""))
    assert any("H-S3" in p for p in problems)


def test_required_ids_covers_all_registered_hypotheses():
    # Guards against a future narrowing (like the one this ticket corrects) going unnoticed.
    assert set(REQUIRED_IDS) == {"H-S1", "H-S2", "H-S3", "H-S4", "H-E7a", "H-E7b", "H-E8", "H-E9"}


def test_shelved_is_a_valid_verdict():
    # Entry 0007 vocabulary: shelved-not-decided must be expressible in the table.
    assert check(GOOD.replace("| H-S1 | s | E1 | unresolved |", "| H-S1 | s | E1 | SHELVED |")) == []


def _with_chain(text: str) -> str:
    """Append an entry 0003 whose prior-entries-sha256 correctly hashes the section above it."""
    entries_start = re.search(r"^## Entries\s*$", text, re.M).start()
    heading = "### 0003 — 2026-09-01 — chained\n"
    chain = chain_hash(text, len(text), entries_start)
    return text + heading + f"prior-entries-sha256: {chain}\n"


def test_chain_accepts_correct_hash():
    assert check(_with_chain(GOOD)) == []


def test_chain_detects_edit_to_prior_entry():
    # The exact hole the chain closes: a registered entry is edited after a later entry
    # recorded the hash. ledger_check without the chain would still say "ledger ok".
    chained = _with_chain(GOOD)
    tampered = chained.replace("### 0001 — 2026-08-26 — first", "### 0001 — 2026-08-26 — first (reworded)")
    problems = check(tampered)
    assert any("prior-entries-sha256" in p for p in problems)


def test_chain_ignores_header_and_table_edits():
    # Editable commentary above '## Entries' is deliberately outside the chain: a verdict
    # cell change (which happens via a numbered entry) must not break earlier hashes.
    chained = _with_chain(GOOD)
    edited = chained.replace("| H-S2 | s | E0 | unresolved |", "| H-S2 | s | E0 | HELD |")
    assert check(edited) == []


def test_repo_ledger_is_clean():
    # Durable invariants only: the lint passes, the registered entries are all present,
    # and every verdict cell holds a value from the lint's own allowed vocabulary. This
    # must keep holding as E1 and later experiments resolve more hypotheses — it does not
    # pin today's specific verdicts (e.g. H-S2 == "NOT CONFIRMED"), which would just bake
    # in a moment and break again on the next legitimate ledger entry.
    text = (REPO_ROOT / "ledger" / "ledger.md").read_text(encoding="utf-8")
    assert check(text, committed_manifest_sha()) == []
    d = parse_ledger(text)
    assert {1, 2, 3, 4, 5} <= set(d["entries"])
    assert all(v in VERDICTS for v in d["hypotheses"].values())


def test_unestimable_is_a_valid_verdict():
    """Entry 0015: the experiment ran and its estimand has no support in the corpus."""
    assert check(GOOD.replace("| H-S1 | s | E1 | unresolved |", "| H-S1 | s | E1 | UNESTIMABLE |")) == []


# --- corpus-manifest citation (entry 0024 on) ---------------------------------------------------

SHA_A, SHA_B = "a" * 64, "b" * 64


def _entry(num, body):
    return f"### {num:04d} — 2026-09-01 — t\n{body}\n"


def test_e7_entry_from_0024_must_cite_the_manifest():
    text = GOOD + _entry(24, "figures from summarize_e7: 0.20%")
    problems = check(text, SHA_A)
    assert any("0024 cites summarize_e7" in p and "e7-manifest-sha256" in p for p in problems)
    assert check(GOOD + _entry(24, f"from summarize_e7\ne7-manifest-sha256: {SHA_A}"), SHA_A) == []


def test_entries_before_0024_and_non_e7_entries_are_exempt():
    text = GOOD + _entry(23, "summarize_e9 verdict, no manifest line") + _entry(22, "summarize_e7 figures, pre-manifest")
    assert check(text, SHA_A) == []
    assert check(GOOD + _entry(25, "an E8 amendment citing summarize_e8 only"), SHA_A) == []


def test_newest_e7_entry_must_cite_the_committed_manifest():
    """A regenerated manifest without an entry that cites it is caught; an older entry citing
    an older manifest is not, by design (the newest citation is the binding one)."""
    text = (GOOD + _entry(24, f"summarize_e7\ne7-manifest-sha256: {SHA_A}")
            + _entry(26, f"summarize_e7\ne7-manifest-sha256: {SHA_B}"))
    assert check(text, SHA_B) == []
    problems = check(text, SHA_A)
    assert any("0026" in p and "not the committed config/e7-manifest.json" in p for p in problems)
    assert check(text, None) == []            # no manifest on disk: citation form is still required


def test_manifest_citation_requires_a_full_sha():
    text = GOOD + _entry(24, "summarize_e7\ne7-manifest-sha256: abc123")
    assert any("no `e7-manifest-sha256:` line" in p for p in check(text, SHA_A))

from linear_ceiling import REPO_ROOT
from linear_ceiling.ledger_check import REQUIRED_IDS, VERDICTS, check, parse_ledger

GOOD = """# Ledger
| id | statement | decided by | verdict |
|---|---|---|---|
| H-S1 | s | E1 | unresolved |
| H-S2 | s | E0 | unresolved |
| H-S3 | s | E2 | unresolved |
| H-S4 | s | E4 | unresolved |
| H-E7a | s | E7 | unresolved |
| H-E7b | s | E7 | unresolved |
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


def test_required_ids_covers_all_six_registered_hypotheses():
    # Guards against a future narrowing (like the one this ticket corrects) going unnoticed.
    assert set(REQUIRED_IDS) == {"H-S1", "H-S2", "H-S3", "H-S4", "H-E7a", "H-E7b"}


def test_repo_ledger_is_clean():
    # Durable invariants only: the lint passes, the registered entries are all present,
    # and every verdict cell holds a value from the lint's own allowed vocabulary. This
    # must keep holding as E1 and later experiments resolve more hypotheses — it does not
    # pin today's specific verdicts (e.g. H-S2 == "NOT CONFIRMED"), which would just bake
    # in a moment and break again on the next legitimate ledger entry.
    text = (REPO_ROOT / "ledger" / "ledger.md").read_text(encoding="utf-8")
    assert check(text) == []
    d = parse_ledger(text)
    assert {1, 2, 3, 4, 5} <= set(d["entries"])
    assert all(v in VERDICTS for v in d["hypotheses"].values())

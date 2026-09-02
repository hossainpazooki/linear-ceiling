import re

import pytest

from linear_ceiling import REPO_ROOT
from linear_ceiling.ledger_check import (
    REQUIRED_IDS, VERDICT_PROVENANCE, VERDICTS, chain_hash, check, check_against,
    committed_manifest_sha, ledger_at, parse_ledger,
)
from tests.conftest import commit_all

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


def _entry(num, body):
    return f"### {num:04d} — 2026-09-01 — t\n{body}\n"


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
    # Entry 0007 vocabulary: shelved-not-decided must be expressible in the table (and, since
    # cells carry provenance, set by an entry's `verdict:` line).
    text = GOOD.replace("| H-S1 | s | E1 | unresolved |", "| H-S1 | s | E1 | SHELVED |") + _entry(24, "verdict: H-S1 = SHELVED")
    assert check(text) == []


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
    assert not any("prior-entries-sha256" in p for p in check(edited))


def test_chain_hashes_crlf_and_lf_identically():
    chained = _with_chain(GOOD)
    assert check(chained.replace("\n", "\r\n")) == []


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
    text = GOOD.replace("| H-S1 | s | E1 | unresolved |", "| H-S1 | s | E1 | UNESTIMABLE |") + _entry(24, "verdict: H-S1 = UNESTIMABLE")
    assert check(text) == []


# --- verdict-cell provenance (check 4) -------------------------------------------------------

def test_a_cell_no_entry_sets_is_refused_by_name():
    """The review's second adversarial edit: flip a table cell with no entry claiming it."""
    problems = check(GOOD.replace("| H-E8 | s | E8 | unresolved |", "| H-E8 | s | E8 | HELD |"))
    assert any(p.startswith("H-E8 verdict cell is 'HELD' but no entry sets it says 'unresolved'") for p in problems)


def test_frozen_map_applies_only_when_its_setting_entry_is_present():
    # entry 0020 present, cell still unresolved: the frozen map says NOT CONFIRMED by 0020
    text = GOOD + _entry(20, "H-E8's verdict cell changes to `NOT CONFIRMED` with this entry.")
    assert any("H-E8 verdict cell is 'unresolved' but entry 0020 (frozen provenance map)" in p for p in check(text))
    fixed = text.replace("| H-E8 | s | E8 | unresolved |", "| H-E8 | s | E8 | NOT CONFIRMED |")
    assert check(fixed) == []
    # the same cell flipped to HELD with 0020 present and no later `verdict:` line
    flipped = text.replace("| H-E8 | s | E8 | unresolved |", "| H-E8 | s | E8 | HELD |")
    assert any("H-E8 verdict cell is 'HELD' but entry 0020" in p for p in check(flipped))


def test_verdict_line_overrides_the_frozen_map_and_the_newest_wins():
    base = GOOD.replace("| H-E8 | s | E8 | unresolved |", "| H-E8 | s | E8 | HELD |")
    text = base + _entry(20, "changes to `NOT CONFIRMED`") + _entry(27, "verdict: H-E8 = HELD")
    assert check(text) == []
    reopened = (text.replace("| H-E8 | s | E8 | HELD |", "| H-E8 | s | E8 | unresolved |")
                + _entry(28, "verdict: H-E8 = unresolved"))
    assert check(reopened) == []
    stale = text + _entry(28, "verdict: H-E8 = unresolved")      # line says unresolved, cell still HELD
    assert any("entry 0028's `verdict:` line says 'unresolved'" in p for p in check(stale))


def test_verdict_line_must_name_a_registered_id_and_a_known_verdict():
    problems = check(GOOD + _entry(24, "verdict: H-X9 = HELD\nverdict: H-S1 = MAYBE"))
    assert any("names H-X9" in p for p in problems) and any("'MAYBE'" in p for p in problems)


def test_frozen_map_matches_the_repo_ledger_as_of_0022():
    assert VERDICT_PROVENANCE == {
        "H-S1": ("SHELVED", 7), "H-S2": ("NOT CONFIRMED", 4), "H-S3": ("SHELVED", 7), "H-S4": ("SHELVED", 7),
        "H-E7a": ("NOT CONFIRMED", 15), "H-E7b": ("UNESTIMABLE", 15), "H-E8": ("NOT CONFIRMED", 20),
        "H-E9": ("unresolved", 19)}


# --- block diff against a base revision (check 3) ----------------------------------------------

def _commit_ledger(repo, text):
    (repo / "ledger" / "ledger.md").write_text(text, encoding="utf-8")
    commit_all(repo, "ledger")


def test_block_diff_accepts_an_append_and_header_edits(repo):
    _commit_ledger(repo, GOOD)
    base = ledger_at("HEAD", repo)
    assert check_against(GOOD + _entry(3, "appended"), base) == []
    assert check_against(GOOD.replace("# Ledger", "# Ledger (header reworded)"), base) == []
    assert check_against(GOOD.replace("| H-S2 | s | E0 | unresolved |", "| H-S2 | s | E0 | HELD |"), base) == []
    assert check_against(GOOD.replace("\n", "\r\n"), base) == []                   # a CRLF checkout
    assert check_against(GOOD + "\n\n", base) == []                                 # trailing whitespace


def test_block_diff_refuses_an_edit_to_the_trailing_entry(repo):
    """The review's first adversarial edit: the newest entry has no successor hashing it, so
    the chain is blind to it; the block diff is not."""
    text = GOOD + _entry(22, "k=1: K +0.1185 UNRESOLVED / V +0.1715 DEGRADES")
    _commit_ledger(repo, text)
    base = ledger_at("HEAD", repo)
    assert check(text) == [] and check_against(text, base) == []
    edited = text.replace("K +0.1185 UNRESOLVED / V +0.1715 DEGRADES", "K +0.01 HOLDS / V +0.02 HOLDS")
    assert check(edited) == []                                    # the chain alone still says ok
    problems = check_against(edited, base)
    assert len(problems) == 1 and problems[0].startswith("entry 0022 differs from its text at the base revision")
    assert "immutable" in problems[0]


def test_block_diff_refuses_a_removed_entry(repo):
    _commit_ledger(repo, GOOD)
    problems = check_against(GOOD.replace("### 0002 — 2026-08-26 — second\n", ""), ledger_at("HEAD", repo))
    assert problems == ["entry 0002 is present at the base revision but gone now; registered entries are never removed"]


def test_block_diff_refuses_an_unreadable_base(repo):
    _commit_ledger(repo, GOOD)
    with pytest.raises(ValueError, match="cannot read ledger/ledger.md at 'HEAD~5'"):
        ledger_at("HEAD~5", repo)


def test_repo_ledger_blocks_match_head():
    """The working tree's entry blocks equal HEAD's -- what CI runs against the push base."""
    now = (REPO_ROOT / "ledger" / "ledger.md").read_text(encoding="utf-8")
    assert check_against(now, ledger_at("HEAD")) == []


# --- corpus-manifest citation (check 5, entry 0024 on) -------------------------------------------

SHA_A, SHA_B = "a" * 64, "b" * 64


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

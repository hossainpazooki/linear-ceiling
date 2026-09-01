"""Ledger lint (invariant 2): entries numbered and unique, every registered hypothesis has
a verdict cell from the allowed vocabulary, and each entry that declares a
`prior-entries-sha256:` line hashes the entries section above it correctly. Runs in CI.

The chain (entry 0007 onward) makes silent edits to REGISTERED ENTRY TEXT fail this lint:
each new entry records the sha256 of everything from the `## Entries` heading up to (not
including) its own heading, computed over the universal-newline-decoded text encoded as
UTF-8 (so CRLF checkouts hash identically). The header prose and the hypotheses table sit
ABOVE `## Entries` and are deliberately outside the chain — they are editable commentary,
and verdict cells legitimately change (only via a new numbered entry, which remains a
convention enforced by review, not by this hash). A history rewrite that regenerates the
chain is undetectable locally, exactly as the README says of the seal."""
import hashlib
import re
import sys

from linear_ceiling import REPO_ROOT

REQUIRED_IDS = ("H-S1", "H-S2", "H-S3", "H-S4", "H-E7a", "H-E7b")
VERDICTS = ("unresolved", "HELD", "NOT CONFIRMED", "WITHDRAWN", "SUPERSEDED", "SHELVED")
_ENTRY = re.compile(r"^### (\d{4}) — \d{4}-\d{2}-\d{2} — .+$", re.M)
_ROW = re.compile(r"^\| (H-[A-Za-z0-9]+) \|.*\| ([^|]+) \|\s*$", re.M)
_ENTRIES_HEAD = re.compile(r"^## Entries\s*$", re.M)
_CHAIN = re.compile(r"^prior-entries-sha256: ([0-9a-f]{64})\s*$", re.M)


def chain_hash(text: str, upto: int, entries_start: int) -> str:
    """sha256 of the entries section from `## Entries` (inclusive) to `upto` (exclusive)."""
    return hashlib.sha256(text[entries_start:upto].encode("utf-8")).hexdigest()


def parse_ledger(text: str) -> dict:
    entries = [int(m.group(1)) for m in _ENTRY.finditer(text)]
    hyps = {m.group(1): m.group(2).strip() for m in _ROW.finditer(text)}
    return {"entries": entries, "hypotheses": hyps}


def _check_chain(text: str) -> list[str]:
    head = _ENTRIES_HEAD.search(text)
    marks = list(_ENTRY.finditer(text))
    problems = []
    for i, m in enumerate(marks):
        block_end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        c = _CHAIN.search(text, m.start(), block_end)
        if not c:
            continue  # entries before 0007 predate the chain and declare no hash
        if head is None:
            return ["a prior-entries-sha256 line exists but no '## Entries' heading was found"]
        want = chain_hash(text, m.start(), head.start())
        if c.group(1) != want:
            problems.append(
                f"entry {m.group(1)}: prior-entries-sha256 {c.group(1)[:12]}... does not match the "
                f"entries section above it ({want[:12]}...); a registered entry was edited after "
                "the chain recorded it, or the chain line itself is wrong"
            )
    return problems


def check(text: str) -> list[str]:
    d = parse_ledger(text)
    problems = []
    seen = set()
    for e in d["entries"]:
        if e in seen:
            problems.append(f"duplicate entry number {e:04d}")
        seen.add(e)
    for hid in REQUIRED_IDS:
        if hid not in d["hypotheses"]:
            problems.append(f"hypothesis {hid} is not registered in the table")
    for hid, v in d["hypotheses"].items():
        if v not in VERDICTS:
            problems.append(f"{hid} has verdict {v!r}, not one of {VERDICTS}")
    problems.extend(_check_chain(text))
    return problems


def main() -> int:
    problems = check((REPO_ROOT / "ledger" / "ledger.md").read_text(encoding="utf-8"))
    for p in problems:
        print("LEDGER:", p)
    print("ledger ok" if not problems else f"ledger: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

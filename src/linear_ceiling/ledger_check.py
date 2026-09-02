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
chain is undetectable locally, exactly as the README says of the seal.

Corpus-manifest citation (entry 0024 on): an entry numbered >= 0024 whose text cites
`summarize_e7` figures must carry a line `e7-manifest-sha256: <64 hex>`, and the newest such
entry must cite the sha256 of the committed `config/e7-manifest.json` (canonical-JSON hash,
`e7_manifest.manifest_sha256`) -- so a manifest cannot be regenerated without an entry that
says so, and no E7 figure ships without naming the exact corpus it was measured on."""
import hashlib
import re
import sys

from linear_ceiling import REPO_ROOT
from linear_ceiling.hashing import hash_json_file

REQUIRED_IDS = ("H-S1", "H-S2", "H-S3", "H-S4", "H-E7a", "H-E7b", "H-E8", "H-E9")
VERDICTS = ("unresolved", "HELD", "NOT CONFIRMED", "WITHDRAWN", "SUPERSEDED", "SHELVED",
            "UNESTIMABLE")   # 0015: the experiment ran and its estimand has no support in the corpus
_ENTRY = re.compile(r"^### (\d{4}) — \d{4}-\d{2}-\d{2} — .+$", re.M)
_ROW = re.compile(r"^\| (H-[A-Za-z0-9]+) \|.*\| ([^|]+) \|\s*$", re.M)
_ENTRIES_HEAD = re.compile(r"^## Entries\s*$", re.M)
_CHAIN = re.compile(r"^prior-entries-sha256: ([0-9a-f]{64})\s*$", re.M)
_MANIFEST_LINE = re.compile(r"^e7-manifest-sha256: ([0-9a-f]{64})\s*$", re.M)
MANIFEST_CITED_FROM = 24          # entry 0024 committed the corpus manifest; earlier entries predate it
MANIFEST_MARKER = "summarize_e7"  # an entry that cites E7 figures names the summarizer they came from


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


def _blocks(text: str) -> list[tuple[int, str]]:
    """(entry number, block text) for every `### NNNN` entry, in file order."""
    marks = list(_ENTRY.finditer(text))
    return [(int(m.group(1)), text[m.start():(marks[i + 1].start() if i + 1 < len(marks) else len(text))])
            for i, m in enumerate(marks)]


def _check_manifest_citations(text: str, manifest_sha: str | None) -> list[str]:
    problems, newest = [], None
    for num, block in _blocks(text):
        if num < MANIFEST_CITED_FROM or MANIFEST_MARKER not in block:
            continue
        c = _MANIFEST_LINE.search(block)
        if not c:
            problems.append(f"entry {num:04d} cites {MANIFEST_MARKER} figures but carries no "
                            "`e7-manifest-sha256:` line (entry 0024: every E7 figure names the corpus "
                            "manifest it was measured against)")
            continue
        if newest is None or num > newest[0]:
            newest = (num, c.group(1))
    if newest is not None and manifest_sha is not None and newest[1] != manifest_sha:
        problems.append(f"entry {newest[0]:04d}: e7-manifest-sha256 {newest[1][:12]}... is not the committed "
                        f"config/e7-manifest.json ({manifest_sha[:12]}...); a regenerated manifest needs a "
                        "new entry that cites it")
    return problems


def check(text: str, manifest_sha: str | None = None) -> list[str]:
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
    problems.extend(_check_manifest_citations(text, manifest_sha))
    return problems


def committed_manifest_sha() -> str | None:
    p = REPO_ROOT / "config" / "e7-manifest.json"
    return hash_json_file(p) if p.exists() else None


def main() -> int:
    problems = check((REPO_ROOT / "ledger" / "ledger.md").read_text(encoding="utf-8"),
                     committed_manifest_sha())
    for p in problems:
        print("LEDGER:", p)
    print("ledger ok" if not problems else f"ledger: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

"""Ledger lint (README invariant 2). Runs in CI; every check fails closed.

1. STRUCTURE: entry numbers unique; every registered hypothesis has a verdict cell from the
   allowed vocabulary.

2. CHAIN (entry 0007 on): each entry records the sha256 of everything from the `## Entries`
   heading up to (not including) its own heading, over universal-newline text as UTF-8 (so
   CRLF checkouts hash identically). A silent edit to any entry that HAS a successor fails
   here. The header prose and the hypotheses table sit above `## Entries` and are outside the
   chain by design -- editable commentary.

3. BLOCK DIFF (`--against <rev>`): every `### NNNN` block present in `ledger/ledger.md` at
   <rev> must be byte-identical now (universal newlines; trailing whitespace of a block
   ignored). This closes the hole the chain leaves: the TRAILING entry has no successor
   hashing it, so until the next entry landed it was editable with `ledger ok` (demonstrated
   on 12ba2ca: 0020's k=1 row edited to HOLDS/HOLDS passed). Appending blocks is allowed;
   header/table edits are allowed here (check 4 covers the cells). Locally <rev> defaults to
   HEAD, so a working-tree edit to a committed entry is refused before it is committed; in CI
   it is the base of the push (`github.event.before`, else HEAD~1) or of the pull request.
   What it cannot see: a squash-merge collapses a PR's commits, so an entry appended and then
   edited inside the same PR reaches the base comparison already edited and is seen as one
   append; a force-push that rewrites the base leaves <rev> unreadable -- REFUSED, never
   skipped; a history rewrite that regenerates chain, blocks and cells together is invisible
   locally, and only the public remote's history catches that.

4. VERDICT-CELL PROVENANCE: a non-`unresolved` cell must be set by a numbered entry. Existing
   entries phrase it four ways (0004 "verdict cell is set to", 0007 "moves ... from
   `unresolved` to `SHELVED`", 0015 and 0020 "verdict cell changes to"), so no regex is
   trusted: the (id -> verdict, set-by entry) map as of entry 0022 is frozen in
   VERDICT_PROVENANCE, and every entry from 0024 on that changes a cell carries a
   machine-readable line `verdict: H-XX = <VERDICT>`. Each table cell must equal the newest
   such line for its id, else the frozen value (when the entry that set it is present), else
   `unresolved`. Reopening is `verdict: H-XX = unresolved` (0007's rule, now checkable).

5. CORPUS-MANIFEST CITATION (entry 0024 on): an entry numbered >= 0024 whose text cites
   `summarize_e7` figures must carry `e7-manifest-sha256: <64 hex>`, and the newest such entry
   must cite the sha256 of the committed `config/e7-manifest.json` (canonical-JSON hash,
   `e7_manifest.manifest_sha256`) -- a manifest cannot be regenerated without an entry that
   says so, and no E7 figure ships without naming the exact corpus it was measured on.
"""
import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

from linear_ceiling import REPO_ROOT
from linear_ceiling.hashing import hash_json_file

REQUIRED_IDS = ("H-S1", "H-S2", "H-S3", "H-S4", "H-E7a", "H-E7b", "H-E8", "H-E9")
VERDICTS = ("unresolved", "HELD", "NOT CONFIRMED", "WITHDRAWN", "SUPERSEDED", "SHELVED",
            "UNESTIMABLE")   # 0015: the experiment ran and its estimand has no support in the corpus

# Frozen at entry 0022 (tree f48b536): id -> (verdict, the numbered entry that set it).
# 0004: "H-S2's verdict cell is set to `NOT CONFIRMED` by this entry"
# 0007: "moves H-S1, H-S3, and H-S4 from `unresolved` to `SHELVED`"
# 0015: "H-E7a's verdict cell changes to `NOT CONFIRMED`"; "H-E7b -- UNESTIMABLE"
# 0019: H-E9 registered, cell `unresolved` (row completed with 0019's commit set, 16b7f56)
# 0020: "H-E8's verdict cell changes to `NOT CONFIRMED` with this entry"
# From 0024 on, a cell changes only with a `verdict: H-XX = <VERDICT>` line; this map is
# never edited -- it is the provenance of the cells that predate the line convention.
VERDICT_PROVENANCE = {
    "H-S1": ("SHELVED", 7), "H-S2": ("NOT CONFIRMED", 4), "H-S3": ("SHELVED", 7), "H-S4": ("SHELVED", 7),
    "H-E7a": ("NOT CONFIRMED", 15), "H-E7b": ("UNESTIMABLE", 15),
    "H-E8": ("NOT CONFIRMED", 20), "H-E9": ("unresolved", 19),
}

_ENTRY = re.compile(r"^### (\d{4}) — \d{4}-\d{2}-\d{2} — .+$", re.M)
_ROW = re.compile(r"^\| (H-[A-Za-z0-9]+) \|.*\| ([^|]+) \|\s*$", re.M)
_ENTRIES_HEAD = re.compile(r"^## Entries\s*$", re.M)
_CHAIN = re.compile(r"^prior-entries-sha256: ([0-9a-f]{64})\s*$", re.M)
_VERDICT_LINE = re.compile(r"^verdict: (H-[A-Za-z0-9]+) = (.+?)\s*$", re.M)
_MANIFEST_LINE = re.compile(r"^e7-manifest-sha256: ([0-9a-f]{64})\s*$", re.M)
MANIFEST_CITED_FROM = 24          # entry 0024 committed the corpus manifest; earlier entries predate it
MANIFEST_MARKER = "summarize_e7"  # an entry that cites E7 figures names the summarizer they came from
LEDGER_REL = "ledger/ledger.md"


def chain_hash(text: str, upto: int, entries_start: int) -> str:
    """sha256 of the entries section from `## Entries` (inclusive) to `upto` (exclusive)."""
    return hashlib.sha256(text[entries_start:upto].encode("utf-8")).hexdigest()


def parse_ledger(text: str) -> dict:
    entries = [int(m.group(1)) for m in _ENTRY.finditer(text)]
    hyps = {m.group(1): m.group(2).strip() for m in _ROW.finditer(text)}
    return {"entries": entries, "hypotheses": hyps}


def _norm(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _blocks(text: str) -> list[tuple[int, str]]:
    """(entry number, block text) for every `### NNNN` entry, in file order."""
    marks = list(_ENTRY.finditer(text))
    return [(int(m.group(1)), text[m.start():(marks[i + 1].start() if i + 1 < len(marks) else len(text))])
            for i, m in enumerate(marks)]


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


def _check_provenance(text: str, d: dict) -> list[str]:
    problems: list[str] = []
    present = set(d["entries"])
    lines: dict[str, tuple[int, str]] = {}
    for num, block in _blocks(text):
        for m in _VERDICT_LINE.finditer(block):
            hid, v = m.group(1), m.group(2).strip()
            if hid not in d["hypotheses"]:
                problems.append(f"entry {num:04d}: `verdict:` line names {hid}, which is not in the table")
            elif v not in VERDICTS:
                problems.append(f"entry {num:04d}: `verdict:` line sets {hid} to {v!r}, not one of {VERDICTS}")
            elif hid not in lines or num > lines[hid][0]:
                lines[hid] = (num, v)
    for hid, cell in d["hypotheses"].items():
        if hid in lines:
            want, src = lines[hid][1], f"entry {lines[hid][0]:04d}'s `verdict:` line"
        elif hid in VERDICT_PROVENANCE and VERDICT_PROVENANCE[hid][1] in present:
            want, src = VERDICT_PROVENANCE[hid][0], f"entry {VERDICT_PROVENANCE[hid][1]:04d} (frozen provenance map)"
        else:
            want, src = "unresolved", "no entry sets it"
        if cell != want:
            problems.append(f"{hid} verdict cell is {cell!r} but {src} says {want!r}; a cell changes only by a "
                            f"numbered entry carrying `verdict: {hid} = <VERDICT>`")
    return problems


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
    """Checks 1, 2, 4 and 5 on the text alone (no git)."""
    text = _norm(text)
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
    problems.extend(_check_provenance(text, d))
    problems.extend(_check_manifest_citations(text, manifest_sha))
    return problems


def check_against(now_text: str, base_text: str) -> list[str]:
    """Check 3: every entry block at the base revision is byte-identical now."""
    base = {n: b.rstrip() for n, b in _blocks(_norm(base_text))}
    now = {n: b.rstrip() for n, b in _blocks(_norm(now_text))}
    problems = []
    for num in sorted(base):
        if num not in now:
            problems.append(f"entry {num:04d} is present at the base revision but gone now; registered "
                            "entries are never removed")
            continue
        if now[num] != base[num]:
            a, b = base[num].split("\n"), now[num].split("\n")
            k = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
            old = a[k] if k < len(a) else "<end of block>"
            new = b[k] if k < len(b) else "<end of block>"
            problems.append(f"entry {num:04d} differs from its text at the base revision (block line {k + 1}: "
                            f"{old[:80]!r} -> {new[:80]!r}); registered entries are immutable -- append a "
                            "new entry instead")
    return problems


def ledger_at(rev: str, repo_root: Path = REPO_ROOT) -> str:
    """`ledger/ledger.md` as committed at `rev`, or a refusal: an unreadable base is a
    force-push or a broken checkout, and the check must fail rather than skip."""
    r = subprocess.run(["git", "show", f"{rev}:{LEDGER_REL}"], cwd=repo_root, capture_output=True,
                       text=True, encoding="utf-8")
    if r.returncode != 0:
        raise ValueError(f"cannot read {LEDGER_REL} at {rev!r} ({r.stderr.strip()[:120]}); the block-diff "
                         "check refuses rather than skips")
    return r.stdout


def committed_manifest_sha() -> str | None:
    p = REPO_ROOT / "config" / "e7-manifest.json"
    return hash_json_file(p) if p.exists() else None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m linear_ceiling.ledger_check")
    ap.add_argument("--against", default="HEAD", metavar="REV",
                    help="revision whose entry blocks must be byte-identical now (default HEAD)")
    a = ap.parse_args(argv)
    now = (REPO_ROOT / "ledger" / "ledger.md").read_text(encoding="utf-8")
    problems = check(now, committed_manifest_sha())
    try:
        problems += check_against(now, ledger_at(a.against))
    except ValueError as e:
        problems.append(str(e))
    for p in problems:
        print("LEDGER:", p)
    print(f"ledger ok (blocks unchanged vs {a.against})" if not problems else f"ledger: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

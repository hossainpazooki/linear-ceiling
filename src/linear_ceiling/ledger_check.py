"""Ledger lint (invariant 2): entries numbered and unique, every registered hypothesis has
a verdict cell from the allowed vocabulary. Runs in CI."""
import re
import sys

from linear_ceiling import REPO_ROOT

REQUIRED_IDS = ("H-S1", "H-S2", "H-S3", "H-S4", "H-E7a", "H-E7b")
VERDICTS = ("unresolved", "HELD", "NOT CONFIRMED", "WITHDRAWN", "SUPERSEDED")
_ENTRY = re.compile(r"^### (\d{4}) — \d{4}-\d{2}-\d{2} — .+$", re.M)
_ROW = re.compile(r"^\| (H-[A-Za-z0-9]+) \|.*\| ([^|]+) \|\s*$", re.M)


def parse_ledger(text: str) -> dict:
    entries = [int(m.group(1)) for m in _ENTRY.finditer(text)]
    hyps = {m.group(1): m.group(2).strip() for m in _ROW.finditer(text)}
    return {"entries": entries, "hypotheses": hyps}


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
    return problems


def main() -> int:
    problems = check((REPO_ROOT / "ledger" / "ledger.md").read_text(encoding="utf-8"))
    for p in problems:
        print("LEDGER:", p)
    print("ledger ok" if not problems else f"ledger: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

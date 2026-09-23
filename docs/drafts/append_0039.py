"""Stage Path B: operator acceptance of the existing review for paper admission.

Administrative entry only: no scientific reader, experiment, or probe runs here.
Allocated after 0038 in docs/drafts/README.md. The operator confirmed the draft's
release scope (0029, 0038, and 0034 E9) without choosing to execute this path.

--preview prints a fully chained candidate without writing. --append requires an
operator identity and is reserved for the operator. Both modes refuse if the
ledger or reviewer-owned source differs from the staged version. The append
preserves the existing ledger bytes and runs ledger_check afterwards.

Shape adapted from c360950^:docs/drafts/append_0037.py: ordering guard, preview,
chain_hash, post-append checker. No experiment-specific imports or readers.
"""

import argparse
from datetime import date, datetime, timezone
import hashlib
import os
from pathlib import Path
import re
import subprocess
import sys

sys.dont_write_bytecode = True

from linear_ceiling.ledger_check import (  # noqa: E402
    _ENTRIES_HEAD, chain_hash, check, check_against, committed_manifest_sha, ledger_at,
)

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "ledger" / "ledger.md"
REVIEW = ROOT / "docs" / "reviews" / "2026-09-08-e9-independent-reverification.md"
NUM, PREV = "0039", "0038"
STAGED_HEAD = "a5053b2f1d453235c87ce07e9f30f95524a2a590"
LEDGER_SHA = "68720a6e3be84ff0f3728e074ea8b74e2493cf48142b0c1d347dde04eaa97333"
REVIEW_SHA = "1a8ac32108aa7287a5c3f04b66d0ebb90be065d75b6e31c063c76f05e0e0d31d"
MARKER = re.compile(r"^### (\d{4})\b", re.MULTILINE)


def normalized(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def text_hash(text: str) -> str:
    return hashlib.sha256(normalized(text).encode("utf-8")).hexdigest()


def validate_staged_ledger(text: str) -> None:
    entries = MARKER.findall(normalized(text))
    if not entries or entries[-1] != PREV or NUM in entries:
        raise ValueError(f"ordering: staged after {PREV}; {NUM} must be absent and {PREV} must still be last")
    if text_hash(text) != LEDGER_SHA:
        raise ValueError("ledger changed since staging; re-read the record and re-stage through the allocator")


def validate_review(text: str) -> None:
    if text_hash(text) != REVIEW_SHA:
        raise ValueError("review record changed since staging; re-read its boundary and re-stage the draft")


def entry_text(ruling_date: str, operator: str) -> str:
    if date.fromisoformat(ruling_date).isoformat() != ruling_date:
        raise ValueError("ruling date must be YYYY-MM-DD")
    if not operator.strip() or any(c in operator for c in "\r\n`"):
        raise ValueError("operator identity must be nonempty, single-line, and contain no backticks")
    return f"""### {NUM} — {ruling_date} — Operator admission ruling: existing E9 computational re-verification accepted for condition 1; release scope stated; no hypothesis cell moves

**Operator decision, taken now.** {operator.strip()} accepts the supporting review
`docs/reviews/2026-09-08-e9-independent-reverification.md` as sufficient to discharge
0032's co-author-refutation condition for this LCFM submission's admission decision.
This is an operator ruling about what evidence is accepted for publication, not a
finding that the review performed attacks it does not document. Staged against
`{STAGED_HEAD}` after entry {PREV}; normalized review-text SHA-256
`{REVIEW_SHA}`.

**What the review did.** Its cold-rescore section (lines 30–40) records two retained
handoffs, out of 0029's 25 included handoffs, re-scored from archived raw dumps,
mapper, and alignment using the frozen upstream scorer. Quoted from lines 37–40:

> The archived and regenerated
> headline fields matched exactly, as did the keys and contents of every retained
> per-token array. The review used exact equality rather than the registered
> cross-platform tolerance.

**What the review did not establish.** Its boundary (lines 61–66), quoted:

> This re-verification supports computational integrity for the sampled archived
> records. It does not resolve the registered threshold choices, the chronology
> of later sign-off, the oracle-floor-versus-achieved-method distinction, or
> generalization beyond the recorded harness, model pair, and corpus. Those are
> scientific judgment and governance questions, not failures of the comparison
> tool.

Neither an attack on the threshold-ladder sensitivity nor an attack on the
exactly-zero prefix-invariance control is documented there. Acceptance of this
computational re-verification in place of that recorded adversarial work is the
operator's decision in this entry. It does not certify a separately signed
refutation or that both scientific leads survived an attack. The probe remains
outside the evidence path: this entry records acceptance of its review document,
and no driver, scorer, summarizer, or gate is made to depend on the probe.

**Chronology and the clause superseded.** Entry 0032 fixed its numbers-freeze gate
at EOD 2026-09-08 and required withholding if the refutation was not recorded by
that gate; 0035 preserved that consequence for E9. This entry makes a post-freeze
admission decision on its own date. For the release scope below, it supersedes
0032's withholding consequence and its requirement that the accepted refutation
be recorded by that earlier freeze. It does not backdate this decision or assert
that the required attack was completed before the freeze. A board or brief did
not make this change; this numbered operator entry does.

**Figures released for the paper.** The operator's confirmed scope is:

- **0029:** the native short-cell figures, including the arm table, threshold
  ladder, seam profile, controls, and coverage.
- **0038:** the descriptive scaled-short measurement and its registered comparison
  with 0029 and 0036, including the configuration-share readings. It remains
  descriptive and changes no hypothesis row.
- **0034, E9 part only:** calibration-size sensitivity on the eight retained
  handoffs from 0029, explicitly scoped to that subset and the native receiver.
  No long-cell calibration-size effect is released or inferred.

0036 remains separately admitted under 0035's own-entry and passing-summarizer
requirements; this entry does not create a new condition for E9-long. E8's
entries and the E8 part of 0034 are outside this ruling's release scope.

**Conditions retained and scientific state unchanged.** Figures still enter only
from their passing fail-closed readers and numbered entries; coverage travels
with the numbers; same-model figures retain the cross arm beside them; the
native-short, scaled-short, and long measurements are never pooled. This entry
releases no new scientific value and claims no new recomputation. The registered
mean-removal definition governs the paper; this acceptance does not endorse the
older universal tokenwise wording. The H-E9 and H-E9L cells, all other hypothesis
cells, thresholds, bands, controls, experimental configurations, and recorded
results are unchanged. There is no verdict line.

prior-entries-sha256: PLACEHOLDER
"""


def prepare_append(original: bytes, ruling_date: str, operator: str) -> tuple[bytes, str]:
    """Build and lint in memory; never write any path."""
    text = normalized(original.decode("utf-8"))
    validate_staged_ledger(text)
    separator = b"\n" if original.endswith((b"\n", b"\r")) else b"\n\n"
    prefix = original + separator
    normalized_prefix = normalized(prefix.decode("utf-8"))
    head = _ENTRIES_HEAD.search(normalized_prefix)
    if head is None:
        raise ValueError("ledger has no Entries heading")
    digest = chain_hash(normalized_prefix, len(normalized_prefix), head.start())
    entry = entry_text(ruling_date, operator).replace("prior-entries-sha256: PLACEHOLDER", f"prior-entries-sha256: {digest}")
    candidate = prefix + entry.encode("utf-8")
    candidate_text = normalized(candidate.decode("utf-8"))
    problems = check(candidate_text) + check_against(candidate_text, text)
    if problems:
        raise ValueError("candidate ledger refused: " + "; ".join(problems))
    return candidate, entry


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true", help="print the candidate; write nothing")
    mode.add_argument("--append", action="store_true", help="operator only: take Path B and append the ruling")
    parser.add_argument("--operator", help="operator identity to record; required for --append")
    parser.add_argument("--date", default=datetime.now(timezone.utc).date().isoformat(), help="actual ruling date, YYYY-MM-DD (default UTC today)")
    args = parser.parse_args(argv)
    if args.append and not args.operator:
        parser.error("--append requires --operator; previewing or staging is not an operator decision")
    try:
        original = LEDGER.read_bytes()
        validate_staged_ledger(original.decode("utf-8"))
        validate_review(REVIEW.read_text(encoding="utf-8"))
        baseline_problems = check(original.decode("utf-8"), committed_manifest_sha())
        baseline_problems += check_against(original.decode("utf-8"), ledger_at("HEAD", ROOT))
        if baseline_problems:
            raise ValueError("existing ledger refused: " + "; ".join(baseline_problems))
        operator = args.operator or "[operator identity required before append]"
        candidate, entry = prepare_append(original, args.date, operator)
        if args.preview:
            print("PREVIEW ONLY — Path B has not been chosen; nothing appended.\n")
            print(entry, end="")
            return 0

        # Recheck the bytes immediately before writing. Existing bytes are never rewritten.
        with LEDGER.open("r+b") as target:
            if target.read() != original:
                raise ValueError("ledger changed after preview preparation; refusing to append")
            target.seek(0, os.SEEK_END)
            written = target.write(candidate[len(original):])
            target.flush()
            os.fsync(target.fileno())
        if written != len(candidate) - len(original):
            raise OSError("short ledger append; inspect the file before any further action")
        print(f"appended {NUM}; running ledger_check")
        return subprocess.run([sys.executable, "-m", "linear_ceiling.ledger_check"], cwd=ROOT).returncode
    except (ValueError, OSError, UnicodeError) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

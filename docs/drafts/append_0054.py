"""Append entry 0054 -- Condition 1 discharged by operator ruling (2026-10-04). DESCRIPTIVE: records a ruling and its
basis; no hypothesis row, no `verdict:` line, no cell moves, no figure.

Condition 1 lives on the ledger (0032, lines 1948-1951; restated at 0045, lines 3062-3064): "nothing enters a paper until
the co-author refutation is merged under `docs/reviews/` with two signatures." On 2026-10-04 the operator ruled that
issue #7 together with PR #12's two review records is treated as that confirmation. A ruling in a chat or an issue
comment is not a ledger fact; this entry makes it one, so the ledger and the paper say the same thing.

Numbering (operator instruction 2026-10-04: "numbered after llama-branch"): 0048-0053 are allocated to staged, unrun
drafts (0048/0049 the two registered runs' figures, 0050/0051 the Llama long cell, 0052/0053 the Llama E8 amendment,
staged at 4ab54ae). This entry takes 0054 and is appended NOW, so it precedes 0048-0053 in file order. `ledger_check`
chains entries in file order and does not require consecutive numbers; the drafts README is the allocator and records
this. Ordering guard: 0047 present, 0054 absent.

  --date YYYY-MM-DD   --preview
Runs `ledger_check` after appending. Delete once appended, chained to the append with `&&`.
"""
import argparse
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))
from linear_ceiling.ledger_check import _ENTRIES_HEAD, chain_hash  # noqa: E402

NUM, LAST = "0054", "0047"
RULING_ISSUE = "https://github.com/hossainpazooki/linear-ceiling/issues/7#issuecomment-5977785608"
RULING_PR = "https://github.com/hossainpazooki/linear-ceiling/pull/12#issuecomment-5977785713"
PR12_HEAD = "8100414f7510a30eb73d7a4a4592144413140e53"
REVIEWED_AT = "39b13b4dcd4e8d4a51d3a3145bd07c13556f8fb6"

ap = argparse.ArgumentParser()
ap.add_argument("--date", default=dt.date.today().isoformat())
ap.add_argument("--preview", action="store_true")
a = ap.parse_args()
assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.date)

LEDGER = REPO_ROOT / "ledger" / "ledger.md"
text = LEDGER.read_text(encoding="utf-8").replace("\r\n", "\n")
assert f"### {LAST} " in text and f"### {NUM} " not in text, f"ordering: {LAST} present, {NUM} absent"
# The clause this entry discharges must be where the entry says it is.
assert "nothing enters a paper until the co-author refutation is merged" in text, "0045's Condition 1 clause not found"
assert "with two signatures" in text
lines = text.split("\n")
assert "Condition 1 (entry 0032) binds this cell" in lines[3061], "0045's clause is no longer at line 3062; re-anchor"
assert "Condition carried forward, not a ledger fact" in lines[1947], "0032's clause is no longer at line 1948; re-anchor"

ENTRY = f"""### {NUM} — {a.date} — Condition 1 discharged by operator ruling: issue #7 and PR #12's review records stand as the co-author confirmation; the two-signature clause of 0032 / 0045 no longer gates the paper; descriptive, no cell moves

**What Condition 1 said.** Entry 0032 (lines 1948–1951) admitted E9 to the LCFM paper on a condition carried forward:
the co-author refutation of entries 0025–0029 (two leads: τ-ladder sensitivity; the exactly-zero prefix control)
recorded before the submission's numbers froze. Entry 0045 (lines 3062–3064) restated what remained after the
2026-10-01 ruling that the numbers-freeze was moot for the camera-ready: "nothing enters a paper until the co-author
refutation is merged under `docs/reviews/` with two signatures." Issue #7 (opened 2026-10-02) widened the review's
scope to the cells the camera-ready prints (0036, 0038, 0045's tail) and named the two approvers.

**The ruling (operator, 2026-10-04).** Issue #7 together with PR #12 — `docs/reviews/2026-10-01-cache-refutation-0025-0029.md`
and `docs/reviews/2026-10-01-feedback-and-claims.md` at PR head `{PR12_HEAD[:7]}` — is treated as the Condition 1 confirmation.
The two-signature clause is discharged by this ruling rather than by two approvals on the review file. Recorded the same
day on the issue ({RULING_ISSUE}) and on the PR ({RULING_PR}); this entry is the ledger's record of it.

**What the basis is, stated as the review states it.** The refutation record covers issue #7's rows R1, R3, R4
(ladder sensitivity and the token claim: the three Qwen exceedance counts reproduced) and R9, R10 (prefix-control source
inspection), against repository revision `{REVIEWED_AT[:7]}`, with its own status line "evidence checked; proposed co-author
review and signatures pending" and an empty signature table. It lists as not covered: R2 (calibration refits), R5/R6
(sample and uncertainty), R11/R12 (prefix-control checks beyond one handoff), the long and scaled-short attack pass with
the configuration share, 0045's all-cell maxima and bin means, and R13/R14 (coverage and cross-arm). The disposition
record maps the seven upstream changes to their evidence and claims no new result. Both were written by the co-author who
built PRs #8–#14; neither carries a second reviewer's approval. **The ruling accepts this partial, unsigned record as
sufficient; the entry does not claim the uncovered rows were checked.**

**What changes.** The short-cell figures of 0029 and 0038 (and 0034's E9 column) may be cited in paper text as admitted,
without the "subject to Condition 1" qualifier; 0045's "release nothing" clause for e9s is lifted to the same extent. The
uncovered rows remain open work under issue #7 and no longer gate any paper. No deadline is implied: the LCFM
camera-ready closed 2026-10-03 23:59 AoE; whether its text printed the short-cell figures under the old condition is a
fact for the response map, not for this entry.

**What this does NOT touch.** Every verdict and cell (H-E9 HELD on a floor, 0029; H-E9L, 0036; the scaled short cell,
0038; 0045's tail figures); τ, the rule, the bands; the registered reading of f* as an oracle LOWER BOUND for two reasons
(0023, lines 1278 and 1281; 0027) — PR #12's README paragraph that calls it "not a general lower bound" is not adopted by
this ruling and needs its own corrective entry if it is ever to stand; the admission procedure for co-author-run results
(`docs/2026-10-03-co-author-run-admission.md`) and entries 0046/0047, which are about evidence, not review.

**Numbering.** 0048–0053 are allocated to staged, unrun drafts (the two registered runs' figures; the Llama long cell;
the Llama E8 amendment). By operator instruction this entry is numbered after them and appended before them, so it
precedes them in file order; `ledger_check` chains by file order and the drafts README is the allocator. Next free number
after this entry: 0055.

prior-entries-sha256: PLACEHOLDER
"""

if a.preview:
    sys.stdout.reconfigure(encoding="utf-8")
    print(ENTRY)
    raise SystemExit(0)
new = text + ("" if text.endswith("\n") else "\n") + "\n" + ENTRY
head = _ENTRIES_HEAD.search(new)
digest = chain_hash(new, new.index(f"### {NUM} "), head.start())
new = new.replace("prior-entries-sha256: PLACEHOLDER", f"prior-entries-sha256: {digest}")
LEDGER.write_text(new, encoding="utf-8", newline="\n")
print(f"appended {NUM}; chain {digest[:12]}")
r = subprocess.run([sys.executable, "-m", "linear_ceiling.ledger_check"], cwd=REPO_ROOT, capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip())
raise SystemExit(r.returncode)

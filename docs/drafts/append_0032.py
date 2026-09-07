"""Append entry 0032 -- E9 admitted to the LCFM 4-pager behind the summarizer gate; descriptive; no cell moves.

Ordering guard: 0031 present, 0032 absent (staging order per docs/drafts/README.md: 0031 = the E8 amendment's
figures, staged first). Carries no number that is not already on the record (0029) and re-reads none of them:
the only figures it names are quoted from `results/e9/summary.json` to bind the admission to the summary that
must reproduce them, and the script refuses if that file is absent or names a different entry set. Runs
`ledger_check` after appending. Delete once appended."""
import json
import subprocess
import sys

from linear_ceiling import REPO_ROOT
from linear_ceiling.ledger_check import _ENTRIES_HEAD, chain_hash

LEDGER = REPO_ROOT / "ledger" / "ledger.md"
text = LEDGER.read_text(encoding="utf-8").replace("\r\n", "\n")
assert "### 0031 " in text and "### 0032 " not in text, "ordering: 0031 present, 0032 absent"
assert "verdict: H-E9 = HELD" in text, "0029's verdict line must be on the record before E9 is admitted anywhere"
summary_path = REPO_ROOT / "results" / "e9" / "summary.json"
assert summary_path.exists(), "results/e9/summary.json is the summarizer's output; nothing is admitted without it"
s = json.loads(summary_path.read_text(encoding="utf-8"))
n_included = int(s["coverage"]["included"]) if "coverage" in s and "included" in s["coverage"] else None
assert n_included == 25, f"summary.json coverage does not read 25 included (got {n_included}); 0029 was decided on 25"

ENTRY = f"""### 0032 — 2026-09-06 — E9 admitted to the LCFM 4-pager behind the summarizer gate; descriptive; the H-E9 cell does not move

**Operator decision of 2026-09-06.** The LCFM short-paper sprint proceeds (deadline 2026-09-10 AoE; numbers-freeze
gate EOD 2026-09-08 per entry 0006), and E9 joins the submission. Entry 0006's scope cap named "Lane A/B premise
numbers and the taxonomy" as the core and allowed the transfer-fidelity leg "only if they clear the same gate";
entry 0016(1) applied that allowance to E8. This entry applies it to E9 on the same terms and no wider:

- **E9 figures enter the 4-pager only from `summarize_e9`**, fail-closed, from a run that passes every check it
  carries (alignments re-derived from the raw traces; R² from recorded moments; per-token sums against the
  moments; the {n_included} included handoffs' keep subset re-scored under 0028's tolerance; τ recomputed from the
  archived mapper; controls checked). The submission cites 0029's figures as 0029 states them; nothing is
  re-read, rounded up, or restated from a report.
- **The reading is 0027's, verbatim in spirit:** H-E9 `HELD` is read on a floor — f*(τ) is an oracle lower bound
  on the recompute fraction (oracle token selection, recompute in isolation) — and the cross-model arm's
  descriptive outcome (beyond the DEGRADES edge) is named beside it in every place the same-model figure appears.
  The 4-pager may not present the same-model result without the cross-model outcome in the same table or
  sentence.
- **Coverage travels with the number.** Every appearance of the verdict names the included set ({n_included} of 68,
  the shorter half of the corpus by |S|, entry 0025's comparison) — the claim is about that set.
- **Space.** E9 is one paragraph, one table (controls, same-model and cross-model f*, bridge R²), and the
  τ ladder in an appendix; Lane A/B premise numbers and the taxonomy remain the submission's core (0006, 0016).

**Condition carried forward, not a ledger fact.** The co-author refutation of entries 0025–0029 (two leads:
the τ-ladder sensitivity; the exactly-zero prefix-invariance control) is owed at the time of writing. If it has
not been recorded by the numbers-freeze gate, the 4-pager's E9 section is cut to one sentence marked as
ongoing work and the figures are withheld from the submission; this entry does not decide that outcome and a
later entry records it either way.

**What this does NOT touch.** No `verdict:` line; the H-E9 cell stays `HELD` as 0029 decided it; τ_K, the
rule, the band, the keep subset, the kept dumps and `results/e9/` are unchanged; no experiment is registered
and nothing runs under this entry.

prior-entries-sha256: PLACEHOLDER
"""

new = text + ("" if text.endswith("\n") else "\n") + "\n" + ENTRY
head = _ENTRIES_HEAD.search(new)
digest = chain_hash(new, new.index("### 0032 "), head.start())
new = new.replace("prior-entries-sha256: PLACEHOLDER", f"prior-entries-sha256: {digest}")
LEDGER.write_text(new, encoding="utf-8", newline="\n")
print("appended 0032; chain", digest[:12])
r = subprocess.run([sys.executable, "-m", "linear_ceiling.ledger_check"], cwd=REPO_ROOT, capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip())
raise SystemExit(r.returncode)

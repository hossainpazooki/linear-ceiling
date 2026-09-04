"""Append entry 0028 -- the registered cross-platform tolerance for the keep-subset per-token re-score.

Ordering guard: runs `summarize_e9` IN-PROCESS first (it must pass under the tolerance this entry
registers) and pulls every figure from `results/e9/summary.json`; refuses if 0028 already exists or
if the run's report is absent; runs `ledger_check` after appending. Delete once appended."""
import json
import subprocess
import sys
from pathlib import Path

from linear_ceiling import REPO_ROOT
from linear_ceiling.config import load_e9_config
from linear_ceiling.ledger_check import _ENTRIES_HEAD, chain_hash
from linear_ceiling.summarize_e9 import _RESCORE_RTOL, _SUM_TOL, summarize

LEDGER = REPO_ROOT / "ledger" / "ledger.md"
text = LEDGER.read_text(encoding="utf-8").replace("\r\n", "\n")
assert "### 0027 " in text and "### 0028 " not in text, "ordering: 0027 present, 0028 absent"
cfg = load_e9_config(REPO_ROOT / "config" / "e9.toml", REPO_ROOT)
assert (cfg.results_dir / "report.json").exists(), "no run to register a tolerance against"
summarize(cfg)                                              # raises (refuses) on anything else; nothing is written on refusal
f = json.loads((cfg.results_dir / "summary.json").read_text(encoding="utf-8"))
ra = f["rescore_agreement"]
assert ra["rtol_square"] == _RESCORE_RTOL and ra["rtol_sum"] == _SUM_TOL
per = ra["per_handoff"]
arms = ("same_K", "same_V", "cross_K", "cross_V", "ref_K", "ref_V")
rows = []
for arm in arms:
    rows.append(f"| {arm} | {min(per[h][arm]['bit_identical_frac'] for h in per):.3f} – {max(per[h][arm]['bit_identical_frac'] for h in per):.3f} "
                f"| {max(per[h][arm]['max_rel_square'] for h in per):.1e} | {max(per[h][arm]['max_rel_sum'] for h in per):.1e} "
                f"| {max(per[h][arm].get('max_abs_token_delta_diff', 0.0) for h in per):.1e} | {max(per[h][arm].get('fstar_abs_diff', 0.0) for h in per):.1e} |")
table = "\n".join(rows)
n_kept = len(per)

ENTRY = f"""### 0028 — 2026-09-04 — E9 summarizer enforcement: the keep-subset re-score tolerance registered for a cross-platform re-score; no rule, τ, band, score or handoff change

**What this is, and when.** After the run (2026-09-04, entries 0026/0027 on the record before any score;
`results/e9/report.json` complete, 25 of 68 handoffs scored, {n_kept} kept dumps home and fingerprint-verified)
and BEFORE any figure or verdict is stated. 0023 registered that `summarize_e9` "re-runs the keep-subset
scorer with `--per-token` and compares the squares" and left the comparison's tolerance to the code, which
carried `rtol = 1e-05, atol = 0` -- written for a same-machine comparison of float32 squares against the
float64 sums they were summed into. The re-score at home is a different platform from the box (Linux,
torch 2.11 CPU on the box; Windows, torch 2.13 CPU / numpy 2.5 at home; the scorer has no GPU path), and
under that constant the summarizer refused on the first kept handoff:
`E9 SUMMARY REFUSED: 20241016_composio_swekit/astropy__astropy-14182_traj#68: keep-subset per-token
re-score disagrees on same_K`. This entry registers the tolerance for that check as a judgment, with the
measurement it rests on; it is enforcement of 0023, not a change to anything 0023 registers. The rule
section, τ_K = {f['tau']['K']:.4f}, τ_V = {f['tau']['V']:.4f}, the band, the four cells, the scores on disk and the
handoff set are untouched; `verdict:` lines: none.

**Registered check (replaces the unstated constant).** For every kept handoff, the home re-score's
per-token record must (i) reproduce each per-head float64 SUM of squares to `{_SUM_TOL:.0e}` relative
(unchanged: this is what the moments are), and (ii) reproduce every individual float32 square to
`{_RESCORE_RTOL:.0e}` relative with no absolute floor; a shape mismatch, a sum beyond (i) or a square beyond
(ii) refuses the summary, as before. The summarizer now also reports what the cross-platform jitter does
to the statistic itself: the largest change in any token's centered δ and in any handoff's f*(τ) between
the box record and the home re-score.

**Measured, by `summarize_e9` on this run ({n_kept} kept handoffs × 6 arrays; `rescore_agreement` in
`results/e9/summary.json`):**

| array | bit-identical fraction (min – max over handoffs) | max square rel. diff | max per-head sum rel. diff | max \\|Δδ_token\\| | max \\|Δf*(τ)\\| |
|---|---|---|---|---|---|
{table}

Overall: every per-head sum within {ra['max_rel_sum']:.1e} relative (tolerance {_SUM_TOL:.0e}); every square within
{ra['max_rel_square']:.1e} relative (tolerance {_RESCORE_RTOL:.0e}); the largest change in any token's δ is
{ra['max_abs_token_delta_diff']:.1e} and f*(τ_K) / f*(τ_V) is unchanged on every kept handoff and arm (max |Δf*| =
{ra['max_fstar_abs_diff']:.1e}). The same-model arrays and the reference norms reproduce almost or exactly
bit-for-bit; the cross-arm squares pass through the k = 1 mapper's matmul, where the two platforms' BLAS
reduce in a different order, and never differ by more than a third of a percent. The ref arrays are not
squares; they are checked under the same rule for uniformity.

**Basis beyond this run: what the disagreement is (scratch, 2026-09-04, one kept handoff, astropy-14182).**
Re-scored in an Ubuntu WSL on the home machine with the box's torch build (2.11.0 from the cu128 index,
numpy 2.5.2, python 3.12): `same_K`, `same_V`, `ref_K`, `ref_V` reproduce the box record **bit-for-bit**
(the 132 differing same-K squares at home were Windows-vs-Linux, ≤ 2.5e-04 relative on near-zero squares);
two identical runs on one machine are bit-identical on every array; the cross arrays change with the
THREAD COUNT alone (8 threads vs 1 thread on the same machine: 69% / 48% of cross-K / cross-V squares
identical, ≤ 1.2e-03 relative) and against the 104-core box at any thread count agree on ≈ 10% / 4% of
squares within 2.5e-03 / 3.8e-04 relative. So: the verdict-bearing arrays are exactly reproducible on a
matching platform; the cross arrays' per-square disagreement is reduction order inside the mapper's
float32 matmul, a function of thread count and hardware, not of the record. This is a measured
explanation, not an inference from the sizes of the differences.

**Why {_RESCORE_RTOL:.0e} and not the measured {ra['max_rel_square']:.1e}.** A tolerance set at the observed
maximum is a tautology; one order above it still refuses any square that moved by a percent, which is
{100 * _RESCORE_RTOL / ra['max_rel_square']:.0f}× the largest platform effect seen here and far below anything that could move a
token across τ_K (a token would need δ to move by a factor, not a percent, and the measured max |Δδ| is
{ra['max_abs_token_delta_diff']:.1e} against τ_K = {f['tau']['K']:.4f}). The sum check keeps the tight floor: a record whose
squares were altered in a way that preserved every per-head sum would still have to keep every square
within a percent of the box's.

**Scope.** All of 0019's, 0023's, 0025's, 0026's and 0027's limits. No hypothesis cell changes with this
entry; no `verdict:` line. The verdict on H-E9 enters only by its own numbered entry, from a summary that
passes under this check.

prior-entries-sha256: PLACEHOLDER
"""

new = text + ("" if text.endswith("\n") else "\n") + "\n" + ENTRY
head = _ENTRIES_HEAD.search(new)
digest = chain_hash(new, new.index("### 0028 "), head.start())
new = new.replace("prior-entries-sha256: PLACEHOLDER", f"prior-entries-sha256: {digest}")
LEDGER.write_text(new, encoding="utf-8", newline="\n")
print("appended 0028; chain", digest[:12])
r = subprocess.run([sys.executable, "-m", "linear_ceiling.ledger_check"], cwd=REPO_ROOT, capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip())
raise SystemExit(r.returncode)

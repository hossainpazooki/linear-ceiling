"""Entry 0018: the corrected figures of 0013/0015, through the fail-closed summarizer, after the
0017 correction is committed. Numbers pulled from the report ONLY after summarize_e7 passes in
this same process. Run order: commit 0017 -> `python -m linear_ceiling.e7` ->
`.venv/Scripts/python.exe docs/drafts/append_0018.py <date YYYY-MM-DD>`"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

from linear_ceiling import REPO_ROOT
from linear_ceiling.config import load_e7_config
from linear_ceiling.summarize_e7 import summarize

LEDGER = Path("ledger/ledger.md")
DATE = sys.argv[1]
committed = subprocess.run(["git", "show", "HEAD:ledger/ledger.md"], cwd=REPO_ROOT,
                           capture_output=True, text=True, encoding="utf-8")
if "### 0017" not in committed.stdout:
    sys.exit("entry 0017 must be COMMITTED before the corrected figures are put on the record")
cfg = load_e7_config(REPO_ROOT / "config" / "e7.toml", REPO_ROOT)
summarize(cfg)                                              # raises -> nothing is written
rep = json.loads((cfg.results_dir / "skeleton_report.json").read_text(encoding="utf-8"))
h = rep["h_e7a"]
p = h["pooled"]
hs = rep["headroom"]["summary"]
comp = next(t for t in rep["trajectories"] if t["agent"] == "composio_swekit")   # existence check
inp = sum(t["totals"]["input_tokens"] for t in rep["trajectories"] if t["agent"] == "composio_swekit")
req = sum(t["totals"]["requests"] for t in rep["trajectories"] if t["agent"] == "composio_swekit")
ntr = sum(1 for t in rep["trajectories"] if t["agent"] == "composio_swekit")


def frac(s):
    return f"{s['median']:.3f} (p10 {s['p10']:.3f}, p90 {s['p90']:.3f})"


def tok(s):
    return f"{s['median']:,.0f} (p10 {s['p10']:,.0f}, p90 {s['p90']:,.0f})"


def pct(s):
    return f"{100 * s['median']:.1f}% (p10 {100 * s['p10']:.1f}%, p90 {100 * s['p90']:.1f}%)"


ENTRY = f"""### 0018 — {DATE} — Corrected figures of 0013 and 0015's ratio `[BASELINE]`, through the fixed instrument

The figures below replace those superseded by entry 0017, recomputed by `summarize_e7` from the
raw traces with the corrected adapter and measure (config sha256 {rep['config_sha256'][:12]};
{len(rep['trace_files'])} trace files hashed; refusal on any disagreement). Registered rules unchanged;
the verdicts of 0015 stand as stated there.

**Corpus (composio family, both submissions, prompts now read in full):** {ntr} trajectories,
{req} requests, {inp:,} input tokens (visible-only LOWER BOUND, 0012).

**Headroom at the {hs['switches']} observed Lane A switches** (replacing 0013's table; read_mult
{rep['headroom']['read_mult']}; `paid` is now the receiver's own request prefill per 0017):

| figure | value |
|---|---|
| byte-identical handoffs | **{hs['byte_identical']}/{hs['switches']}** |
| overlap of the receiver's ACTUAL prompt with sender-processed content | {frac(hs['overlap_fraction'])} |
| receiver prefill at the switch, tokens (visible-only LOWER BOUND) | {tok(hs['paid_tokens'])} |
| headroom UPPER BOUND as a fraction of paid | **{pct(hs['recoverable_fraction'])}** |

The corrected overlap is HIGHER than 0013's superseded figure and nearly total: the o1-mini
prompt is the re-rendered transcript, almost entirely words the sender produced. The corrected
prefill is much smaller: the receiving stage pays for its own prompt, not the trajectory's
history. Both move the same direction for the program's thesis -- the one observed handoff
pattern re-pays a nearly fully redundant prompt, and that prompt is small.

**H-E7a ratio, restated** (rule unchanged: 0006 cutoff, Lane A alone per 0007, measurable-subset
denominator per 0014): recoverable upper bound {p['recoverable_upper_bound']:,.0f} / input spend
{p['input_spend']:,} over {p['measurable_trajs']} measurable trajectories = **{100 * p['ratio']:.2f}%** vs
{100 * h['cutoff']:.0f}%. The correction moved the ratio DOWN from the superseded 1.41%: H-E7a's
`NOT CONFIRMED` verdict (0015) stands, now by a wider margin. No other verdict is touched.

This entry decides nothing new; it puts the corrected numbers where the superseded ones stood.

prior-entries-sha256: __CHAIN__
"""
text = LEDGER.read_text(encoding="utf-8")
if "### 0018" in text:
    sys.exit("0018 present")
if "### 0017" not in text:
    sys.exit("0017 must exist first")
head = re.search(r"^## Entries\s*$", text, re.M)
if not text.endswith("\n"):
    text += "\n"
prefix = text + "\n"
chain = hashlib.sha256(prefix[head.start():].encode("utf-8")).hexdigest()
LEDGER.write_text(prefix + ENTRY.replace("__CHAIN__", chain), encoding="utf-8", newline="\n")
from linear_ceiling.ledger_check import check  # noqa: E402

pr = check(LEDGER.read_text(encoding="utf-8"))
print("0018 chain:", chain)
print("problems:", pr or "none")
sys.exit(1 if pr else 0)

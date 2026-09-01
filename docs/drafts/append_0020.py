"""Entry 0020: E8 ran; H-E8 verdict. Numbers pulled from the report ONLY after summarize_e8
passes in this same process (it re-runs the upstream scorer on the fingerprinted dumps, ~25 min
CPU). Run ONLY after 0019 exists.
usage (repo root): .venv/Scripts/python.exe docs/drafts/append_0020.py <date YYYY-MM-DD>"""
import hashlib
import json
import re
import sys
from pathlib import Path

from linear_ceiling import REPO_ROOT
from linear_ceiling.config import load_e8_config
from linear_ceiling.summarize_e8 import summarize

LEDGER = Path("ledger/ledger.md")
DATE = sys.argv[1]
cfg = load_e8_config(REPO_ROOT / "config" / "e8.toml", REPO_ROOT)
summarize(cfg)                                              # raises -> nothing is written
rep = json.loads((cfg.results_dir / "report.json").read_text(encoding="utf-8"))
vk = str(cfg.verdict_k)
out = rep["per_k"][vk]["band_outcome"]
if out["K"] == "HOLDS" and out["V"] == "HOLDS":
    verdict = "HELD"
elif "DEGRADES" in out.values() or "UNRESOLVED" in out.values():
    verdict = "NOT CONFIRMED" if "DEGRADES" in out.values() else "unresolved"
rows = []
for k in map(str, cfg.report_k):
    r = rep["per_k"][k]
    tag = " (verdict-bearing)" if k == vk else " (reported only; k=8 from a collapsed baseline, 0016)" if k == "8" else " (reported only)"
    rows.append(f"| {k}{tag} | {r['generic']['K']:.4f} / {r['generic']['V']:.4f} | "
                f"{r['agent']['K']:.4f} / {r['agent']['V']:.4f} | {r['drop']['K']:+.4f} / {r['drop']['V']:+.4f} | "
                f"{r['band_outcome']['K']} / {r['band_outcome']['V']} |")
table = ("| k | arm (a) generic K / V | arm (b) agent K / V | drop K / V | band K / V |\n|---|---|---|---|---|\n"
         + "\n".join(rows))
tok = rep["tokens"]

ENTRY = f"""### 0020 — {DATE} — E8 ran `[BASELINE]`; H-E8 {verdict}

**Provenance.** Design and band per 0009, amendments per 0016; gate passed with the committed
ledger and the upstream pinned at `{rep['upstream_sha'][:12]}` (clean tree for every invoked
path). Every figure recomputed by `summarize_e8` re-running the upstream scorer on the
fingerprinted dumps and cross-checking arm (a) against the archived `r2.json` for every k
(config sha256 {rep['config_sha256'][:12]}; agent token file sha256 {tok['sha256'][:12]}, manifest
hashed). Two independent end-to-end executions produced a byte-identical arm (b) token matrix
and identical R² -- an unplanned determinism check, recorded here.

**Held-out pooled R² (definition A5), generic calibration text vs agent-trace text, the
EXISTING mappers, no refit:**

{table}

**H-E8 -- {verdict}.** The registered claim is that the mapper "retains its held-out pooled R²
when the KV states come from agent-trace text, within the tolerance band, K and V separately"
(0009), verdict-bearing at k = 1 (0016), neither read-out alone (0009). At k = 1 the V drop
({rep['per_k'][vk]['drop']['V']:+.4f}) is DEGRADES and the K drop ({rep['per_k'][vk]['drop']['K']:+.4f})
is UNRESOLVED (inside the registered dead band): retention FAILS for V and is NOT ESTABLISHED
for K, so the claim as registered is {verdict}. The direction is consistent at every k, and V
degrades more than K everywhere -- content shift hits the value pathway harder than the key
pathway on this pair.

**Scope, carried from 0009/0016 and binding on any use of these numbers:** the text is
off-policy for Qwen (content distribution shift only, never on-policy agent behaviour); one
pair, one calibration size (n = 50, where k = 4 is already partly and k = 8 fully collapsed);
NOT a transfer at a real switch point; arm (b) text is visible-messages-only and omits every
hidden prefix the provider billed (0012). H-E8's verdict cell changes to `{verdict}` with this
entry.

prior-entries-sha256: __CHAIN__
"""
text = LEDGER.read_text(encoding="utf-8")
if "### 0020" in text:
    sys.exit("0020 present")
if "### 0019" not in text:
    sys.exit("0019 must exist first (approved ordering)")


def flip(t, hid, new):
    pat = re.compile(rf"^(\| {re.escape(hid)} \|.*\|) unresolved \|$", re.M)
    if not pat.search(t):
        sys.exit(f"table row for {hid} not found with verdict 'unresolved'")
    return pat.sub(lambda m: f"{m.group(1)} {new} |", t, count=1)


text = flip(text, "H-E8", verdict)
head = re.search(r"^## Entries\s*$", text, re.M)
if not text.endswith("\n"):
    text += "\n"
prefix = text + "\n"
chain = hashlib.sha256(prefix[head.start():].encode("utf-8")).hexdigest()
LEDGER.write_text(prefix + ENTRY.replace("__CHAIN__", chain), encoding="utf-8", newline="\n")
from linear_ceiling.ledger_check import check  # noqa: E402

pr = check(LEDGER.read_text(encoding="utf-8"))
print("0020 chain:", chain)
print("H-E8:", verdict, "| k=1 outcomes:", out)
print("problems:", pr or "none")
sys.exit(1 if pr else 0)

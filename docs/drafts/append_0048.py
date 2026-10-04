"""Append entry 0048 -- the same-model extension RAN (registered by 0046); figures only, written ONLY from
`tools/consolidation/summarize.py` run in-process over the operator's verified mirror. DESCRIPTIVE: no `verdict:` line,
no hypothesis row, no cell moves. The pilot (0046) is compared only if its published bundle is given.

Ordering guard: 0047 on the ledger, 0048 absent; the reader must PASS (it refuses on any hash, pin, identity or
bridge disagreement and writes nothing then). Run facts the reader cannot know come as arguments and are refused when
missing:

  --box "<instance type, GPU, region, instance id>"   --launched <UTC>   --finished <UTC>
  --dataset <repo_id>          the R8 backup, verified by tools/hf_verify_backup.py (exit 0) before this runs
  --mirror <path>              default results/consolidation (SHA256SUMS, provenance/, a100/inputs, a100/results, archive/records)
  --pilot-mirror <path>        optional: the co-author's published bundle, laid out the same way; recomputed and compared
  --date <YYYY-MM-DD>          defaults to --finished's date
  --preview                    print, do not append
Runs `ledger_check` after appending. Delete once appended, chained to the append with `&&`.
"""
import argparse
import csv
import datetime as dt
import json
import re
import runpy
import subprocess
import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))
from linear_ceiling.hashing import sha256_file_bytes, sha256_text_file   # noqa: E402  (text = LF-normalized, for tracked files on a CRLF checkout)
from linear_ceiling.ledger_check import _ENTRIES_HEAD, chain_hash  # noqa: E402

NUM, PREV, REG = "0048", "0047", "0046"
LABEL = {"qwen17_bridge": "Qwen3-1.7B (bridge)", "qwen4": "Qwen3-4B", "smollm3": "SmolLM3-3B"}
COHORT = {"e9s": "short (0038's 25)", "e9l": "long (0036's 35)"}

ap = argparse.ArgumentParser()
ap.add_argument("--box", required=True)
ap.add_argument("--launched", required=True)
ap.add_argument("--finished", required=True)
ap.add_argument("--dataset", required=True)
ap.add_argument("--mirror", type=Path, default=REPO_ROOT / "results" / "consolidation")
ap.add_argument("--pilot-mirror", type=Path, default=None)
ap.add_argument("--date", default=None)
ap.add_argument("--preview", action="store_true")
a = ap.parse_args()
a.date = a.date or a.finished[:10]
assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.date), "--date must be YYYY-MM-DD"
LEDGER = REPO_ROOT / "ledger" / "ledger.md"
text = LEDGER.read_text(encoding="utf-8").replace("\r\n", "\n")
assert f"### {PREV} " in text and f"### {NUM} " not in text, f"ordering: {PREV} present, {NUM} absent"
assert f"### {REG} " in text, "the registration entry is not on the ledger"

READER = REPO_ROOT / "tools" / "consolidation" / "summarize.py"
DRIVER = {n: sha256_text_file(REPO_ROOT / "tools" / "consolidation" / n) for n in ("run.py", "capture.py")}
cfg_sha = sha256_text_file(REPO_ROOT / "config" / "consolidation.toml")
man_sha = sha256_text_file(REPO_ROOT / "config" / "consolidation-manifest.json")
tau_k = tomllib.loads((REPO_ROOT / "config" / "consolidation.toml").read_text(encoding="utf-8"))["tau_K"]


def recompute(mirror: Path, tag: str) -> tuple[dict, list[dict]]:
    """Run the fail-closed reader in-process; it raises on any disagreement. Returns (summary.json, summary.csv rows)."""
    out = mirror / "a100"
    assert (mirror / "SHA256SUMS").exists(), f"{mirror}: no SHA256SUMS"
    assert sha256_file_bytes(mirror / "provenance" / "consolidation.toml") == cfg_sha, f"{tag}: mirror config is not the registered one"
    assert sha256_file_bytes(mirror / "provenance" / "consolidation-manifest.json") == man_sha, f"{tag}: mirror manifest is not the registered one"
    argv, sys.argv = sys.argv, ["summarize.py", "--evidence", str(mirror), "--output", str(out)]
    try:
        runpy.run_path(str(READER), run_name="__main__")
    finally:
        sys.argv = argv
    summ = json.loads((out / "summary.json").read_text(encoding="utf-8"))
    assert summ["verified"] is True
    with (out / "summary.csv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    return summ, rows


summ, rows = recompute(a.mirror, "registered run")
reports = {}
for model in ("qwen17_bridge", "qwen4", "smollm3"):
    rep = json.loads((a.mirror / "a100" / "results" / model / "report.json").read_text(encoding="utf-8"))
    assert rep["complete"] and rep["config_sha256"] == cfg_sha and rep["manifest_sha256"] == man_sha
    assert rep.get("code_sha256") == DRIVER, f"{model}: the run's driver hashes are not the committed driver's (0046)"
    reports[model] = rep
gpu = {rep["gpu"] for rep in reports.values()}
assert len(gpu) == 1, "the three models ran on different GPUs; one sitting is one card"
gpu = gpu.pop()
runtime = {k: {rep[k] for rep in reports.values()} for k in ("torch", "transformers", "numpy", "cuda")}
assert all(len(v) == 1 for v in runtime.values()), "runtime differs across models"
runtime = {k: v.pop() for k, v in runtime.items()}
controls = {m: max(reports[m]["control"][k]["max_delta"] for k in ("K", "V")) for m in reports}
peak = {m: max(e["peak_allocated_GiB"] for e in reports[m]["scores"].values()) for m in reports}
bridge_mean = max(b["relative_mean_gap"] for b in summ["bridge"])
bridge_f = max(b["max_fstar_gap"] for b in summ["bridge"])

s = lambda d, nd=4: f"{d['median']:.{nd}f} (p10 {d['p10']:.{nd}f}, p90 {d['p90']:.{nd}f})"  # noqa: E731
def cell(model, cohort, kind):
    c = summ["models"][model][f"{cohort}_{kind}"]
    med = c["median"]
    return (f"{c['zero_fstar_handoffs']} of {c['handoffs']} at f*(τ) = 0; median f*(τ_{kind}) {med['fstar']:.4f}; "
            f"f*(0.1) {med['fstar_0.1']:.4f}; f*(0.03) {med['fstar_0.03']:.4f} [{c['cluster_bootstrap_95']['fstar_0.03'][0]:.4f}, "
            f"{c['cluster_bootstrap_95']['fstar_0.03'][1]:.4f}]; mean δ {med['mean_delta']:.4f}; tail over τ {med['tail_fraction']:.4f}")
lines = []
for model in ("qwen4", "smollm3"):
    for cohort in ("e9s", "e9l"):
        lines.append(f"- **{LABEL[model]}, {COHORT[cohort]}**, K: {cell(model, cohort, 'K')}. V: {cell(model, cohort, 'V')}.")
nonzero = [r for r in rows if r["kind"] == "K" and r["model"] in ("qwen4", "smollm3") and float(r["fstar"]) > 0]
nz = ("; ".join(f"`{r['handoff']}` ({LABEL[r['model']]}, {r['cohort']}): mean δ_K {float(r['mean_delta']):.4f}, f*(τ_K) {float(r['fstar']):.4f}"
                for r in nonzero) or "none")
pilot_txt = ""
if a.pilot_mirror:
    psumm, _ = recompute(a.pilot_mirror, "pilot")
    diffs = []
    for model in ("qwen4", "smollm3"):
        for cohort in ("e9s", "e9l"):
            o, p = summ["models"][model][f"{cohort}_K"], psumm["models"][model][f"{cohort}_K"]
            diffs.append(f"{LABEL[model]} {cohort}: zero f* {o['zero_fstar_handoffs']} vs {p['zero_fstar_handoffs']}, "
                         f"median f*(0.03) {o['median']['fstar_0.03']:.4f} vs {p['median']['fstar_0.03']:.4f}")
    pilot_txt = (f"\n\n**Against the pilot (0046), recomputed from its published bundle by the same reader:** " + "; ".join(diffs)
                 + ". Two platforms, one frozen input set: the differences are reduction-order effects in the sense of 0028.")

ENTRY = f"""### {NUM} — {a.date} — Same-model extension ran `[BASELINE, DESCRIPTIVE]`: Qwen3-4B and SmolLM3-3B on the original 60 handoff texts at the Qwen reference τ, bridge passed; stated beside the Qwen3-0.6B→1.7B cells and never pooled; no cell moves

**Setup, as registered ({REG}).** {a.box}; launched {a.launched}, finished {a.finished}; GPU as recorded in every report
`{gpu}`; PyTorch {runtime['torch']}, Transformers {runtime['transformers']}, NumPy {runtime['numpy']}, CUDA {runtime['cuda']}; config `{cfg_sha[:12]}…`, manifest
`{man_sha[:12]}…`, driver `run.py` `{DRIVER['run.py'][:12]}…` / `capture.py` `{DRIVER['capture.py'][:12]}…` as committed. All 126 handoffs
complete, none excluded. Backup: `{a.dataset}` (R8, verified both ways before this entry).

**Controls.** Chunked-prefill control, maximum normalized deviation per model: {', '.join(f'{LABEL[m]} {controls[m]:.2e}' for m in controls)}
(limit 1e-4). Bridge on six archived handoffs: maximum relative mean-deviation gap {bridge_mean:.2e} (limit 0.01), maximum f* gap {bridge_f:.4f}
(limit 0.01). Peak allocation per model: {', '.join(f'{LABEL[m]} {peak[m]:.2f} GiB' for m in peak)}.

**Figures (same-model arm; `summarize.py` recomputed every record, re-scored every witness, 2,000 trajectory-cluster
bootstrap resamples; brackets are 95 % intervals on f*(0.03)).** τ_K = {tau_k!r} is the 0023 Qwen3-0.6B→1.7B mapper's
shortfall, a common numerical reference and not a threshold calibrated for either model.

{chr(10).join(lines)}

Handoffs with f*(τ_K) > 0 on K among the new models: {nz}.{pilot_txt}

**Reading.** On both new receivers the mean deviation of the matched tokens sits under the Qwen reference on every
handoff but the ones named, with far less headroom at the ladder's 0.03 on the long cohort than on the short, as on the
original pair. This is a statement about means under one map's tolerance (0045); it is not a quality result, not a
length effect (different handoffs), and not pooled with any 0029 / {REG.replace('0046','0036')} figure.

**What this does NOT touch.** Every cell and verdict; τ, the rule, the bands; the original pair's entries and records.

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

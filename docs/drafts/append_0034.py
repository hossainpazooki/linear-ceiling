"""Append entry 0034 -- the calibration-size sensitivity's figures, written ONLY from in-process runs of
`summarize_e8` on `config/e8c.toml` and `e9_rescore.summarize` on `config/e9c.toml` (entry 0033 registers them).

Ordering guard: 0033 present, 0034 absent; both reports exist and name entry 0033; both summaries must pass (each
re-scores, recomputes, and refuses on any disagreement). Descriptive: no `verdict:` line; no cell moves. Runs
`ledger_check` after appending. Delete once appended."""
import json
import subprocess
import sys
from pathlib import Path

from linear_ceiling import REPO_ROOT
from linear_ceiling.config import load_e8_config, load_e9_rescore_config
from linear_ceiling.e9_rescore import summarize as summarize_e9c
from linear_ceiling.ledger_check import _ENTRIES_HEAD, chain_hash
from linear_ceiling.summarize_e8 import summarize as summarize_e8

LEDGER = REPO_ROOT / "ledger" / "ledger.md"
text = LEDGER.read_text(encoding="utf-8").replace("\r\n", "\n")
assert "### 0033 " in text and "### 0034 " not in text, "ordering: 0033 present, 0034 absent"
e8c = load_e8_config(REPO_ROOT / "config" / "e8c.toml", REPO_ROOT)
e9c = load_e9_rescore_config(REPO_ROOT / "config" / "e9c.toml", REPO_ROOT)
for cfg in (e8c, e9c):
    rep = json.loads((cfg.results_dir / "report.json").read_text(encoding="utf-8"))
    assert rep.get("amendment", {}).get("entry") == "0033" and rep["upstream_sha"] == cfg.upstream_sha
summarize_e8(e8c)                                   # refuses on anything wrong; nothing is written then
f8 = json.loads((e8c.results_dir / "summary.json").read_text(encoding="utf-8"))
f9 = summarize_e9c(e9c)                             # same
per, rec = f8["per_k"], f8["recomputed"]
kv = e8c.verdict_k
m1, r1 = per[str(kv)], rec[str(kv)]
a9 = f9["aggregate"]


def s(d, nd=4):
    return f"{d['median']:.{nd}f} (p10 {d['p10']:.{nd}f}, p90 {d['p90']:.{nd}f})"


rows = ["| k | arm (a) generic K / V, n = 420 mapper | arm (b) agent ALL K / V, n = 420 mapper | 0031's arm (b) K / V, n = 50 mapper | change K / V | drop K / V | drop 95% K | drop 95% V | band K / V (descriptive) |",
        "|---|---|---|---|---|---|---|---|---|"]
for k in e8c.report_k:
    m, r = per[str(k)], rec[str(k)]
    pr, ch, b = m["prior_0016_protocol"]["agent"], m["change_from_prior"], m["bootstrap"]
    rows.append(f"| {k}{' (compared k)' if k == kv else ''} | {r['generic']['K']:.4f} / {r['generic']['V']:.4f} | **{r['agent']['K']:.4f} / {r['agent']['V']:.4f}** | "
                f"{pr['K']:.4f} / {pr['V']:.4f} | {ch['K']:+.4f} / {ch['V']:+.4f} | {r['drop']['K']:+.4f} / {r['drop']['V']:+.4f} | "
                f"[{b['K']['drop_lower_2.5']:+.4f}, {b['K']['drop_upper_97.5']:+.4f}] | [{b['V']['drop_lower_2.5']:+.4f}, {b['V']['drop_upper_97.5']:+.4f}] | "
                f"{r['band_outcome']['K']} / {r['band_outcome']['V']} |")
table8 = "\n".join(rows)
t = a9["tau"]
ck, cv = a9["cross_K"], a9["cross_V"]
ctl = a9["same_arm_control"]
ladder_rows = "\n".join(f"| {key} | {s(row['cross_K'])} | {s(row['prior_cross_K'])} |" for key, row in a9["ladder"].items())
boot = ck["bootstrap_median_fstar_tau_reg"]
tag = e8c.mapper_tag

ENTRY = f"""### 0034 — 2026-09-06 — Calibration-size sensitivity ran `[BASELINE, DESCRIPTIVE]`: the n = 420 mapper on E8's arms and E9's kept-subset cross arm; no cell moves

**Provenance.** Registered by 0033 before the fit existed; `config/e8c.toml`, `config/e9c.toml` and this ledger committed
unmodified; upstream at `{e8c.upstream_sha[:7]}`, clean for the invoked paths; the tagged mapper `mappers/{e8c.pair}/{tag}/k{kv}` named by
sha256 in both reports (safetensors `{f9['mapper']['files']['safetensors'][:12]}`); 0020's agent dumps and token file reused through 0031's
record; 0029's kept dumps and alignments by fingerprint. Every figure below is a summarizer's: `summarize_e8 --config
config/e8c.toml` (scorer re-run, per-sequence R² recomputed from the record, bootstrap, prior report re-hashed) and
`e9_rescore summarize` (files by hash, squares summed to moments, the same-arm control, f* recomputed from both records).

**E8 with the n = 420 mapper** (0030's protocol; the change is from 0031's all-sequence figures under the n = 50 mapper):

{table8}

Per-sequence agent K at k = {kv}: median {s(m1['per_sequence']['agent_K'])} over {m1['n_heldout_seqs']['agent']} sequences.

**E9 cross arm on the {a9['n_handoffs']} kept handoffs.** Same-arm control PASSED on every handoff (max relative square vs 0028's
re-score: same_K {ctl['same_K']['max_rel_square']:.2e}, same_V {ctl['same_V']['max_rel_square']:.2e}; the tensors and alignments are 0029's). Tolerances:
τ_K (0023) {t['registered_0023']['K']:.4f}; τ_K′ under the n = 420 mapper {t['tagged_mapper']['K']:.4f} (1 − its verified arm (a) K R²); τ_agent_K {t['agent_K_0025']:.4f}.

- cross K f*(τ_K): **n = 420 mapper {s(ck['fstar_tau_reg'])}** vs n = 50 mapper on the same handoffs {s(ck['prior_fstar_tau_reg'])};
  bootstrap of the median (seed {e9c.amendment['bootstrap_seed']}, {boot['reps']} reps; reported): [{boot['lower_2.5']:.4f}, {boot['upper_97.5']:.4f}]; band word at 0023's edges, descriptive: {ck['band_word_descriptive']['tau_reg']}.
- cross K f*(τ_K′), the mapper read against its own tolerance: {s(ck['fstar_tau_tag'])} ({ck['band_word_descriptive']['tau_tag']}, descriptive).
- cross K f*(τ_agent_K): {s(ck['fstar_tau_agent'])} vs n = 50 mapper {s(ck['prior_fstar_tau_agent'])}.
- cross V f*(τ_V): {s(cv['fstar_tau_reg'])} vs {s(cv['prior_fstar_tau_reg'])}.
- bridge R² (A5, head- and layer-averaged): cross K {s(a9['bridge_r2']['cross_K'])} vs {s(a9['prior_bridge_r2']['cross_K'])}; cross V {s(a9['bridge_r2']['cross_V'])} vs
  {s(a9['prior_bridge_r2']['cross_V'])}; same K (control) {s(a9['bridge_r2']['same_K'])} vs {s(a9['prior_bridge_r2']['same_K'])}.

| τ (ladder) | cross K f*, n = 420 mapper | cross K f*, n = 50 mapper |
|---|---|---|
{ladder_rows}

**What this establishes, narrowly.** Descriptive only: the decided cells (H-E8 0020, H-E9 0029) were decided under the
registered protocol with the n = 50 mapper and do not move; the n = 420 figures stand beside them as the answer to
"was it the calibration size" for this pair, this direction, {a9['n_handoffs']} kept of 25 included handoffs, on a floor (0027).
Not established: anything about the excluded long handoffs; an achievable scheme; the paper's own regime (~128K tokens).

**Scope.** All of 0033's. No `verdict:` line.

prior-entries-sha256: PLACEHOLDER
"""

new = text + ("" if text.endswith("\n") else "\n") + "\n" + ENTRY
head = _ENTRIES_HEAD.search(new)
digest = chain_hash(new, new.index("### 0034 "), head.start())
new = new.replace("prior-entries-sha256: PLACEHOLDER", f"prior-entries-sha256: {digest}")
LEDGER.write_text(new, encoding="utf-8", newline="\n")
print("appended 0034; chain", digest[:12])
r = subprocess.run([sys.executable, "-m", "linear_ceiling.ledger_check"], cwd=REPO_ROOT, capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip())
raise SystemExit(r.returncode)

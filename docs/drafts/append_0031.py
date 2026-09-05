"""Append entry 0031 -- the E8 amendment's figures, written ONLY from an in-process `summarize_e8` run on
`config/e8a.toml` (entry 0030 registers what is computed).

Ordering guard: 0030 present, 0031 absent; `results/e8a/report.json` exists and names entry 0030; the summary
must pass (it re-scores, recomputes per-sequence R^2 from the record, bootstraps, re-checks the prior report).
Descriptive: no `verdict:` line, the H-E8 cell does not move. Runs `ledger_check` after appending. Delete once
appended."""
import json
import subprocess
import sys
from pathlib import Path

from linear_ceiling import REPO_ROOT
from linear_ceiling.config import load_e8_config
from linear_ceiling.e8 import agent_holdout_frac
from linear_ceiling.ledger_check import _ENTRIES_HEAD, chain_hash
from linear_ceiling.summarize_e8 import summarize

LEDGER = REPO_ROOT / "ledger" / "ledger.md"
text = LEDGER.read_text(encoding="utf-8").replace("\r\n", "\n")
assert "### 0030 " in text and "### 0031 " not in text, "ordering: 0030 present, 0031 absent"
cfg = load_e8_config(REPO_ROOT / "config" / "e8a.toml", REPO_ROOT)
rep = json.loads((cfg.results_dir / "report.json").read_text(encoding="utf-8"))
assert rep.get("amendment", {}).get("entry") == "0030" and rep["upstream_sha"] == cfg.upstream_sha
summarize(cfg)                                              # refuses on anything wrong; nothing is written then
f = json.loads((cfg.results_dir / "summary.json").read_text(encoding="utf-8"))
per, rec = f["per_k"], f["recomputed"]


def s(d, nd=4):
    return f"{d['median']:.{nd}f} (p10 {d['p10']:.{nd}f}, p90 {d['p90']:.{nd}f})"


rows = ["| k | agent seqs / tokens | arm (a) generic K / V | arm (b) agent, ALL K / V | 0020's arm (b) K / V | change K / V | drop K / V | drop 95% K | drop 95% V | band K / V (descriptive) |",
        "|---|---|---|---|---|---|---|---|---|---|"]
for k in cfg.report_k:
    m, r = per[str(k)], rec[str(k)]
    pr, ch, b = m["prior_0016_protocol"]["agent"], m["change_from_prior"], m["bootstrap"]
    rows.append(f"| {k}{' (0016 verdict k)' if k == cfg.verdict_k else ''} | {m['n_heldout_seqs']['agent']} / {m['n_heldout_tokens']['agent']:,} | "
                f"{r['generic']['K']:.4f} / {r['generic']['V']:.4f} | **{r['agent']['K']:.4f} / {r['agent']['V']:.4f}** | {pr['K']:.4f} / {pr['V']:.4f} | "
                f"{ch['K']:+.4f} / {ch['V']:+.4f} | {r['drop']['K']:+.4f} / {r['drop']['V']:+.4f} | "
                f"[{b['K']['drop_lower_2.5']:+.4f}, {b['K']['drop_upper_97.5']:+.4f}] | [{b['V']['drop_lower_2.5']:+.4f}, {b['V']['drop_upper_97.5']:+.4f}] | "
                f"{r['band_outcome']['K']} / {r['band_outcome']['V']} |")
table = "\n".join(rows)
kv = cfg.verdict_k
m1, r1 = per[str(kv)], rec[str(kv)]
ps = m1["per_sequence"]
seq_rows = "\n".join(f"| {k} | {s(per[str(k)]['per_sequence']['agent_K'])} | {s(per[str(k)]['per_sequence']['agent_V'])} | "
                     f"{s(per[str(k)]['per_sequence']['generic_K'])} | {s(per[str(k)]['per_sequence']['generic_V'])} |" for k in cfg.report_k)
prior_band = m1["prior_0016_protocol"]["band_outcome"]
tau_agent_prior = 1 - m1["prior_0016_protocol"]["agent"]["K"]
tau_agent_all = 1 - r1["agent"]["K"]

ENTRY = f"""### 0031 — 2026-09-04 — E8 amendment ran `[BASELINE, DESCRIPTIVE]`: arm (b) over every agent sequence; the H-E8 cell does not move

**Provenance.** Registered by 0030 before any rescoring; `config/e8a.toml` and this ledger committed unmodified;
upstream at the 0030 re-pin `{cfg.upstream_sha[:7]}`, clean for the invoked paths; 0020's agent dumps and token file
reused byte for byte (fingerprints checked at run time and again by the summarizer); arm (a) cross-checked against
the archived `r2.json` for every k. Every figure below is `summarize_e8 --config config/e8a.toml`'s: the scorer
re-run on the fingerprinted dumps, per-sequence R² recomputed from the per-token record and checked against both
the report and the re-scored json, the prior report's hash re-checked. Arm (a) keeps the mapper's own held-out
fraction {cfg.holdout_frac}; arm (b) scores all {m1['n_heldout_seqs']['agent']} agent sequences ({m1['n_heldout_tokens']['agent']:,} tokens) — 0020 had scored
{m1['prior_0016_protocol']['n_heldout_seqs']} of them ({m1['prior_0016_protocol']['n_heldout_tokens']:,} tokens at the matched protocol).

{table}

Bootstrap: seeded percentile over agent sequences (seed {cfg.amendment['bootstrap_seed']} + k, {cfg.amendment['bootstrap_reps']} reps), 2.5% / 97.5% of the drop;
reported, read by nothing. Band words are 0009's band applied to the all-sequence drop for orientation only.

**Per-sequence R² (a share of the pooled decomposition, SST around the global held-out mean), median (p10, p90):**

| k | agent K | agent V | generic K | generic V |
|---|---|---|---|---|
{seq_rows}

**What changed and what did not.** Scoring every agent sequence instead of the last {m1['prior_0016_protocol']['n_heldout_seqs']} moves arm (b) at
k = {kv} by {m1['change_from_prior']['K']:+.4f} (K) / {m1['change_from_prior']['V']:+.4f} (V); the drop at k = {kv} is {r1['drop']['K']:+.4f} / {r1['drop']['V']:+.4f} with 95% bootstrap
[{m1['bootstrap']['K']['drop_lower_2.5']:+.4f}, {m1['bootstrap']['K']['drop_upper_97.5']:+.4f}] / [{m1['bootstrap']['V']['drop_lower_2.5']:+.4f}, {m1['bootstrap']['V']['drop_upper_97.5']:+.4f}], read against 0009's band as {r1['band_outcome']['K']} / {r1['band_outcome']['V']}
(0020, at the matched protocol: {prior_band['K']} / {prior_band['V']}). **The H-E8 cell was decided by 0020 under the registered 0016
protocol and does not move here; this entry carries no `verdict:` line.** τ_agent_K stays 0025's registered
value, 1 − {m1['prior_0016_protocol']['agent']['K']:.4f} = {tau_agent_prior:.4f}; the all-sequence counterpart, 1 − {r1['agent']['K']:.4f} = {tau_agent_all:.4f}, is reported here beside it
and substituted for nothing (0029 has already read τ_agent_K). Per-sequence spread on the agent arm at k = {kv}:
K {s(ps['agent_K'])}, V {s(ps['agent_V'])} over {ps['agent_K']['n']} sequences.

**Not established.** Anything beyond 0020's limits: off-policy text for Qwen, one pair, one direction, one mapper,
visible messages only (0012); the agent windows are the 0016 sample, not new text; arm (a)'s figure is on the
mapper's own {m1['n_heldout_seqs']['generic']} held-out generic sequences and its per-sequence spread is over that many.

**Scope.** All of 0009's, 0016's, 0020's and 0030's limits. No hypothesis cell changes with this entry.

prior-entries-sha256: PLACEHOLDER
"""

new = text + ("" if text.endswith("\n") else "\n") + "\n" + ENTRY
head = _ENTRIES_HEAD.search(new)
digest = chain_hash(new, new.index("### 0031 "), head.start())
new = new.replace("prior-entries-sha256: PLACEHOLDER", f"prior-entries-sha256: {digest}")
LEDGER.write_text(new, encoding="utf-8", newline="\n")
print("appended 0031; chain", digest[:12])
r = subprocess.run([sys.executable, "-m", "linear_ceiling.ledger_check"], cwd=REPO_ROOT, capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip())
raise SystemExit(r.returncode)

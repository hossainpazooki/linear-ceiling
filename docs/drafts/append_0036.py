"""Append entry 0036 -- E9-long ran; the H-E9L verdict, written ONLY from an in-process `summarize_e9 --config config/e9l.toml` run.

Ordering guard: 0035 on the ledger, 0036 absent; the e9l summary must PASS (it refuses on anything wrong and nothing is
written then); the band outcome maps to the ledger vocabulary (HOLDS -> HELD, DEGRADES -> NOT CONFIRMED, UNRESOLVED ->
unresolved). Sets the H-E9L cell by its `verdict:` line. Run facts the summarizer cannot know come as arguments and are
refused when missing:

  --box "<instance type, GPU, region>"  --launched <UTC>  --finished <UTC>
  --cutoff-reason "<why the run was closed early>"   (REQUIRED when the report is a partial close; forbidden otherwise)
  --preview                                          (print, do not append)

Per entry 0035: if the bridge reading is SCALED RECEIVER ONLY, the FIRST paragraph says so; coverage "n scored of 35
registered" travels with every number; nothing is pooled with 0029's 25. Runs `ledger_check` after appending. Delete
once appended."""
import argparse
import json
import re
import subprocess
import sys

from linear_ceiling import REPO_ROOT
from linear_ceiling.config import load_e7_config, load_e9_config
from linear_ceiling.e7_manifest import manifest_path, manifest_sha256
from linear_ceiling.ledger_check import _ENTRIES_HEAD, chain_hash
from linear_ceiling.summarize_e9 import summarize

ap = argparse.ArgumentParser()
ap.add_argument("--box", required=True)
ap.add_argument("--launched", required=True)
ap.add_argument("--finished", required=True)
ap.add_argument("--cutoff-reason", default=None)
ap.add_argument("--preview", action="store_true")
a = ap.parse_args()

LEDGER = REPO_ROOT / "ledger" / "ledger.md"
text = LEDGER.read_text(encoding="utf-8").replace("\r\n", "\n")
assert "### 0035 " in text and "### 0036 " not in text, "ordering: 0035 present, 0036 absent"
cfg = load_e9_config(REPO_ROOT / "config" / "e9l.toml", REPO_ROOT)
e7 = load_e7_config(REPO_ROOT / "config" / "e7.toml", REPO_ROOT)
manifest = manifest_sha256(manifest_path(e7))
summarize(cfg)                                              # refuses on anything wrong; nothing is written then
f = json.loads((cfg.results_dir / "summary.json").read_text(encoding="utf-8"))
rep = json.loads((cfg.results_dir / "report.json").read_text(encoding="utf-8"))
assert rep["complete"] and rep["upstream_sha"] == cfg.upstream_sha and f["rope"] == cfg.rope
VERDICT = {"HOLDS": "HELD", "DEGRADES": "NOT CONFIRMED", "UNRESOLVED": "unresolved"}[f["band_outcome"]]
partial = f.get("partial")
if partial:
    assert a.cutoff_reason, "the report is a partial close: --cutoff-reason is required (entry 0035 stopping rule)"
else:
    assert not a.cutoff_reason, "the run is complete: --cutoff-reason is not allowed"

s = lambda d, nd=4: f"{d['median']:.{nd}f} (p10 {d['p10']:.{nd}f}, p90 {d['p90']:.{nd}f})"   # noqa: E731
fs, cov, cc, tau = f["fstar"], f["coverage"], f["coverage_comparison"], f["tau"]
boot, pre, ra = f["median_fstar_same_K_bootstrap"], f["prefix_control"], f["rescore_agreement"]
ratio, br, lad = f["cross_over_same_median_delta"], f["bridge_r2"], f["fstar_ladder"]
agent, rule, bridge, prof = f["fstar_at_tau_agent"], f["rule"], f["bridge"], f["length_profiles"]
n_sc, n_reg = cov["scored"], cov["registered"]
COVER = f"{n_sc} scored of {n_reg} registered"
cross_band = ("beyond the DEGRADES edge" if fs["cross_K"]["median"] >= rule["degrades_min"] else
              "inside the HOLDS edge" if fs["cross_K"]["median"] <= rule["holds_max"] else "between the edges")
ladder_txt = "; ".join(f"τ = {float(k):g}: same K {s(lad['same_K'][k])} / V {s(lad['same_V'][k])}"
                       for k in sorted(lad["same_K"], key=lambda k: -float(k)))
seam = " · ".join(f"{r['bin']}: {r['median']:.3f} (n={r['n_tokens']})" for r in f["seam_profile_left_pooled"]["same_K"] if r["median"] is not None)
dn = f["delta_null"]
scaled_only = bridge["median_fstar_K"] > bridge["reading_max_fstar"]
bridge_rows = "; ".join(f"`{h.split('/')[-1]}` (|S| {r['n_sender']:,}) K {r['fstar_K']:.4f} / V {r['fstar_V']:.4f}, median δ_K {r['median_token_delta_K']:.3f}"
                        for h, r in bridge["per_handoff"].items())
len_rows = "; ".join(f"|S| {r['bin']}: {'n/a (no handoff)' if r['fstar_K'] is None else s(r['fstar_K'])} (n = {r['n_handoffs']})" for r in prof["s_len"])
pos_rows = "; ".join(f"positions {r['bin']}: {'n/a (no token)' if r['fstar_K_pooled'] is None else f'{r['fstar_K_pooled']:.4f}'} / "
                     f"{'n/a' if r['median_token_delta_K'] is None else f'{r['median_token_delta_K']:.3f}'} (n = {r['n_tokens']:,})" for r in prof["s_pos"])
kept_scored = len(ra["per_handoff"])
rescore_txt = (f"the {kept_scored} kept dumps fingerprint-verified and re-scored at home under 0028's tolerance (every square within "
               f"{ra['max_rel_square']:.1e} relative, max |f* diff| {ra['max_fstar_abs_diff']:.1e})" if kept_scored else
               "NO kept handoff was scored before the close, so the keep-subset re-score has nothing to read (stated, never a zero); "
               "the bridge dumps are the tensors re-scored from disk")
prior_cap = cc["n"]["excluded_prior_cap"]
partial_txt = (f"**PARTIAL CLOSE** at {partial['closed_utc']} (entry 0035 stopping rule): {COVER}, the scored set being the "
               f"prefix of the registered |S|-ascending order; unscored by id: {', '.join(f'`{h}`' for h in partial['unscored'])}. "
               f"Operator's stated reason for the cutoff: {a.cutoff_reason}. The cutoff did not depend on any score." if partial else
               f"Complete: {COVER}.")
first = ((f"**Read as a claim about the SCALED receiver only (entry 0035 control 4).** The configuration bridge — the same "
          f"receiver prefilling the same tokens under the native RoPE and under YaRN factor {cfg.rope['factor']}, scored at (p, p) — "
          f"gives median native-vs-scaled f*(τ_K) = {bridge['median_fstar_K']:.4f} over {len(bridge['per_handoff'])} short handoffs, above the "
          f"registered reading maximum {bridge['reading_max_fstar']}: the receiver configuration alone exceeds the mapper's tolerance, so "
          f"every same-model figure below is about the scaled receiver, not the trained-range model of 0029.\n\n") if scaled_only else
         (f"**Bridge reading (entry 0035 control 4): CARRIED.** Median native-vs-scaled f*(τ_K) = {bridge['median_fstar_K']:.4f} over "
          f"{len(bridge['per_handoff'])} short handoffs, within the registered maximum {bridge['reading_max_fstar']}; τ_K carries to the "
          f"scaled receiver.\n\n"))

ENTRY = f"""### 0036 — {a.finished[:10]} — E9-long ran `[BASELINE]`; H-E9L {VERDICT} ({COVER})

{first}**Setup, as registered (0035).** {a.box}; linear-ceiling at the commit carrying 0035 and `config/e9l.toml`
(gate: entries 0019/0023/0025/0027/0035), upstream pin `{cfg.upstream_sha[:7]}` (the RoPE-spec commit). Pair {cfg.pair};
receiver Qwen3-1.7B and source Qwen3-0.6B both under `{json.dumps(cfg.rope, sort_keys=True)}`
(window {cfg.context_cap:,}); the n = 50 k = 1 mapper of 0016/0020 for the cross arm. Launched {a.launched}, finished {a.finished}.
{partial_txt} Of {rep['coverage']['observed']} observed handoffs: {n_reg} registered (|S| or |R| above the prior cap {cfg.context_floor:,}, both within
{cfg.context_cap:,}), {prior_cap} decided under 0029 and excluded here, {cc['n']['excluded_long']} above the cap, {cc['n']['excluded_empty_r']} with an empty receiver prompt.
Every figure below is `summarize_e9 --config config/e9l.toml`'s, from a run that passed all of its checks: alignments
re-derived from the raw traces under the cap and floor; the run order re-derived; every R² recomputed from recorded
moments; per-token squares summed against the moments; {rescore_txt}; the bridge dumps re-scored from tensors; τ
recomputed from the archived mapper; controls checked.

**Controls (0023, 0025, 0035).** Pipeline identity: exactly zero. Prefix invariance on the first handoff in run order:
max centered per-token δ {pre['max_token_delta']:.3e} over {pre['n_positions']:,} positions (tolerance {pre['tolerance']:.0e}). δ_null same K / V token-mean
median {dn['same_K']['median_token_mean']:.3f} / {dn['same_V']['median_token_mean']:.3f}; equal-token null pairs {f['delta_null_equal_token_fraction']:.4f}. **Bridge (control 4), per handoff:** {bridge_rows};
median K {bridge['median_fstar_K']:.4f} / V {bridge['median_fstar_V']:.4f} against the reading maximum {bridge['reading_max_fstar']}. Matched fraction |M|/|R| (a floor): {s(f['matched_fraction'])}.

**The rule (0023, carried verbatim by 0035) and the figure it reads.** Per scored handoff, E9-same, K read-out:
f*(τ_K) = the fraction of matched tokens whose centered per-token deviation exceeds τ_K = {tau['K']:.4f}; median over
scored handoffs; HOLDS ≤ {rule['holds_max']}, DEGRADES ≥ {rule['degrades_min']}, UNRESOLVED between.

- **median f*(τ_K), E9-same K: {s(fs['same_K'])}** over {fs['same_K']['n']} handoffs ({COVER}). Seeded bootstrap of the
  median (seed {boot['seed']}, {boot['reps']} reps; reported, not read): [{boot['lower_2.5']:.4f}, {boot['upper_97.5']:.4f}].
- f*(τ_V = {tau['V']:.4f}), E9-same V (alongside): {s(fs['same_V'])}.
- τ ladder (descriptive): {ladder_txt}.
- f*(τ_agent_K = {f['tau_agent_K']:.4f}) (alongside): same K {s(agent['same_K'])}; cross K {s(agent['cross_K'])}.
- f*(τ_K) over matched blocks of length ≥ {f['min_block_len']}: same K {s(f['fstar_blocks_ge_min']['same_K']) if f['fstar_blocks_ge_min']['same_K'] else 'NOT COMPUTABLE'}.
- Seam profile under the causal distance b⁻(t), E9-same K, pooled median δ by bin: {seam}.
- **Length profiles (0035 control 5, descriptive).** (i) by |S| bin, median f*(τ_K) same K over handoffs: {len_rows}.
  (ii) by matched-token position in S, pooled f*(τ_K) same K / median δ_K: {pos_rows}.

**Band outcome, against the rule as written: {f['band_outcome']}** — on the scored prefix, {COVER}, never pooled with 0029's 25.
{"Not one scored handoff has a single matched token whose centered deviation exceeds τ_K on the same-model arm." if fs['same_K']['median'] == 0 and fs['same_K']['p90'] == 0 else ""}

**Read on a floor (0027, bound to this cell).** f*(τ) is an oracle LOWER BOUND on the recompute fraction (oracle
selection, recompute in isolation); this cell reads "no more than the mapper, on a floor", never that an achievable
scheme reaches it.

**Cross-arm outcome, named (descriptive, decides nothing).** E9-cross through the n = 50 k = 1 mapper: median f*(τ_K)
= {s(fs['cross_K'])} and f*(τ_V) = {s(fs['cross_V'])}; against the same edges the transfer arm sits {cross_band}.
Cross/same median-δ ratio K / V: {s(ratio['K'], 1)} / {s(ratio['V'], 1)}. Bridge R² (A5; decides nothing): same K {s(br['same_K'])},
same V {s(br['same_V'])}, cross K {s(br['cross_K'])}, cross V {s(br['cross_V'])}. The n = 420 mapper's arm on the kept subset is not
in this entry (its own config and entry, if run).

**What this establishes, stated narrowly.** On Qwen3-1.7B under YaRN factor {cfg.rope['factor']} re-rendering {n_sc} real SWE-bench
composio handoffs whose sender prompt runs {cfg.context_floor + 1:,}–{cfg.context_cap:,} tokens, with 0019's alignment and 0023's per-token rule, the
same-model oracle recompute floor is as stated above{" for the scaled receiver only" if scaled_only else ""}. **Not established:** anything
about the {n_reg - n_sc} unscored registered handoffs{"" if partial else " (none)"}, the four above {cfg.context_cap:,} or the four with an empty receiver prompt;
any achievable recompute scheme; the trained-range receiver of 0029 at these lengths{" (the bridge says the configurations differ beyond the tolerance)" if scaled_only else ""};
one pair, one direction, one mapper, one alignment method; generation quality after reuse.

verdict: H-E9L = {VERDICT}
e7-manifest-sha256: {manifest}

prior-entries-sha256: PLACEHOLDER
"""

if a.preview:
    print(ENTRY)
    raise SystemExit(0)

row = re.compile(r"^(\| H-E9L \|.*\| E9-long \(entry 0035\) \|) unresolved (\|\s*)$", re.M)
assert len(row.findall(text)) == 1, "H-E9L row not found in its expected shape"
text = row.sub(lambda m: f"{m.group(1)} {VERDICT} {m.group(2)}", text)

new = text + ("" if text.endswith("\n") else "\n") + "\n" + ENTRY
head = _ENTRIES_HEAD.search(new)
digest = chain_hash(new, new.index("### 0036 "), head.start())
new = new.replace("prior-entries-sha256: PLACEHOLDER", f"prior-entries-sha256: {digest}")
LEDGER.write_text(new, encoding="utf-8", newline="\n")
print(f"appended 0036 (H-E9L = {VERDICT}); chain", digest[:12])
r = subprocess.run([sys.executable, "-m", "linear_ceiling.ledger_check"], cwd=REPO_ROOT, capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip())
raise SystemExit(r.returncode)

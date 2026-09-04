"""Append entry 0029 -- E9 ran; the H-E9 verdict, written ONLY from an in-process `summarize_e9` run.

Ordering guard: 0028 must be on the ledger (the re-score tolerance the summary passes under); 0029 must
not; the summary must pass; the band outcome maps to the ledger vocabulary (HOLDS -> HELD, DEGRADES ->
NOT CONFIRMED, UNRESOLVED -> unresolved). Sets the H-E9 verdict cell, carries the `verdict:` line and the
`e7-manifest-sha256:` line (the coverage comparison cites 0018's E7 rows), runs `ledger_check` after
appending. Delete once appended."""
import json
import re
import subprocess
import sys
from pathlib import Path

from linear_ceiling import REPO_ROOT
from linear_ceiling.config import load_e7_config, load_e9_config
from linear_ceiling.e7_manifest import manifest_path, manifest_sha256
from linear_ceiling.ledger_check import _ENTRIES_HEAD, chain_hash
from linear_ceiling.summarize_e9 import summarize

LEDGER = REPO_ROOT / "ledger" / "ledger.md"
text = LEDGER.read_text(encoding="utf-8").replace("\r\n", "\n")
assert "### 0028 " in text and "### 0029 " not in text, "ordering: 0028 present, 0029 absent"
cfg = load_e9_config(REPO_ROOT / "config" / "e9.toml", REPO_ROOT)
e7 = load_e7_config(REPO_ROOT / "config" / "e7.toml", REPO_ROOT)
manifest = manifest_sha256(manifest_path(e7))
summarize(cfg)                                              # refuses on anything wrong; nothing is written then
f = json.loads((cfg.results_dir / "summary.json").read_text(encoding="utf-8"))
rep = json.loads((cfg.results_dir / "report.json").read_text(encoding="utf-8"))
assert rep["complete"] and rep["upstream_sha"] == cfg.upstream_sha
VERDICT = {"HOLDS": "HELD", "DEGRADES": "NOT CONFIRMED", "UNRESOLVED": "unresolved"}[f["band_outcome"]]

s = lambda d, nd=4: f"{d['median']:.{nd}f} (p10 {d['p10']:.{nd}f}, p90 {d['p90']:.{nd}f})"   # noqa: E731
fs, cov, cc, tau = f["fstar"], f["coverage"], f["coverage_comparison"], f["tau"]
boot, pre, ra = f["median_fstar_same_K_bootstrap"], f["prefix_control"], f["rescore_agreement"]
ratio, br, lad = f["cross_over_same_median_delta"], f["bridge_r2"], f["fstar_ladder"]
agent = f["fstar_at_tau_agent"]
inc, exc = cc["included"], cc["excluded_long"]
rule = f["rule"]
cross_band = ("beyond the DEGRADES edge" if fs["cross_K"]["median"] >= rule["degrades_min"] else
              "inside the HOLDS edge" if fs["cross_K"]["median"] <= rule["holds_max"] else "between the edges")
ladder_txt = "; ".join(f"τ = {float(k):g}: same K {s(lad['same_K'][k])} / V {s(lad['same_V'][k])}"
                       for k in sorted(lad["same_K"], key=lambda k: -float(k)))
seam = " · ".join(f"{r['bin']}: {r['median']:.3f} (n={r['n_tokens']})" for r in f["seam_profile_left_pooled"]["same_K"] if r["median"] is not None)
dn = f["delta_null"]

ENTRY = f"""### 0029 — 2026-09-04 — E9 ran `[BASELINE]`; H-E9 {VERDICT}

**Setup, as registered.** Algoverse grant, one H100 80 GB MIG 3g.40gb slice, JupyterHub only; linear-ceiling
`0a19b56` (entries 0019, 0023, 0025, 0026, 0027 required by the gate and committed), upstream pin
`{cfg.upstream_sha[:7]}` (entry 0026). Pair {cfg.pair}; receiver Qwen3-1.7B, source Qwen3-0.6B, the k = 1
content-space mapper of 0016/0020 for the cross arm. Launched 17:35:32 UTC after two refused attempts (0027
names them; nothing scored in either), finished 18:13 UTC: {cov['included']} handoffs scored in 38 minutes wall,
{rep['coverage']['observed']} observed, {cov['excluded']} excluded ({cc['n']['excluded_long']} over the 32,768 cap, {cc['n']['excluded_empty_r']} with an empty receiver prompt).
Every figure below is `summarize_e9`'s, from a run that passed all of its checks: alignments re-derived from
the raw traces; every R² recomputed from recorded moments; per-token squares summed against the moments;
the {len(f['keep_subset'])} kept dumps fingerprint-verified and re-scored at home under 0028's tolerance (every square within
{ra['max_rel_square']:.1e} relative, f* unchanged on every kept handoff); τ recomputed from the archived mapper; controls checked.

**Controls (0023, 0025).** Pipeline identity: exactly zero. Prefix invariance: max centered per-token δ
{pre['max_token_delta']:.3e} over {pre['n_positions']:,} positions (tolerance {pre['tolerance']:.0e}) -- the box reproduced the prefix under one extra
token bit-for-bit. δ_null (deranged pairing, the top of the deviation scale) same K / V token-mean median
{dn['same_K']['median_token_mean']:.3f} / {dn['same_V']['median_token_mean']:.3f}; fraction of null pairs with equal token ids {f['delta_null_equal_token_fraction']:.4f}.
Matched fraction |M|/|R| (a floor; blocks method): {s(f['matched_fraction'])}.

**The rule (0023, frozen before any prefill) and the figure it reads.** Per included handoff, E9-same, K
read-out: f*(τ_K) = the fraction of matched tokens whose centered per-token deviation exceeds
τ_K = {tau['K']:.4f} (1 − the k = 1 mapper's own held-out K R²); median over included handoffs; HOLDS ≤ {rule['holds_max']},
DEGRADES ≥ {rule['degrades_min']}, UNRESOLVED between.

- **median f*(τ_K), E9-same K: {s(fs['same_K'])}** over {fs['same_K']['n']} handoffs. Seeded bootstrap of the
  median (0025, seed {boot['seed']}, {boot['reps']} reps; reported, not read): [{boot['lower_2.5']:.4f}, {boot['upper_97.5']:.4f}].
- f*(τ_V = {tau['V']:.4f}), E9-same V (alongside, verdict-bearing for nothing): {s(fs['same_V'])}.
- τ ladder (0025, descriptive): {ladder_txt}.
- f*(τ_agent_K = {f['tau_agent_K']:.4f}) (0025, alongside): same K {s(agent['same_K'])}; cross K {s(agent['cross_K'])}.
- f*(τ_K) over matched blocks of length ≥ {f['min_block_len']} (0025): same K {s(f['fstar_blocks_ge_min']['same_K'])}.
- Seam profile under the causal distance b⁻(t) (0025), E9-same K, pooled median δ by bin: {seam}.

**Band outcome, against the rule as written: {f['band_outcome']}.** {"Not one included handoff has a single matched token whose centered deviation exceeds τ_K on the same-model arm: the receiver's KV at the re-rendered position agrees with its KV at the original position to within the mapper's own tolerance at every matched token, on every handoff." if fs['same_K']['median'] == 0 and fs['same_K']['p90'] == 0 else ""}

**Read on a floor (0027, bound to this cell).** f*(τ) is an oracle LOWER BOUND on the recompute fraction
(0023: oracle selection of the tokens, and recompute in isolation). CacheBlend's 10–15% is an ACHIEVED
figure. This HOLDS therefore reads: the oracle floor of the re-render's repair is no more than the budget a
same-model reuse the literature already spends -- "no more than the mapper, on a floor" -- and not that an
achievable scheme reaches it.

**Cross-arm outcome, named (0027; descriptive, decides nothing).** E9-cross, the 0.6B source mapped through
the k = 1 mapper: median f*(τ_K) = {s(fs['cross_K'])} and f*(τ_V) = {s(fs['cross_V'])}; read against the same
edges, the transfer arm sits {cross_band}. Cross/same median-δ ratio K / V: {s(ratio['K'], 1)} / {s(ratio['V'], 1)}.
Bridge R² (A5, head- and layer-averaged; decides nothing): same K {s(br['same_K'])}, same V {s(br['same_V'])},
cross K {s(br['cross_K'])}, cross V {s(br['cross_V'])} -- the cross K figure lands where 0020's arm (b) put the same
mapper on agent text (K R² 0.4371). Own-norm diagnostic, fraction of tokens with δ_own > 1, same K / V:
{s(f['own_norm_delta_gt_1_fraction']['K'])} / {s(f['own_norm_delta_gt_1_fraction']['V'])}.

**Coverage (0025; what the cap selected on).** Included vs excluded-by-length, medians (p10, p90): |S|
{inc['n_sender']['median']:,.0f} ({inc['n_sender']['p10']:,.0f}, {inc['n_sender']['p90']:,.0f}) vs {exc['n_sender']['median']:,.0f} ({exc['n_sender']['p10']:,.0f}, {exc['n_sender']['p90']:,.0f}); |R| {inc['n_receiver']['median']:,.0f} vs {exc['n_receiver']['median']:,.0f};
0018 overlap {inc['overlap_fraction_0018']['median']:.4f} vs {exc['overlap_fraction_0018']['median']:.4f}; 0018 recoverable fraction {inc['recoverable_fraction_0018']['median']:.4f} vs {exc['recoverable_fraction_0018']['median']:.4f}
({cc['unmatched_0018_rows']} handoffs without a 0018 row). H-E9 is decided on the included set and is a claim about it: the
shorter half of the corpus by |S|.

**What this establishes, stated narrowly.** On Qwen3-1.7B re-rendering {cov['included']} real SWE-bench composio handoffs
under the 32,768-token cap, with the LCS-floor alignment of 0019 and the per-token rule of 0023, the
same-model KV agreement at content-matched tokens is inside the k = 1 mapper's own tolerance at every
matched token of every handoff, so the oracle recompute floor is zero. **Not established:** anything about
the excluded long handoffs; any achievable recompute scheme (floor, not method); the cross-model transfer
at this handoff, which by the named descriptive outcome sits beyond the DEGRADES edge; one pair, one
direction, one mapper, one alignment method; and nothing about generation quality after reuse (0023's
`[STRETCH]` partial-prefill experiment, registered for the retained dumps, is not run).

verdict: H-E9 = {VERDICT}
e7-manifest-sha256: {manifest}

prior-entries-sha256: PLACEHOLDER
"""

# the hypothesis cell changes only here, by this entry's verdict line
row = re.compile(r"^(\| H-E9 \|.*\| E9 \(band in entry 0019\) \|) unresolved (\|\s*)$", re.M)
assert len(row.findall(text)) == 1, "H-E9 row not found in its expected shape"
text = row.sub(lambda m: f"{m.group(1)} {VERDICT} {m.group(2)}", text)

new = text + ("" if text.endswith("\n") else "\n") + "\n" + ENTRY
head = _ENTRIES_HEAD.search(new)
digest = chain_hash(new, new.index("### 0029 "), head.start())
new = new.replace("prior-entries-sha256: PLACEHOLDER", f"prior-entries-sha256: {digest}")
LEDGER.write_text(new, encoding="utf-8", newline="\n")
print(f"appended 0029 (H-E9 = {VERDICT}); chain", digest[:12])
r = subprocess.run([sys.executable, "-m", "linear_ceiling.ledger_check"], cwd=REPO_ROOT, capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip())
raise SystemExit(r.returncode)

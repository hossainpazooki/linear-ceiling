"""Append entry 0046 -- the E9 long half of the second model family RAN; figures only, written ONLY from an
in-process `summarize_e9 --config config/e9fl.toml` run. DESCRIPTIVE: no `verdict:` line, no hypothesis row
exists for this cell, no cell moves. Entry 0036's scaled-receiver figures are stated BESIDE these and are
never pooled with them.

Ordering guard: 0045 on the ledger, 0046 absent; the summary must PASS (it refuses on anything wrong and
nothing is written then). Run facts the summarizer cannot know come as arguments and are refused when
missing:

  --box "<instance type, GPU, region, instance id>"   --launched <UTC>   --finished <UTC>
  --cutoff-reason "<why the run was closed early>"   (REQUIRED on a partial close; forbidden otherwise)
  --date <YYYY-MM-DD>   (defaults to --finished's date)
  --preview             (print, do not append)

Per entry 0045: coverage "n scored of N registered" travels with every number; the band word is computed
and stated but is verdict-bearing for nothing; the two RoPE controls stand in for entry 0035's
configuration bridge and are reported first, because on a natively long receiver they are the whole of the
evidence that nothing was scaled. Runs `ledger_check` after appending. Delete once appended, chained to the
append with `&&`."""
import argparse
import json
import re
import subprocess
import sys

from linear_ceiling import REPO_ROOT
from linear_ceiling.config import load_e7_config, load_e9_config
from linear_ceiling.e7_manifest import manifest_path, manifest_sha256
from linear_ceiling.ledger_check import _ENTRIES_HEAD, chain_hash
from linear_ceiling.pairs import pair_models
from linear_ceiling.summarize_e9 import summarize

NUM, PREV = "0046", "0045"
FAMILY = "0039"      # the family registration entry, APPENDED 2026-09-18 -- a fixed number now
ap = argparse.ArgumentParser()
ap.add_argument("--box", required=True)
ap.add_argument("--launched", required=True)
ap.add_argument("--finished", required=True)
ap.add_argument("--cutoff-reason", default=None)
ap.add_argument("--date", default=None)
ap.add_argument("--preview", action="store_true")
a = ap.parse_args()
a.date = a.date or a.finished[:10]
assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.date), "--date must be YYYY-MM-DD (the ledger heading's form)"

LEDGER = REPO_ROOT / "ledger" / "ledger.md"
text = LEDGER.read_text(encoding="utf-8").replace("\r\n", "\n")
assert f"### {PREV} " in text and f"### {NUM} " not in text, f"ordering: {PREV} present, {NUM} absent"
cfg = load_e9_config(REPO_ROOT / "config" / "e9fl.toml", REPO_ROOT)
e9l = load_e9_config(REPO_ROOT / "config" / "e9l.toml", REPO_ROOT)
e7 = load_e7_config(REPO_ROOT / "config" / "e7.toml", REPO_ROOT)
manifest = manifest_sha256(manifest_path(e7))
src_id, tgt_id = pair_models(cfg.pair)

summarize(cfg)                                              # refuses on anything wrong; nothing is written then
f = json.loads((cfg.results_dir / "summary.json").read_text(encoding="utf-8"))
rep = json.loads((cfg.results_dir / "report.json").read_text(encoding="utf-8"))
assert rep["upstream_sha"] == cfg.upstream_sha
assert f["rope"] is None and f["bridge"] is None, "this cell registers no rope and no bridge; the summary carries one"
partial = f.get("partial")
if partial:
    assert a.cutoff_reason, "the report is a partial close: --cutoff-reason is required (entry 0045 stopping rule)"
else:
    assert rep["complete"] and not a.cutoff_reason, "the run is complete: --cutoff-reason is not allowed"

# The scaled long cell's figures, read to be stated BESIDE these -- never merged into them.
prior_path = e9l.results_dir / "summary.json"
assert prior_path.exists(), f"{prior_path} is missing; entry 0036's figures are stated beside these and must be readable"
prior = json.loads(prior_path.read_text(encoding="utf-8"))
assert prior["rope"] == e9l.rope and prior["rope"] is not None, "results/e9l/summary.json is not the scaled cell's"

rope = f["dump_rope"]
assert rope and rope.get("recorded"), \
    ("the run's dumps carry no RoPE spec, so neither the native-window nor the frequency-identity control ran -- "
     "and on a natively long receiver those two ARE the control (entry 0045)")
roles = ", ".join(f"{role} ({r['n_dumps']} dumps, max_position_embeddings {r['max_position_embeddings']:,}, "
                  f"inv_freq {str(r['inv_freq_sha256'])[:12]}, attention factor {r['attention_scaling']})"
                  for role, r in rope["by_role"].items())

sent = lambda t: t.strip().rstrip(".") + "."      # operator free text, punctuated once  # noqa: E731
s = lambda d, nd=4: f"{d['median']:.{nd}f} (p10 {d['p10']:.{nd}f}, p90 {d['p90']:.{nd}f})"   # noqa: E731
fs, cov, cc, tau = f["fstar"], f["coverage"], f["coverage_comparison"], f["tau"]
boot, pre, ra = f["median_fstar_same_K_bootstrap"], f["prefix_control"], f["rescore_agreement"]
ratio, br, lad = f["cross_over_same_median_delta"], f["bridge_r2"], f["fstar_ladder"]
agent, rule, prof = f["fstar_at_tau_agent"], f["rule"], f["length_profiles"]
n_sc, n_reg = cov["scored"], cov["registered"]
COVER = f"{n_sc} scored of {n_reg} registered"
band = f["band_outcome"]
cross_band = ("beyond the DEGRADES edge" if fs["cross_K"]["median"] >= rule["degrades_min"] else
              "inside the HOLDS edge" if fs["cross_K"]["median"] <= rule["holds_max"] else "between the edges")
ladder_txt = "; ".join(f"τ = {float(k):g}: same K {s(lad['same_K'][k])} / V {s(lad['same_V'][k])}"
                       for k in sorted(lad["same_K"], key=lambda k: -float(k)))
seam = " · ".join(f"{r['bin']}: {r['median']:.3f} (n={r['n_tokens']})"
                  for r in f["seam_profile_left_pooled"]["same_K"] if r["median"] is not None)
len_rows = "; ".join(f"|S| {r['bin']}: {'n/a (no handoff)' if r['fstar_K'] is None else s(r['fstar_K'])} "
                     f"(n = {r['n_handoffs']})" for r in prof["s_len"])
pos_rows = "; ".join(
    f"positions {r['bin']}: "
    f"{'n/a (no token)' if r['fstar_K_pooled'] is None else format(r['fstar_K_pooled'], '.4f')} / "
    f"{'n/a' if r['median_token_delta_K'] is None else format(r['median_token_delta_K'], '.3f')} "
    f"(n = {r['n_tokens']:,})" for r in prof["s_pos"])
dn = f["delta_null"]
kept_scored = len(ra["per_handoff"])
rescore_txt = (f"the {kept_scored} kept handoffs' stride-1 dumps fingerprint-verified and re-scored at home under "
               f"0028's tolerance (every square within {ra['max_rel_square']:.1e} relative, max |f* diff| "
               f"{ra['max_fstar_abs_diff']:.1e})" if kept_scored else
               "NO kept handoff was scored before the close, so the keep-subset re-score has nothing to read "
               "(stated, never a zero)")
blocks = f["fstar_blocks_ge_min"]["same_K"]
residual = cc["n"]["excluded_long"]
partial_txt = (f"**PARTIAL CLOSE** at {partial['closed_utc']} (entry {PREV}'s stopping rule): {COVER}, the scored set "
               f"being the prefix of the registered |S|-ascending order; unscored by id: "
               f"{', '.join(f'`{h}`' for h in partial['unscored'])}. Operator's stated reason for the cutoff: "
               f"{sent(a.cutoff_reason)} The cutoff did not depend on any score." if partial else f"Complete: {COVER}.")

ENTRY = f"""### {NUM} — {a.date} — E9 long half ran on the second model family `[BASELINE, DESCRIPTIVE]`: the long band at a NATIVE receiver; stated beside entry 0036's scaled-receiver figures and never pooled with them; no cell moves ({COVER})

**Setup, as registered ({PREV}).** {a.box}; linear-ceiling at the commit carrying {PREV} and
`config/e9fl.toml` (gate: entries {'/'.join(cfg.required_entries)}), upstream pin `{cfg.upstream_sha[:7]}`.
Pair {cfg.pair}: receiver {tgt_id}, source {src_id}, **neither scaled** — no `[e9.rope]`, no
`[e9.bridge]`, no `--rope-scaling` on any dump; the k = {cfg.mapper_k} mapper of this family's E8 sitting
for the cross arm, by sha. Launched {a.launched}, finished {a.finished}. {partial_txt} Of
{cov['observed']} observed handoffs: {n_reg} registered (longer side above {cfg.context_floor:,} and within
{cfg.context_cap:,} tokens under this pair's own tokenizer), {cc['n']['excluded_prior_cap']} covered by the
short cell and excluded here, {residual} above the cap and scored by NEITHER cell,
{cc['n']['excluded_empty_r']} with an empty receiver prompt. Every figure below is
`summarize_e9 --config config/e9fl.toml`'s, from a run that passed all of its checks: alignments re-derived
from the raw traces under the cap and floor; the run order re-derived; the partial prefix checked; every R²
recomputed from recorded moments; per-token squares summed against the moments; {rescore_txt}; τ recomputed
from the archived mapper; controls checked.

**The two controls that replace entry 0035's configuration bridge, reported first.** On a natively long
receiver these ARE the evidence that nothing was scaled, and `summarize_e9` refuses this cell outright if
the dumps carry no RoPE spec. Over all {rope['n_dumps']} dumps: **native window** — the registered cap
{cfg.context_cap:,} sat inside every dump's own recorded `max_position_embeddings`, so no dump asked either
model for a position its configuration does not declare; **frequency identity, by model role** — {roles};
the spec-vs-model halt check passed at every dumped position (worst |diff| {rope['spec_check_max_abs']:.1e}
against atol {rope['spec_check_atol']:.0e}), and every dump recorded an attention factor of 1.0. The roles
are compared separately because this pair's two sides build different inverse-frequency vectors by
construction (entry {FAMILY}).

**Controls (0023, 0025).** Pipeline identity: exactly zero. Prefix invariance on the first handoff in run
order: max centered per-token δ {pre['max_token_delta']:.3e} over {pre['n_positions']:,} positions
(tolerance {pre['tolerance']:.0e}, this pair's own value). δ_null same K / V token-mean median
{dn['same_K']['median_token_mean']:.3f} / {dn['same_V']['median_token_mean']:.3f}; equal-token null pairs
{f['delta_null_equal_token_fraction']:.4f}. Matched fraction |M|/|R| (a floor): {s(f['matched_fraction'])}.

**The statistic, computed and verdict-bearing for nothing.** Per scored handoff, E9-same, K read-out:
f*(τ_K = {tau['K']:.4f}) as 0023 defines it, median over scored handoffs. τ_K is 1 − THIS pair's own
held-out R² and is identical to the short cell's; this cell has no hypothesis row, so the band words below
are stated descriptively and decide nothing.

- **median f*(τ_K), E9-same K: {s(fs['same_K'])}** over {fs['same_K']['n']} handoffs ({COVER}); seeded
  bootstrap of the median (seed {boot['seed']}, {boot['reps']} reps): [{boot['lower_2.5']:.4f},
  {boot['upper_97.5']:.4f}]. Against 0023's edges (HOLDS ≤ {rule['holds_max']}, DEGRADES ≥
  {rule['degrades_min']}) the band word would be **{band}**, stated descriptively.
- f*(τ_V = {tau['V']:.4f}), E9-same V (alongside): {s(fs['same_V'])}.
- τ ladder (descriptive): {ladder_txt}.
- f*(τ_agent_K = {f['tau_agent_K']:.4f}): same K {s(agent['same_K'])}; cross K {s(agent['cross_K'])}.
- f*(τ_K) over matched blocks of length ≥ {f['min_block_len']}: same K {s(blocks) if blocks else 'NOT COMPUTABLE'}.
- Seam profile under the causal distance b⁻(t), E9-same K, pooled median δ by bin: {seam}.

**Length profiles (entry {PREV} control 5, descriptive).** (i) by |S| bin, median f*(τ_K) same K over
handoffs: {len_rows}. (ii) by matched-token position in S, pooled f*(τ_K) same K / median δ_K: {pos_rows}.
(ii) is the long-context figure — whether agreement at a re-rendered position depends on how deep in the
sender's context the token sat — and its bins are cut at this family's own RoPE boundary, not at entry
0035's YaRN midpoint.

**Cross-arm outcome, named (descriptive, decides nothing).** E9-cross through this pair's own
k = {cfg.mapper_k} mapper: median f*(τ_K) = {s(fs['cross_K'])}, f*(τ_V) = {s(fs['cross_V'])}; against the
same edges the transfer arm sits {cross_band}. Cross/same median-δ ratio K / V: {s(ratio['K'], 1)} /
{s(ratio['V'], 1)}. Bridge R² (A5 across the handoff; not control 4, which does not exist here): same K
{s(br['same_K'])}, same V {s(br['same_V'])}, cross K {s(br['cross_K'])}, cross V {s(br['cross_V'])}.

**Beside entry 0036, and NOT pooled with it.** 0036 measured
{prior['coverage']['scored']} handoffs of {prior['coverage']['registered']} registered on
{e9l.pair} with the receiver pushed to {e9l.context_cap:,} positions by static YaRN
(`{json.dumps(e9l.rope, sort_keys=True)}`), at τ_K = {prior['tau']['K']:.4f}, and reported median f*(τ_K)
{s(prior['fstar']['same_K'])}. This cell measured {n_sc} handoffs on {cfg.pair} with **nothing scaled**, at
τ_K = {tau['K']:.4f}, and reported {s(fs['same_K'])}. **The two numbers are stated side by side and are not
comparable as numbers**: different models, different tokenizers and therefore different handoff sets,
different mappers and therefore different τ, and — the point entry {PREV} registered — one receiver is
scaled past its pretraining window and the other is not. Nothing here supports, refutes or moves H-E9L,
and no figure from the two cells is averaged, pooled or differenced.

**What this establishes, stated narrowly.** On {tgt_id} re-rendering {n_sc} real SWE-bench
`{cfg.agent}` handoffs whose longer side runs {cfg.context_floor + 1:,}–{cfg.context_cap:,} tokens under
this pair's own tokenizer, at a receiver inside its native window throughout, with 0019's alignment and
0023's per-token rule at this pair's own τ, the same-model oracle recompute floor is as stated above.
**Not established:** any hypothesis cell — this entry moves none and carries no `verdict:` line; anything
about the {residual} handoffs above {cfg.context_cap:,} or the {cc['n']['excluded_empty_r']} with an empty
receiver prompt; anything about the {n_reg - n_sc} unscored registered handoffs{"" if partial else " (none)"}; any achievable recompute
scheme (a floor, 0027); anything about a scaled receiver, which this cell does not contain; one pair, one
direction, one mapper, one alignment method; generation quality after reuse.

e7-manifest-sha256: {manifest}

prior-entries-sha256: PLACEHOLDER
"""

if a.preview:
    print(ENTRY)
    raise SystemExit(0)

new = text + ("" if text.endswith("\n") else "\n") + "\n" + ENTRY
head = _ENTRIES_HEAD.search(new)
digest = chain_hash(new, new.index(f"### {NUM} "), head.start())
new = new.replace("prior-entries-sha256: PLACEHOLDER", f"prior-entries-sha256: {digest}")
LEDGER.write_text(new, encoding="utf-8", newline="\n")
print(f"appended {NUM}; chain", digest[:12])
r = subprocess.run([sys.executable, "-m", "linear_ceiling.ledger_check"], cwd=REPO_ROOT, capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip())
raise SystemExit(r.returncode)

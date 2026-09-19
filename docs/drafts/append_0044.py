"""Append entry 0044 -- the E9 short cell of the second model family RAN; the H-E9F verdict, written ONLY
from an in-process `summarize_e9 --config config/e9f.toml` run (it refuses on anything wrong and nothing is
written then). Sets the H-E9F cell by its `verdict:` line.

Ordering guard: 0043 on the ledger, 0044 absent, the H-E9F row present and still `unresolved`. The band
outcome maps to the ledger vocabulary (HOLDS -> HELD, DEGRADES -> NOT CONFIRMED, UNRESOLVED -> unresolved).
Run facts the summarizer cannot know come as arguments and are refused when missing:

  --box "<instance type, GPU, region, instance id>"   --launched <UTC>   --finished <UTC>
  [--tau-ceiling-applies {yes,no}] --tau-ceiling-note "<provenance note about entry 0039's ceiling>"
  --date <YYYY-MM-DD>   (defaults to --finished's date)
  --preview             (print, do not append)

The tau ceiling is not optional: entry 0039 registered, before the fit, that tau_K > 0.45 makes this
cell UNRESOLVED BY CONSTRUCTION (a mapper that transfers badly enough makes f*(tau_K) trivially small
for everything, and a HOLDS read off it would mean nothing). The script derives whether the ceiling
applies from the summarizer's tau_K. `--tau-ceiling-applies`, when supplied, is an auditable assertion
about that derived result and is refused on disagreement; it never selects the verdict. The required
free-text note records provenance only and likewise cannot alter the verdict.

Per entry 0042: coverage "n scored of N registered" travels with every number; nothing is pooled with
entry 0029's handoffs; f* is read on a floor (0027). Runs `ledger_check` after appending. Delete once
appended, chained to the append with `&&`."""
import argparse
import json
import re
import subprocess
import sys

from linear_ceiling import REPO_ROOT
from linear_ceiling.config import load_e7_config, load_e9_config
from linear_ceiling.e7_manifest import manifest_path, manifest_sha256
from linear_ceiling.ledger_check import VERDICTS, _ENTRIES_HEAD, chain_hash
from linear_ceiling.pairs import pair_models
from linear_ceiling.summarize_e9 import summarize

NUM, PREV = "0044", "0043"
FAMILY = "0039"      # the family registration entry, APPENDED 2026-09-18 -- a fixed number now
E8FIG = "0040"      # the E8 figures entry this mapper's fit was reported in; APPENDED, fixed
SHORT = "0042"      # this cell's registration entry; APPENDED 2026-09-18, fixed
TAU_K_CEILING = 0.45                 # entry 0039; asserted against the committed entry below
ap = argparse.ArgumentParser()
ap.add_argument("--box", required=True)
ap.add_argument("--launched", required=True)
ap.add_argument("--finished", required=True)
ap.add_argument("--cutoff-reason", default=None,
                help="REQUIRED on a partial close (entry 0042's stopping rule); forbidden otherwise")
ap.add_argument("--tau-ceiling-applies", choices=("yes", "no"), default=None,
                help="optional assertion only; derived from summary tau_K > entry 0039's 0.45")
ap.add_argument("--tau-ceiling-note", required=True,
                help="provenance note only; cannot select whether the ceiling applies")
ap.add_argument("--date", default=None)
ap.add_argument("--preview", action="store_true")
a = ap.parse_args()
a.date = a.date or a.finished[:10]
assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.date), "--date must be YYYY-MM-DD (the ledger heading's form)"

LEDGER = REPO_ROOT / "ledger" / "ledger.md"
text = LEDGER.read_text(encoding="utf-8").replace("\r\n", "\n")
assert f"### {PREV} " in text and f"### {NUM} " not in text, f"ordering: {PREV} present, {NUM} absent"
family_start = text.index(f"### {FAMILY} ")
family_end = text.find("\n### ", family_start + 1)
family_entry = text[family_start: family_end if family_end >= 0 else len(text)]
assert re.search(r"\*\*τ_K ceiling\*\*.*?short cell is UNRESOLVED by\s+construction.*?\n0\.45\.",
                 family_entry, re.S), \
    f"entry {FAMILY} no longer registers the expected tau_K > {TAU_K_CEILING:g} ceiling"
cfg = load_e9_config(REPO_ROOT / "config" / "e9f.toml", REPO_ROOT)
e7 = load_e7_config(REPO_ROOT / "config" / "e7.toml", REPO_ROOT)
manifest = manifest_sha256(manifest_path(e7))
src_id, tgt_id = pair_models(cfg.pair)

summarize(cfg)                                              # refuses on anything wrong; nothing is written then
f = json.loads((cfg.results_dir / "summary.json").read_text(encoding="utf-8"))
rep = json.loads((cfg.results_dir / "report.json").read_text(encoding="utf-8"))
assert rep["complete"] and rep["upstream_sha"] == cfg.upstream_sha
assert f["rope"] is None and f["bridge"] is None and f["length_profiles"] is None, \
    "this cell registers no rope, no bridge and no length profiles; the summary carries one"
# Entry 0042 REGISTERS a partial close for this cell, and entry 0043 registers the protocol that
# produces one. This line used to refuse any partial outright -- written when the cell forbade one --
# so a run stopped at the budget ceiling could be closed, mirrored and verified and then have no
# verdict entry to write. The shape is what must be checked, not the fact: a prefix of the registered
# order, with the unscored handoffs named, exactly as entry 0036 did for the long half.
partial = f.get("partial") or rep.get("partial")
if partial:
    assert cfg.allow_partial, "the report claims a partial close but config/e9f.toml does not register one"
    assert a.cutoff_reason, "the report is a partial close: --cutoff-reason is required (entry 0042's rule)"
    order, scored = rep["run_order"], list(rep["scores"])
    assert scored == order[:len(scored)], \
        "the scored set is NOT a prefix of the registered run order; 0042 registers a prefix, not a subset"
    assert list(partial["unscored"]) == order[len(scored):], \
        "the partial does not name exactly the unscored tail of the registered order"
else:
    assert not a.cutoff_reason, "the run is complete: --cutoff-reason is not allowed"

BAND_TO_VERDICT = {"HOLDS": "HELD", "DEGRADES": "NOT CONFIRMED", "UNRESOLVED": "unresolved"}
band_verdict = BAND_TO_VERDICT[f["band_outcome"]]
tau = f["tau"]
ceiling = float(tau["K"]) > TAU_K_CEILING
if a.tau_ceiling_applies is not None:
    asserted_ceiling = a.tau_ceiling_applies == "yes"
    assert asserted_ceiling == ceiling, \
        (f"--tau-ceiling-applies {a.tau_ceiling_applies} disagrees with the registered rule: "
         f"tau_K {float(tau['K']):.6g} > {TAU_K_CEILING:g} is "
         f"{'true' if ceiling else 'false'}; the operator assertion cannot select the verdict")
VERDICT = "unresolved" if ceiling else band_verdict
assert VERDICT in VERDICTS, f"{VERDICT!r} is not one of ledger_check.VERDICTS"

# The two controls that stand in for entry 0035's configuration bridge on a natively long receiver.
rope = f["dump_rope"]
assert rope and rope.get("recorded"), \
    ("the run's dumps carry no RoPE spec, so neither the native-window nor the frequency-identity control "
     "ran; the pin must be the RoPE-spec commit or a descendant of it")
roles = ", ".join(f"{role} ({r['n_dumps']} dumps, max_position_embeddings {r['max_position_embeddings']:,}, "
                  f"inv_freq {str(r['inv_freq_sha256'])[:12]}, attention factor {r['attention_scaling']})"
                  for role, r in rope["by_role"].items())
n_roles = len(rope["by_role"])

sent = lambda t: t.strip().rstrip(".") + "."      # operator free text, punctuated once  # noqa: E731
s = lambda d, nd=4: f"{d['median']:.{nd}f} (p10 {d['p10']:.{nd}f}, p90 {d['p90']:.{nd}f})"   # noqa: E731
fs, cov, cc = f["fstar"], f["coverage"], f["coverage_comparison"]
boot, pre, ra = f["median_fstar_same_K_bootstrap"], f["prefix_control"], f["rescore_agreement"]
ratio, br, lad = f["cross_over_same_median_delta"], f["bridge_r2"], f["fstar_ladder"]
agent, rule = f["fstar_at_tau_agent"], f["rule"]
n_sc, n_reg = cov["scored"], cov["registered"]
COVER = f"{n_sc} scored of {n_reg} registered"
cross_band = ("beyond the DEGRADES edge" if fs["cross_K"]["median"] >= rule["degrades_min"] else
              "inside the HOLDS edge" if fs["cross_K"]["median"] <= rule["holds_max"] else "between the edges")
ladder_txt = "; ".join(f"τ = {float(k):g}: same K {s(lad['same_K'][k])} / V {s(lad['same_V'][k])}"
                       for k in sorted(lad["same_K"], key=lambda k: -float(k)))
seam = " · ".join(f"{r['bin']}: {r['median']:.3f} (n={r['n_tokens']})"
                  for r in f["seam_profile_left_pooled"]["same_K"] if r["median"] is not None)
dn = f["delta_null"]
kept_scored = len(ra["per_handoff"])
rescore_txt = (f"the {kept_scored} kept handoffs' stride-1 dumps fingerprint-verified and re-scored at home under "
               f"0028's tolerance (every square within {ra['max_rel_square']:.1e} relative, max |f* diff| "
               f"{ra['max_fstar_abs_diff']:.1e})" if kept_scored else
               "NO kept handoff was scored, so the keep-subset re-score has nothing to read (stated, never a zero)")
blocks = f["fstar_blocks_ge_min"]["same_K"]
first = ((f"**UNRESOLVED BY CONSTRUCTION (entry {FAMILY}'s registered τ_K ceiling).** τ_K for "
          f"this pair is {tau['K']:.4f} > {TAU_K_CEILING:.2f}. Operator provenance note "
          f"(non-verdict-bearing): {sent(a.tau_ceiling_note)} The band word below is computed and stated, but the cell is set to "
          f"`unresolved`: a recompute fraction read against a tolerance this loose does not distinguish a receiver "
          f"that agrees with itself from one that does not, and that reading was fixed before the fit, not after "
          f"this number was seen.\n\n") if ceiling else
         (f"**The registered τ_K ceiling does not bite (entry {FAMILY}).** τ_K = {tau['K']:.4f} ≤ "
          f"{TAU_K_CEILING:.2f}, so the band below is read as the rule writes it. Operator provenance note "
          f"(non-verdict-bearing): {sent(a.tau_ceiling_note)}\n\n"))

closed = (f"**Closed on a registered prefix ({PREV}'s stop protocol, {SHORT}'s rule).** "
          f"{COVER}, in the registered `{cfg.order_by}` order. Operator cutoff reason: "
          f"{sent(a.cutoff_reason)} Unscored, named here and excluded from every figure above and below: "
          f"{', '.join('`' + h + '`' for h in partial['unscored'])}.\n\n"
          if partial else "")

ENTRY = f"""### {NUM} — {a.date} — E9 short cell ran on the second model family `[BASELINE]`; H-E9F {VERDICT} ({COVER}{', closed on a registered prefix' if partial else ''})

{first}{closed}**Setup, as registered ({SHORT}, amended by {PREV}).** {a.box}; linear-ceiling at the commit carrying {PREV} and
`config/e9f.toml` (gate: entries {'/'.join(cfg.required_entries)}), upstream pin `{cfg.upstream_sha[:7]}`
(the one-line `PAIRS` entry on top of the RoPE-spec commit). Pair {cfg.pair}: receiver {tgt_id}, source
{src_id}, **neither scaled** — no `[e9.rope]`, no `[e9.bridge]`, no `--rope-scaling` on any dump; the
k = {cfg.mapper_k} mapper this family's E8 sitting fitted (entry {E8FIG}) for the cross arm, by sha. Launched
{a.launched}, finished {a.finished}. {COVER}, in the registered `{cfg.order_by}` order. Of
{cov['observed']} observed handoffs: {n_reg} included (|S| and |R| both within {cfg.context_cap:,} tokens
under this pair's own tokenizer), {cc['n']['excluded_long']} above the cap, {cc['n']['excluded_empty_r']}
with an empty receiver prompt. Every figure below is `summarize_e9 --config config/e9f.toml`'s, from a run
that passed all of its checks: alignments re-derived from the raw traces under the cap; every R²
recomputed from recorded moments; per-token squares summed against the moments; {rescore_txt}; τ
recomputed from the archived mapper and checked against the config; controls checked.

**The two controls that replace entry 0035's configuration bridge.** This receiver is natively long, so
there is no scaled arm to compare and no bridge to run; what stands in its place is read off the dumps
themselves, from the `RopeSpec` the upstream recorded off each loaded model's own rotary embedding and
halt-checked against the model at every dumped position (worst |diff| {rope['spec_check_max_abs']:.1e}
against atol {rope['spec_check_atol']:.0e}), over all {rope['n_dumps']} dumps of the run. **(i) Native
window:** the registered cap {cfg.context_cap:,} sat inside EVERY dump's own recorded
`max_position_embeddings` — no dump asked either model for a position its configuration does not declare,
which is the positive "no extrapolation happened" statement. **(ii) Frequency identity, scoped by model
role:** {roles}. The {n_roles} roles are compared separately and MUST be: this pair's two sides carry
different llama3 scaling factors and build different inverse-frequency vectors by construction, so an
unscoped equality assert would refuse every correct run. Every dump recorded an attention factor of 1.0,
the only positive evidence that the box applied no scaling the registration does not describe.

**Controls (0023, 0025).** Pipeline identity: exactly zero. Prefix invariance on the first handoff in run
order: max centered per-token δ {pre['max_token_delta']:.3e} over {pre['n_positions']:,} positions
(tolerance {pre['tolerance']:.0e}, this pair's own value — entry {FAMILY}'s pre-registered function of
τ_K, never the Qwen cells'). δ_null same K / V token-mean median {dn['same_K']['median_token_mean']:.3f} /
{dn['same_V']['median_token_mean']:.3f}; equal-token null pairs {f['delta_null_equal_token_fraction']:.4f}.
Matched fraction |M|/|R| (a floor): {s(f['matched_fraction'])}.

**The rule (0023, carried verbatim by {PREV}) and the figure it reads.** Per scored handoff, E9-same, K
read-out: f*(τ_K) = the fraction of matched tokens an oracle must recompute before the mean centered
deviation of the rest is at or below τ_K = {tau['K']:.4f}; median over scored handoffs; HOLDS ≤
{rule['holds_max']}, DEGRADES ≥ {rule['degrades_min']}, UNRESOLVED between. τ_K is 1 − THIS pair's own
held-out R² ({f['calibration']['heldout']['K_r2_layer_mean']:.4f} over
{f['calibration']['heldout']['n_tokens']:,} tokens), recomputed here and refused on disagreement.

- **median f*(τ_K), E9-same K: {s(fs['same_K'])}** over {fs['same_K']['n']} handoffs ({COVER}). Seeded
  bootstrap of the median (seed {boot['seed']}, {boot['reps']} reps; reported, not read):
  [{boot['lower_2.5']:.4f}, {boot['upper_97.5']:.4f}].
- f*(τ_V = {tau['V']:.4f}), E9-same V (alongside): {s(fs['same_V'])}.
- τ ladder (descriptive): {ladder_txt}.
- f*(τ_agent_K = {f['tau_agent_K']:.4f}) (alongside): same K {s(agent['same_K'])}; cross K {s(agent['cross_K'])}.
- f*(τ_K) over matched blocks of length ≥ {f['min_block_len']}: same K {s(blocks) if blocks else 'NOT COMPUTABLE'}.
- Seam profile under the causal distance b⁻(t), E9-same K, pooled median δ by bin: {seam}.

**Band outcome, against the rule as written: {f['band_outcome']}** — on this pair's {n_sc} scored
handoffs, **never pooled with entry 0029's**: the same numeric cap over a different tokenizer selects a
different set of handoffs, and the two cells are compared in prose or not at all.
{"Not one scored handoff has a single matched token whose centered deviation exceeds τ_K on the same-model arm." if fs['same_K']['median'] == 0 and fs['same_K']['p90'] == 0 else ""}

**Read on a floor (0027, bound to this cell).** f*(τ) is an oracle LOWER BOUND on the recompute fraction
(oracle selection, recompute in isolation); this cell reads "no more than the mapper, on a floor", never
that an achievable scheme reaches it.

**Cross-arm outcome, named (descriptive, decides nothing).** E9-cross through this pair's own
k = {cfg.mapper_k} mapper: median f*(τ_K) = {s(fs['cross_K'])} and f*(τ_V) = {s(fs['cross_V'])}; against
the same edges the transfer arm sits {cross_band}. Cross/same median-δ ratio K / V: {s(ratio['K'], 1)} /
{s(ratio['V'], 1)}. Bridge R² (A5 across the handoff; decides nothing): same K {s(br['same_K'])}, same V
{s(br['same_V'])}, cross K {s(br['cross_K'])}, cross V {s(br['cross_V'])}.

**What this establishes, stated narrowly.** On {tgt_id} re-rendering {n_sc} real SWE-bench
`{cfg.agent}` handoffs whose sender and receiver prompts both fit {cfg.context_cap:,} tokens under this
pair's own tokenizer, with 0019's alignment and 0023's per-token rule and τ calibrated on THIS pair's
k = {cfg.mapper_k} mapper, the same-model oracle recompute floor is as stated above. **Not established:**
anything about the {cc['n']['excluded_long']} handoffs above the cap or the
{cc['n']['excluded_empty_r']} with an empty receiver prompt; any achievable recompute scheme; anything
about the Qwen cells, which are a different pair and are unchanged; one pair, one direction, one mapper,
one alignment method; generation quality after reuse. `eval_hellaswag.py` and `compose_mapper.py` remain
out of scope for this pair (entry {FAMILY}).

verdict: H-E9F = {VERDICT}
e7-manifest-sha256: {manifest}

prior-entries-sha256: PLACEHOLDER
"""

if a.preview:
    print(ENTRY)
    raise SystemExit(0)

row = re.compile(rf"^(\| H-E9F \|.*\| E9-family \(entry {PREV}\) \|) unresolved (\|\s*)$", re.M)
assert len(row.findall(text)) == 1, "H-E9F row not found in its expected shape (registered `unresolved` by " + PREV + ")"
text = row.sub(lambda m: f"{m.group(1)} {VERDICT} {m.group(2)}", text)

new = text + ("" if text.endswith("\n") else "\n") + "\n" + ENTRY
head = _ENTRIES_HEAD.search(new)
digest = chain_hash(new, new.index(f"### {NUM} "), head.start())
new = new.replace("prior-entries-sha256: PLACEHOLDER", f"prior-entries-sha256: {digest}")
LEDGER.write_text(new, encoding="utf-8", newline="\n")
print(f"appended {NUM} (H-E9F = {VERDICT}); chain", digest[:12])
r = subprocess.run([sys.executable, "-m", "linear_ceiling.ledger_check"], cwd=REPO_ROOT, capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip())
raise SystemExit(r.returncode)

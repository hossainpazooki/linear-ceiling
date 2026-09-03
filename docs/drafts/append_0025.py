"""Append the E9 pre-prefill amendment (0025 by default) -- ordering-guarded, every figure read
from config or recomputed in-process from the raw traces and the verified E7/E8 records.

What the entry registers (all descriptive; the H-E9 rule, tau_K and the band are untouched):
the tau ladder; the alongside agent-text tau (E8 arm (b)); keep-subset n; the coverage
comparison (included vs excluded); the prefix-invariance control (halts); the causal seam
distance b^-(t); matched-block lengths and f* over blocks >= min_block_len; a seeded bootstrap
of the median; the delta_null equal-token fraction; `e9 --align-only`.

Refuses unless: entry 0024 is in the ledger and the target number is free; `e9.REQUIRED_ENTRIES`
names the target number (the gate and the entry must agree, or the run could start without it);
`config/e9.toml` loads (the loader validates every 0025 parameter); NO prefill has happened
(`results/e9/report.json` and `results/e9/scores/` absent -- 0023: nothing in the rule section
is revisited after the first score file exists); `results/e9/calibration/tau.json` carries
`agent_K` equal to config and to 1 - E8 arm (b) K R^2 from `results/e8/report.json`; the
E7 report verifies under `summarize_e7` (the coverage comparison reads 0018's rows from it).
The prior keep n is read from `config/e9.toml` at PRIOR_CONFIG_REV (the last commit before the
0025 staging), never typed and never from HEAD (HEAD already carries the new value once the
instrument commit lands -- the guard that retired this script before its first append).

    .venv/Scripts/python.exe docs/drafts/append_0025.py --preview      # print the text, touch nothing (~3 min CPU: E7 summarizer)
    .venv/Scripts/python.exe docs/drafts/append_0025.py                # append as 0025
    .venv/Scripts/python.exe docs/drafts/append_0025.py --number 26    # only after e9.REQUIRED_ENTRIES says 0026

Delete this script once the entry is appended (docs/drafts/README.md convention).
"""
import argparse
import json
import re
import subprocess
import sys
import tomllib
from dataclasses import asdict
from datetime import date
from pathlib import Path

import numpy as np

from linear_ceiling import REPO_ROOT, e9
from linear_ceiling.config import load_e7_config, load_e9_config
from linear_ceiling.e7_manifest import manifest_path, manifest_sha256
from linear_ceiling.e7_stats import summary
from linear_ceiling.e8_text import qwen_encoder
from linear_ceiling.e9 import keep_subset, pair_models, submission_dirs
from linear_ceiling.e9_align import align, coverage_comparison, load_handoffs
from linear_ceiling.e9_pertoken import BLOCK_BIN_LABELS, block_bin, block_lengths
from linear_ceiling.hashing import sha256_file_bytes
from linear_ceiling.ledger_check import chain_hash, check, committed_manifest_sha, parse_ledger
from linear_ceiling.summarize_e7 import summarize as summarize_e7
from linear_ceiling.weights import snapshot

LEDGER = REPO_ROOT / "ledger" / "ledger.md"
CONFIG = REPO_ROOT / "config" / "e9.toml"
PRIOR_CONFIG_REV = "8b6cced"     # last commit before the 0025 staging (f8cecf7); keep n and the rule as 0023 left them
_TOL = 1e-9


def prior_config() -> dict:
    r = subprocess.run(["git", "show", f"{PRIOR_CONFIG_REV}:config/e9.toml"], cwd=REPO_ROOT, capture_output=True,
                       text=True, encoding="utf-8")
    if r.returncode != 0:
        raise RuntimeError(f"cannot read {PRIOR_CONFIG_REV}:config/e9.toml")
    return tomllib.loads(r.stdout)["e9"]


def bytes_per_token(model_id: str) -> tuple[int, dict]:
    """fp16 K+V per token as upstream dump_kv writes it: n_layers x n_kv x d_h x 2 (K,V) x 2 bytes."""
    c = json.loads((Path(snapshot(model_id)) / "config.json").read_text(encoding="utf-8"))
    d_h = c.get("head_dim") or c["hidden_size"] // c["num_attention_heads"]
    shape = {"n_layers": int(c["num_hidden_layers"]), "n_kv": int(c["num_key_value_heads"]), "d_h": int(d_h)}
    return shape["n_layers"] * shape["n_kv"] * shape["d_h"] * 2 * 2, shape


def recon(cfg, e7):
    """0019's alignment over every observed handoff, computed and NOT written: records, |S|/|R| of
    the included, and the pooled matched-block length distribution."""
    src_id, tgt_id = pair_models(cfg.pair)
    enc = qwen_encoder(snapshot(src_id))
    counter = lambda t, ct="assistant": 0  # noqa: E731
    records, included, blocks = [], {}, {lab: 0 for lab in BLOCK_BIN_LABELS}
    n_blocks, ge_min = 0, 0
    for h in load_handoffs(submission_dirs(e7, cfg), counter):
        rec, _s, _r, pairs = align(h, enc, cfg.context_cap)
        records.append(asdict(rec))
        if not rec.excluded:
            included[h.handoff_id] = (rec.n_sender, rec.n_receiver)
            bl = block_lengths(pairs)
            bb = block_bin(bl)
            for i, lab in enumerate(BLOCK_BIN_LABELS):
                blocks[lab] += int((bb == i).sum())
            n_blocks += int(round(float(np.sum(1.0 / bl)))) if len(bl) else 0
            ge_min += int((bl >= int(cfg.rule["min_block_len"])).sum())
    return records, included, {"by_bin": blocks, "n_blocks": n_blocks, "tokens_ge_min": ge_min}, \
        bytes_per_token(src_id), bytes_per_token(tgt_id)


def volume(included, ids, bpt_src, bpt_tgt) -> float:
    # three dumps per handoff (0019): receiver on S, receiver on R, source on S
    return sum((included[h][0] + included[h][1]) * bpt_tgt + included[h][0] * bpt_src for h in ids)


def _q(s, digits=3):
    return f"{s['median']:.{digits}f} (p10 {s['p10']:.{digits}f}, p90 {s['p90']:.{digits}f})" if s else "n/a"


def _qi(s):
    return f"{s['median']:,.0f} (p10 {s['p10']:,.0f}, p90 {s['p90']:,.0f})" if s else "n/a"


def render(number: int, cfg, prior: dict, records, included, blocks, src, tgt, cov, e8_agent_k: float,
           e7_sha: str, msha: str) -> str:
    (bpt_src, sh_src), (bpt_tgt, sh_tgt) = src, tgt
    old_n = int(prior["keep"]["n"])
    ids = sorted(included)
    old = keep_subset(ids, cfg.keep_seed, old_n)
    new = keep_subset(ids, cfg.keep_seed, cfg.keep_n)
    shared = sorted(set(old) & set(new))
    vol_old, vol_new = volume(included, old, bpt_src, bpt_tgt), volume(included, new, bpt_src, bpt_tgt)
    tau_k, tau_v, tau_a = float(cfg.rule["tau_K"]), float(cfg.rule["tau_V"]), float(cfg.rule["tau_agent_K"])
    ladder = [float(t) for t in cfg.rule["tau_ladder"]]
    lad_k = ", ".join(f"{t:.4g}" for t in [tau_k, *ladder])
    lad_v = ", ".join(f"{t:.4g}" for t in [tau_v, *ladder])
    short = lambda h: h.split("/", 1)[1] if "/" in h else h  # noqa: E731
    new_lines = "\n".join(f"  - `{h}` ({volume(included, [h], bpt_src, bpt_tgt) / 1e9:.2f} GB)" for h in new)
    n_obs, n_inc = len(records), len(included)
    inc, exl = cov["included"], cov["excluded_long"]
    tot_tokens = sum(blocks["by_bin"].values())
    bins_line = ", ".join(f"{lab}: {blocks['by_bin'][lab]:,} ({100 * blocks['by_bin'][lab] / tot_tokens:.2f}%)"
                          for lab in BLOCK_BIN_LABELS)
    tol = float(cfg.controls["prefix_invariance_max_delta"])
    return f"""### {number:04d} — {date.today().isoformat()} — E9 amended before any prefill: coverage registered; agent-text τ alongside; prefix-invariance control; causal seam distance; block lengths; bootstrap; τ ladder; keep-subset {old_n} → {cfg.keep_n}; no verdict changes

**Why before the box.** An independent pre-run review of E9 (2026-09-02) and the E-RL design each
proposed additions to what E9 reports and controls. None touches the H-E9 rule, τ_K = {tau_k:.4f}, the
band, or the four cells; every one of them is of the kind 0023 forbids after the first score file
exists, so they are registered together here. No prefill has happened: `results/e9/report.json` is
absent at append and this script refuses otherwise. Nothing in this entry is verdict-bearing.

**Coverage, registered (review finding 1).** 0019's alignment over the observed handoffs at the
registered cap {cfg.context_cap}: **{n_inc} included of {n_obs} observed** ({cov['n']['excluded_long']} excluded because `S` or `R`
exceeds the cap, {cov['n']['excluded_empty_r']} because the receiver prompt is empty in the trace). The excluded handoffs
are the long ones, and what the cap selects on is stated beside every E9 figure from here on:
included vs excluded-by-length, medians (p10, p90) -- |S| {_qi(inc['n_sender'])} vs {_qi(exl['n_sender'])};
|R| {_qi(inc['n_receiver'])} vs {_qi(exl['n_receiver'])}; entry 0018's per-handoff overlap
{_q(inc['overlap_fraction_0018'])} vs {_q(exl['overlap_fraction_0018'])}; 0018's recoverable fraction
{_q(inc['recoverable_fraction_0018'])} vs {_q(exl['recoverable_fraction_0018'])} (0018 rows from the E7 report verified by
`summarize_e7` at append, sha256 `{e7_sha[:12]}`; {cov['unmatched_0018_rows']} handoffs without a row). H-E9 is decided on the
included set and is a claim about it; `summarize_e9` recomputes this comparison and states it.

**Agent-text τ, alongside (review finding 2).** τ_K anchors HOLDS to "no more than the mapper itself"
on the mapper's own GENERIC held-out text (0023). Entry 0020 arm (b) measured the same k = 1 mapper on
AGENT text at K R² = {1 - e8_agent_k:.4f}, so on the distribution E9 actually reads, the mapper's own tolerance
is **τ_agent_K = {tau_a:.4f}** (= 1 − {1 - e8_agent_k:.4f}, recomputed by `summarize_e9 --calibrate-tau` from
`results/e8/report.json` and refused on disagreement, like τ_K). f*(τ_agent_K) is reported for the K
arms (E9-same and E9-cross) beside f*(τ_K), per handoff and as medians. It is a K tolerance and is
applied to nothing else. **The band reads τ_K only**; this entry does not move it -- a verdict-bearing
τ chosen after seeing which is looser is exactly what 0023 refused to do -- but the reader sees both.

**τ ladder (descriptive; E-RL design).** f*(τ) is ALSO stated at τ_K ∈ {{{lad_k}}} and
τ_V ∈ {{{lad_v}}} -- the registered value first, then `[e9.rule] tau_ladder` -- for every arm, per
handoff and as median / p10 / p90, from the same per-token record (a re-sort). It reads *how far
inside* the tolerance the re-render sits; the loader refuses a ladder that is not strictly decreasing
inside (0, τ_K). f* at every τ remains an oracle LOWER BOUND (0023, both reasons).

**Prefix-invariance control (review finding 3; HALTS).** 0023's pipeline-identity control scores the
receiver's dump of `S` against itself: the scorer loads one dump twice, so its zero is the scorer's
arithmetic and cannot fail on the box. It stays (it still proves the dump loads and the record sums).
Added: on the same first included handoff, the receiver prefills `S` followed by **R's first token**
(recorded), and rows 0..|S|−1 of that dump are scored against the `S` dump at pairs (p, p). Causal
attention makes them equal up to kernel arithmetic; the max centered per-token deviation (token mean,
K or V, in R²'s units) must be ≤ **{tol:.0e}** -- three orders under τ_K, well above float32 noise -- or
the run HALTS before any handoff is scored. The S+1 dump is transient; its per-token record and
score are kept and `summarize_e9` re-derives the maximum, refuses above the tolerance, and refuses a
record whose extra token is not R's first. The tolerance is a registered judgment, not a citation.

**Causal seam distance b⁻(t) (review finding 4).** 0023's b(t) is the distance to the nearest seam on
EITHER side; a matched token's K/V depend only on what precedes it, so a seam after it cannot touch
them and bin 0 is diluted by construction. b⁻(t) = distance to the nearest PRECEDING seam (same seam
definition; a token with no seam before it reports |R|) is computed from the alignment alone and the
seam profile is stated under both, same fixed bins. b(t) stays as registered; neither decides anything.

**Matched-block lengths (review finding 5).** A block is a maximal run of pairs consecutive on both
sides, re-derived from the pairs. Single shared tokens inside otherwise different text carry
null-level deviation and sit in seam bin 0. Registered: the pooled token count by block length in the
fixed bins {{{', '.join(BLOCK_BIN_LABELS)}}}, and f*(τ_K) over tokens in blocks of length ≥ **{int(cfg.rule['min_block_len'])}**
(`[e9.rule] min_block_len`), E9-same K and V, per handoff and pooled; NOT COMPUTABLE where a handoff has
no such token. Recomputed here from the raw traces over the {n_inc} included handoffs: {tot_tokens:,} matched tokens in
{blocks['n_blocks']:,} blocks -- {bins_line}; {blocks['tokens_ge_min']:,} tokens ({100 * blocks['tokens_ge_min'] / tot_tokens:.2f}%) in blocks ≥ {int(cfg.rule['min_block_len'])}.
`e9 --align-only` writes every alignment and `results/e9/align/coverage.json` (coverage, reasons,
keep draw, per-handoff block counts) before any prefill, with no gate and no upstream call; the driver
recomputes the same files and `summarize_e9` re-derives every alignment from the raw traces regardless.

**Interval on the median (review finding 6).** The rule reads the point median of f*(τ_K) over the
included handoffs. Beside it, a seeded percentile bootstrap of that median (`[e9.controls]`
`bootstrap_seed` = {int(cfg.controls['bootstrap_seed'])}, `bootstrap_reps` = {int(cfg.controls['bootstrap_reps'])}; 2.5 / 97.5 with the ONE pinned quantile convention,
`e7_stats.quantile`) is stated. Reported, never read: the band is the point median as 0023 wrote it.

**δ_null equal-token fraction (review finding 7).** The seeded derangement can pair a receiver position
with a sender position carrying the same token id; the fraction of such pairs is stated beside δ_null.

**Keep subset: n = {old_n} → {cfg.keep_n} (seed {cfg.keep_seed} unchanged).** 0019 retains a seeded subset of handoffs
with full dumps so a CPU summarizer can re-score from tensors; 0023 registers a `[STRETCH]` partial-
prefill experiment and the E-RL design a behavioral control of the same shape; both can only ever run
on retained dumps, the only tensors that survive the GPU day. Same seed, larger draw: `numpy` choice
without replacement is NOT nested across sizes, so this is a different set, not the old {old_n} plus {cfg.keep_n - old_n}.
Recomputed here: the n = {old_n} draw was {', '.join(f'`{short(h)}`' for h in old)} ({vol_old / 1e9:.1f} GB); the n = {cfg.keep_n} draw is
{new_lines}
{len(shared)} of the {old_n} carried over ({', '.join(f'`{short(h)}`' for h in shared) if shared else 'none'}). Retained volume {vol_new / 1e9:.1f} GB of fp16 stride-1 dumps
(three per handoff; {bpt_tgt:,} B per token on the receiver [{sh_tgt['n_layers']} × {sh_tgt['n_kv']} × {sh_tgt['d_h']} × 2 × 2 B], {bpt_src:,} B on the
source), against {vol_old / 1e9:.1f} GB before; the box needs that much free beside the transient dumps, and the sync
off the box scales with it. The GPU runbook's named keep handoffs, volumes, "68 handoffs" and "< 1 h"
predate this entry and are superseded by it and by the 09-02 pre-flight; the driver draws from config.

**Instrument and enforcement.** `config/e9.toml` carries every parameter above (`tau_ladder`,
`tau_agent_K`, `min_block_len`, `prefix_invariance_max_delta`, `bootstrap_seed`, `bootstrap_reps`, keep
`n`); `load_e9_config` refuses a config missing or malforming any of them; `e9.assert_ready` requires
THIS entry beside 0019 and 0023 (`REQUIRED_ENTRIES`), so no prefill can start on a ledger that lacks
it; the driver halts on the prefix control; `summarize_e9` states every quantity above in
`summary.json` / `summary.md` under lines that say DESCRIPTIVE or ALONGSIDE and refuses on any
disagreement with config, the calibration, the E7 report, or the per-token record. Tests: ladder and
agent-τ monotone, band unchanged; prefix control halts above tolerance and its record is refused when
tampered, absent, or over tolerance; b⁻ vs b on a seam after a token; block lengths re-derive
difflib's blocks; bootstrap seeded and nearest-rank; coverage comparison never invents a zero;
non-nesting of the keep draw pinned; malformed parameters refused.

**Scope.** All of 0019's and 0023's limits. No hypothesis cell changes with this entry; no
`verdict:` line. The verdict on H-E9 still enters only by its own numbered entry after the run.
The 0018 rows above are E7 figures and name the corpus manifest they were measured against (0024).
e7-manifest-sha256: {msha}
"""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--number", type=int, default=None, help="entry number (default: next free >= 25)")
    ap.add_argument("--preview", action="store_true", help="print the entry text; touch nothing")
    a = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    text = LEDGER.read_text(encoding="utf-8")
    entries = parse_ledger(text)["entries"]
    number = a.number or max(max(entries) + 1, 25)
    if f"### {number:04d} " not in e9.REQUIRED_ENTRIES:
        print(f"REFUSED: e9.REQUIRED_ENTRIES does not name {number:04d}; the gate and the entry must agree")
        return 2
    if not a.preview:
        if 24 not in entries:
            print("REFUSED: entry 0024 is not in the ledger; appends are sequential")
            return 2
        if number in entries:
            print(f"REFUSED: entry {number:04d} already exists; pass --number for the next free one")
            return 2
    cfg = load_e9_config(CONFIG, REPO_ROOT)          # validates every 0025 parameter
    e7 = load_e7_config(REPO_ROOT / "config" / "e7.toml", REPO_ROOT)
    if (cfg.results_dir / "report.json").exists() or (cfg.results_dir / "scores").exists():
        print("REFUSED: results/e9 already holds a report or scores -- a prefill has happened; 0023 forbids "
              "amending the rule section after the first score file")
        return 2
    prior = prior_config()
    if int(prior["keep"]["n"]) == cfg.keep_n:
        print(f"REFUSED: keep n in config/e9.toml ({cfg.keep_n}) equals the value at {PRIOR_CONFIG_REV}; nothing to register")
        return 2
    # the alongside tau re-derives from E8's report and the calibration file carries it
    e8_path = REPO_ROOT / "results" / "e8" / "report.json"
    cal_path = cfg.results_dir / "calibration" / "tau.json"
    if not e8_path.exists() or not cal_path.exists():
        print("REFUSED: results/e8/report.json and results/e9/calibration/tau.json must both exist (run "
              "`summarize_e9 --calibrate-tau` after this change)")
        return 2
    e8_agent_k = float(json.loads(e8_path.read_text(encoding="utf-8"))["per_k"][str(cfg.mapper_k)]["agent"]["K"])
    cal = json.loads(cal_path.read_text(encoding="utf-8"))["tau"]
    if "agent_K" not in cal or abs(cal["agent_K"] - (1.0 - e8_agent_k)) > _TOL or abs(float(cfg.rule["tau_agent_K"]) - (1.0 - e8_agent_k)) > _TOL:
        print("REFUSED: tau_agent_K in config / tau.json does not equal 1 - E8 arm (b) K R^2; rerun `summarize_e9 --calibrate-tau`")
        return 2
    # 0018's rows come from the E7 report, verified in-process first (fail-closed summarizer)
    summarize_e7(e7)
    e7_report = e7.results_dir / "skeleton_report.json"
    rows = json.loads(e7_report.read_text(encoding="utf-8"))["headroom"]["rows"]
    records, included, blocks, src, tgt = recon(cfg, e7)
    cov = coverage_comparison(records, rows, summary)
    if cov["included"] is None or cov["excluded_long"] is None:
        print("REFUSED: the coverage comparison needs both an included and an excluded-by-length group")
        return 2
    msha = manifest_sha256(manifest_path(e7))          # the committed corpus manifest the 0018 rows were measured against
    body = render(number, cfg, prior, records, included, blocks, src, tgt, cov, e8_agent_k, sha256_file_bytes(e7_report), msha)
    if a.preview:
        print(body)
        return 0
    entries_start = re.search(r"^## Entries\s*$", text, re.M).start()
    new = text.rstrip("\n") + "\n\n"
    chain = chain_hash(new, len(new), entries_start)
    new += body.rstrip("\n") + f"\n\nprior-entries-sha256: {chain}\n"
    LEDGER.write_text(new, encoding="utf-8", newline="\n")
    problems = check(new, committed_manifest_sha())
    if problems:
        LEDGER.write_text(text, encoding="utf-8", newline="\n")
        print("REFUSED after append (ledger restored):\n  " + "\n  ".join(problems))
        return 1
    print(f"appended entry {number:04d}; ledger_check ok. Commit the ledger alone, then retire this script.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

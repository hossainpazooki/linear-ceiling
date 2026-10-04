"""Append entry 0055 -- REGISTER, before any prefill, E-TRUNC: length isolation by HEAD truncation of the sender
context on entry 0036's 35 handoffs at four levels (FULL / S[-65536:] / S[-49152:] / S[-32768:]) under the same
YaRN receiver, scored by 0035's instrument unchanged, compared token by token on the subset matched under EVERY
level (M_cap). DESCRIPTIVE: no hypothesis row, no `verdict:` line, no cell moves. Answers reviewer weakness W2
("length is not isolated"; docs/2026-09-30-review-response-map.md).

The three rulings this entry carries (design docs/drafts/e-trunc-design.md section 10) were taken on 2026-10-04 by
the session under the operator's direction; RUNNING THIS SCRIPT IS THE OPERATOR'S RATIFICATION. Nothing is on the
ledger before that.

Ordering guard: 0054 present (the latest appended entry), 0055 absent; NUM is PROVISIONAL under docs/drafts/README.md
(0048-0053 are staged and may land first; then NUM/PREV and the four configs' [e9.gate] move together in one commit).
Refuses unless the four configs `config/e9t-{full,l65,l49,l32}.toml` are present at their registered (LF-normalized)
hashes and are config/e9l.toml's instrument on every field but the named lines; unless the four alignment passes
exist under their config shas (`e9 --align-only --config config/e9t-*.toml`, the only thing allowed under
results/e9t-*/ at registration, as 0035 and 0037 allowed theirs); and if any report, score, control, bridge, token
record or scratch dump exists under any level's results tree (R1). Every figure below is read from the configs, the
four coverage files, an IN-PROCESS `summarize_e9_trunc.shrinkage`, the two reference records
(`results/e9s/compare.json`, `results/e9l/summary.json`) by sha, the E9-long runbook or the ledger's own text located
by sentence; nothing is typed.

  --date YYYY-MM-DD   --preview   --repo-root <path> (dry-run against another checkout; default: this repository)
Runs `ledger_check` after appending. Delete once appended, chained to the append with `&&`.
"""
import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))
from linear_ceiling.config import load_e9_config                       # noqa: E402
from linear_ceiling.e9 import required_markers                          # noqa: E402
from linear_ceiling.hashing import sha256_text_file                     # noqa: E402  (LF-normalized: this checkout is CRLF)
from linear_ceiling.ledger_check import _ENTRIES_HEAD, chain_hash      # noqa: E402
from linear_ceiling.summarize_e9_trunc import FULL, _references, load_levels, shrinkage  # noqa: E402

NUM, PREV = "0055", "0054"
LONG_REG, LONG, SHORT_SCALED_REG, SHORT_SCALED, CORRECTIVE = "0035", "0036", "0037", "0038", "0045"
# The four configs as staged 2026-10-04 (LF-normalized sha256; config/e9l.toml byte-for-byte except the results and
# scratch dirs, [e9.gate], [e9.order] by, [e9.alignment] sender_head_truncate on the levels and [e9.trunc] on FULL).
CONFIGS = {
    "config/e9t-full.toml": "005d8d102deb743e2de66c62b884dfa5b602e3308a0e7960cc2260bb1de11f7f",
    "config/e9t-l65.toml": "782f7354f42207575d8719267eb12f1df231d5aeb39e2d577e976ffa57f1b239",
    "config/e9t-l49.toml": "d4d54381e3942b9effbac08554f24eab0eaa2122f3f81d07cb30bbe535140c4f",
    "config/e9t-l32.toml": "3c0663fbb651ad50e01389822263c67ae85bb78198d58aaf0333a3c6771dadaa",
}
# Quoted VERBATIM from docs/2026-10-01-run-queue-farhan.md section 10 (rulings 1, 3) and the 2026-10-04 seed's
# alternative (b) for ruling 2; a paraphrase of a ruling once made a builder build the opposite.
RULING_1 = "±0.005 absolute on the far-from-seam (16+) same-K *median*, as entry 0038 reports it"
RULING_2 = "an absolute floor (|M_∩| ≥ 2,000) beside the ratio"
RULING_2_CLAUSE = "the pooled |M_∩| / |M_FULL| stated in the entry regardless of the gate"
RULING_3 = "include it, keep R under YaRN, and state so"
RUNBOOK = "docs/2026-09-10-e9l-gpu-runbook.md"

ap = argparse.ArgumentParser()
ap.add_argument("--date", default=dt.date.today().isoformat())
ap.add_argument("--preview", action="store_true")
ap.add_argument("--repo-root", type=Path, default=REPO_ROOT)
a = ap.parse_args()
assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.date), "--date must be YYYY-MM-DD (the ledger heading's form)"
R = a.repo_root.resolve()

LEDGER = R / "ledger" / "ledger.md"
text = LEDGER.read_text(encoding="utf-8").replace("\r\n", "\n")
assert f"### {PREV} " in text and f"### {NUM} " not in text, f"ordering: {PREV} present, {NUM} absent"
lines = text.split("\n")


def _span(entry: str) -> tuple[int, int]:
    starts = [i for i, ln in enumerate(lines) if ln.startswith("### ")]
    head = next(i for i in starts if lines[i].startswith(f"### {entry} "))
    end = next((i for i in starts if i > head), len(lines))
    return head, end


def cite(entry: str, needle: str) -> int:
    """`entry:line` by sentence search inside the named entry (refuses on 0 or 2+ hits); never typed."""
    head, end = _span(entry)
    hits = [i + 1 for i in range(head, end) if needle in lines[i]]
    assert len(hits) == 1, f"{entry}: {needle!r} found {len(hits)} times, need exactly 1"
    return hits[0]


def entry_text(entry: str) -> str:
    head, end = _span(entry)
    return "\n".join(lines[head:end])


# --- the four configs, at their hashes, one instrument ----------------------------------------------------------
for rel, want in CONFIGS.items():
    p = R / rel
    assert p.exists(), f"{rel} missing"
    assert sha256_text_file(p) == want, f"{rel} is not the registered config (sha {sha256_text_file(p)[:12]} != {want[:12]})"
full = load_e9_config(R / "config" / "e9t-full.toml", R)
levels = load_levels(full, R)                   # refuses unless the levels are one instrument, L descending
e9l = load_e9_config(R / "config" / "e9l.toml", R)
for field in ("pair", "upstream_sha", "rule", "controls", "mapper_k", "mapper_space", "context_cap", "context_floor",
              "rope", "keep_seed", "keep_n", "bridge", "profiles", "alignment_method", "allow_partial"):
    assert getattr(full, field) == getattr(e9l, field), f"config/e9t-full.toml {field} is not config/e9l.toml's"
assert full.required_entries == e9l.required_entries + (NUM,), "the gate must be 0035's extended by this entry"
assert required_markers(full)[-1] == f"### {NUM} " and full.order_by == "n_sender_desc" and full.sender_head_truncate is None
Ls = [c.sender_head_truncate for n, c in levels.items() if n != FULL]
assert Ls == [65536, 49152, 32768], Ls
assert [Path(x).name for x in full.trunc["levels"]] == ["e9t-l65.toml", "e9t-l49.toml", "e9t-l32.toml"]
T = full.trunc
assert T["margin_abs"] == 0.005 and T["min_common_matched"] == 2000 and T["seam_far_bin"] == "16+", T
assert T["bootstrap_seed"] == 52 and T["bootstrap_reps"] == 2000
assert e9l.rope == {"rope_type": "yarn", "factor": 2.5, "original_max_position_embeddings": 32768}

# --- R1: nothing under this entry exists but the alignment passes ---------------------------------------------------
for name, cfg in levels.items():
    assert not (cfg.results_dir / "report.json").exists(), f"{cfg.results_dir}/report.json exists: a run happened before registration; refusing"
    for sub in ("scores", "controls", "bridge", "scratch", "tokens", "calibration", "recheck"):
        assert not (cfg.results_dir / sub).exists(), f"{cfg.results_dir}/{sub} exists: refusing"
    assert (cfg.results_dir / "align" / "coverage.json").exists(), \
        f"run `e9 --align-only --config {cfg.config_path.name}` first: every count below is read from the instrument"
out_dir = R / T["out_dir"]
stray = sorted(p.name for p in out_dir.iterdir()) if out_dir.exists() else []
assert set(stray) <= {"shrinkage.json", "shrinkage.md"}, f"{out_dir} holds {stray}; only the pre-check's outputs may exist"

# --- the figures: coverage, the pre-check (in-process), the references --------------------------------------------
covs = {name: json.loads((cfg.results_dir / "align" / "coverage.json").read_text(encoding="utf-8")) for name, cfg in levels.items()}
for name, cov in covs.items():
    assert cov["config_sha256"] == sha256_text_file(levels[name].config_path), f"{name}: coverage.json under another config"
    assert cov["context_cap"] == full.context_cap and cov["context_floor"] == full.context_floor and cov["rope"] == full.rope
    assert cov["order_by"] == "n_sender_desc" and cov["coverage"] == covs[FULL]["coverage"] and cov["keep_subset"] == covs[FULL]["keep_subset"]
    assert cov["run_order"] == covs[FULL]["run_order"], f"{name}: run order differs from FULL's (it reads the full |S|)"
cov = covs[FULL]
recs = {r["handoff_id"]: r for r in cov["alignments"]}
order = cov["run_order"]
included = sorted(h for h, r in recs.items() if not r["excluded"])
assert sorted(order) == included and len(order) == cov["coverage"]["included"] > 0
ns = {h: int(recs[h]["n_sender"]) for h in order}
assert all(ns[a_] >= ns[b_] for a_, b_ in zip(order, order[1:])), "run order must be |S| descending"
by_reason = {}
for h, r in recs.items():
    if r["excluded"]:
        by_reason.setdefault(r["reason"], []).append(h)
empty = sorted(by_reason.get("receiver prompt is empty in the trace", []))
above = sorted(h for reason, hs in by_reason.items() if "exceeds context cap" in reason for h in hs)
prior = sorted(by_reason.get(f"S and R within context floor {full.context_floor} (decided under the prior cap)", []))
assert len(empty) + len(above) + len(prior) == cov["coverage"]["excluded"], "an exclusion reason this entry does not name"
n_over = {L: sum(1 for h in order if ns[h] > L) for L in Ls}
sum_r = sum(int(recs[h]["n_receiver"]) for h in order)
budget = {name: 2 * sum(min(ns[h], c.sender_head_truncate or ns[h]) for h in order) + sum_r for name, c in levels.items()}
total_budget = sum(budget.values())
keep = cov["keep_subset"]
assert len(keep) == full.keep_n and set(keep) <= set(order)

shrink = shrinkage(levels)                      # CPU, from the four passes; refuses on any coverage/config disagreement
assert shrink["n_handoffs"] == len(order) and shrink["min_common_matched"] == T["min_common_matched"]
refs = _references(full, R)                     # 0038's and 0036's far-from-seam medians, by sha
short_lvl, long_lvl = refs["short_scaled"]["far_median"], refs["long"]["far_median"]
assert abs(long_lvl - short_lvl) > 2 * T["margin_abs"], "the two reference levels sit inside one margin of each other; the reading is undefined"
share = json.loads((R / T["short_scaled_compare"]).read_text(encoding="utf-8"))["configuration_share"]["seam_far"]

# --- the record this entry cites, located by sentence --------------------------------------------------------------
L_share = cite(SHORT_SCALED, "Far-from-seam (16+) median δ_K: native 0.0195")
L_both = cite(SHORT_SCALED_REG, "is therefore length AND")
L_never = cite("0025", "25 included of 68 observed")
m = re.search(r"Launched (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})Z, finished (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})Z", entry_text(LONG))
assert m, f"{LONG} does not state the launch and finish times"
t0, t1 = (dt.datetime.fromisoformat(s) for s in m.groups())
e9l_minutes = int(round((t1 - t0).total_seconds() / 60))
rb = (R / RUNBOOK).read_text(encoding="utf-8").replace("\r\n", "\n").split("\n")
peak_lines = [i + 1 for i, ln in enumerate(rb) if "**31.56 GiB**" in ln]
rate_lines = [i + 1 for i, ln in enumerate(rb) if "min per handoff" in ln]
assert len(peak_lines) == 1 and len(rate_lines) == 1, (peak_lines, rate_lines)
peak = re.search(r"\*\*(\d+\.\d+) GiB\*\*", rb[peak_lines[0] - 1]).group(1)
rate = re.search(r"(\d+(?:\.\d+)?[–-]\d+) min per handoff", rb[rate_lines[0] - 1]).group(1)

if not a.preview:
    for rel in (*CONFIGS, "ledger/ledger.md", "config/e9l.toml"):
        tracked = subprocess.run(["git", "ls-files", "--error-unmatch", "--", rel], cwd=R, capture_output=True)
        assert tracked.returncode == 0, f"{rel} is not tracked; registration requires committed inputs"
        clean = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", rel], cwd=R)
        assert clean.returncode == 0, f"{rel} differs from HEAD; commit it before registration"

sha12 = lambda s: s[:12]  # noqa: E731
names = lambda hs: "; ".join(f"`{h}`" for h in hs)      # noqa: E731
sr = shrink["ratio"]
fmt = lambda x: f"{x:.4f}"      # noqa: E731
lvl_line = " / ".join(f"{name} (L = {c.sender_head_truncate:,}: {n_over[c.sender_head_truncate]} of {len(order)} handoffs differ from FULL)"
                      for name, c in levels.items() if name != FULL)
ENTRY = f"""### {NUM} — {a.date} — E-TRUNC registered before any prefill: head truncation of the sender context on entry {LONG}'s 35 handoffs at four levels (FULL / 65,536 / 49,152 / 32,768) under the same YaRN receiver, compared on the subset matched under every level; shrinkage stated from the alignment passes; descriptive, no cell moves

**Why, and why now.** Reviewer weakness W2 (`docs/2026-09-30-review-response-map.md`): length is not isolated. The
record agrees — entry {SHORT_SCALED_REG} (line {L_both}) says every cross-cell "what length changes" figure is length AND
configuration, and entry {SHORT_SCALED} (line {L_share}) measured the configuration's share of the short→long far-from-seam gap
at {share:.4f} on identical tokens; the residual is unattributed because the short and long cohorts are different handoffs.
This entry registers the run that varies length WITHIN a handoff: under causal attention a matched token's reused
K/V depend only on the sender prefix before it, so TAIL truncation of S changes nothing and the length treatment is
HEAD truncation, S' = S[−L:], every matched token's K/V computed from a shorter causal prefix at sender position
p_S' = p_S − (|S| − L). `results/e9t-*/` hold no report, score, control, bridge, token record or dump at append, and
this script refuses otherwise (R1); the only things under them are the four alignment passes
(`e9 --align-only --config config/e9t-<level>.toml`; coverage sha256 FULL `{sha12(shrink['levels'][FULL]['coverage_sha256'])}`, L65
`{sha12(shrink['levels']['L65536']['coverage_sha256'])}`, L49 `{sha12(shrink['levels']['L49152']['coverage_sha256'])}`, L32 `{sha12(shrink['levels']['L32768']['coverage_sha256'])}`), from which every count below is read.

**Three rulings, 2026-10-04 (design `docs/drafts/e-trunc-design.md` §10; quoted verbatim).** (1) Margin and statistic
for the pre-registered reading: "{RULING_1}" (0038's levels {short_lvl:.4f} scaled-short, {long_lvl:.4f} long, READ from
`{T['short_scaled_compare']}` sha256 `{sha12(refs['short_scaled']['sha256'])}` and `{T['long_summary']}` sha256 `{sha12(refs['long']['sha256'])}`);
"unattributed" between the band and FULL's level. Why the median: {SHORT_SCALED} reports medians and the seam-bin means run
1.6–1.8× higher ({CORRECTIVE}). (2) Shrinkage gate: NOT the run queue's 0.80 ratio default but "{RULING_2}", taken as the void
gate, with "{RULING_2_CLAUSE}" — because the pre-check below shows the ratio default would void {shrink['n_below_0_80']} of {shrink['n_handoffs']}
handoffs. (3) The L32-native cell: "{RULING_3}". Scope check: entry 0025 (line {L_never}) and 0019 register the native cell's
exclusion rule as over-cap handoffs EXCLUDED and counted, never truncated, so a sender truncated into the native window
can never enter or speak to H-E9's verdict and the cell would be descriptive-only. It is **not in this entry**: the
driver applies one RoPE schedule to every dump of a handoff and the summarizer enforces per-role spec identity, so a
sender-native / receiver-scaled dump has no instrument yet; it enters, if at all, by its own pre-prefill amendment
after that instrument exists and is tested ({LONG_REG}'s precedent: the RoPE spec before the scaled receiver).

**Cells.** FULL = {LONG_REG}'s instrument on the same 35 handoffs (|S| {min(ns.values()):,}–{max(ns.values()):,}), re-run under this entry's gate
so every level's per-token record comes from one box and one pin — the control arm; {lvl_line}. Receiver and source
under {LONG}'s static YaRN `{json.dumps(full.rope, sort_keys=True)}` on every dump of every level, at the upstream pin
`{sha12(full.upstream_sha)}`; the n = 50 k = 1 mapper by sha for the cross arm. `config/e9t-{{full,l65,l49,l32}}.toml` are
`config/e9l.toml` byte-for-byte on the rule, τ, ladder, controls, seam bins, block floor, bootstrap, bridge, profiles,
keep draw, mapper and pin; they differ only in the results and scratch directories, `[e9.gate]` (ends at this entry),
`[e9.order] by = "n_sender_desc"`, `[e9.alignment] sender_head_truncate` on the three levels, and `[e9.trunc]` on FULL
(the levels, the floor, the margin, the two reference records, bootstrap seed {T['bootstrap_seed']} / {T['bootstrap_reps']} reps). Registered
hashes (LF-normalized): {"; ".join(f"`{Path(k).name}` `{sha12(v)}`" for k, v in CONFIGS.items())}. Inclusion is decided on the FULL
lengths before truncation, so every level keeps {LONG}'s set: **{cov['coverage']['observed']} observed · {len(order)} included · {len(prior)} excluded as decided
under the prior cap · {len(above)} excluded above the cap · {len(empty)} excluded for an empty receiver prompt**, the same eight by name as {LONG_REG}.
A handoff with |S| ≤ L is identical at that level and at FULL and still counts.

**The matched subset, and the shrinkage stated before any verdict (ruling 2).** Alignment is re-run per level because
the aligner sees S'. Tokens matched under EVERY level form M_∩, identified in the FULL frame as (p_S, p_R) after
undoing each level's offset |S| − L; δ is compared on M_∩ only. A handoff with **|M_∩| < {T['min_common_matched']:,}** is VOID for the
comparison and listed; |M_∩| / |M_FULL| is stated per handoff and pooled and gates nothing. **The CPU pre-check, from
the four alignment passes alone (`summarize_e9_trunc --shrinkage`, recomputed in-process by this script):** |M_∩| / |M_FULL|
per handoff median {fmt(sr['median'])} (p10 {fmt(sr['p10'])}, p90 {fmt(sr['p90'])}; min {fmt(sr['min'])}, max {fmt(sr['max'])}), pooled {fmt(shrink['pooled_ratio'])}
({shrink['n_common_total']:,} of {shrink['n_matched_full_total']:,} matched tokens); **{shrink['n_void']} of {shrink['n_handoffs']} handoffs are void under the floor** ({shrink['n_zero']} with
|M_∩| = 0), so **{shrink['n_handoffs'] - shrink['n_void']} handoffs enter the comparison**; {shrink['n_below_0_80']} sit below the 0.80 ratio the run queue proposed. The
loss is dominated by what the truncation REMOVES: the receiver's prompt re-renders EARLY sender content, and the
fraction of FULL pairs whose sender position survives S[−{min(Ls):,}:] has median {fmt(shrink['survivable_fraction']['median'])}; aligner re-matching
loses more than the removal on {shrink['n_with_rematching_loss_over_0_05']} handoffs (median loss beyond removal {fmt(shrink['rematching_loss']['median'])}, max
{fmt(shrink['rematching_loss']['max'])} of |M_FULL|) — the design's stated weak point, measured rather than assumed. Void:
{names(shrink['void'])}. Consequence stated now: "length" here means causal-prefix length on the tokens the receiver
re-renders from the LATE part of S, and M_∩ sits at late sender positions while the two reference medians were pooled
over full matched sets.

**Statistics (per handoff on M_∩, paired across levels; descriptive).** Per level: mean δ_K; the fraction of tokens
over τ_K = {float(full.rule['tau_K']):.4f}; f*(τ_K) and f* on the ladder ({", ".join(f"{float(t):.4g}" for t in full.rule['tau_ladder'])}) by 0023's MEAN-repair definition, oracle
lower bounds (0027); the far-from-seam ({T['seam_far_bin']}) pooled median AND mean δ_K in FULL's causal seam frame b⁻(t) (0025); the
paired (level − FULL) mean δ_K per handoff with its median over handoffs and a seeded percentile bootstrap (seed
{T['bootstrap_seed']}, {T['bootstrap_reps']} reps, `e7_stats.quantile`; reported, not read). V alongside, verdict-bearing for nothing. Each level is
also a complete {LONG_REG} run and is read by `summarize_e9` on its own (controls, bridge, profiles, band word stated
descriptively) before the comparison runs.

**The pre-registered reading (ruling 1).** If L32's far-from-seam ({T['seam_far_bin']}) pooled median δ_K on M_∩ over the non-void
handoffs lies within ±{T['margin_abs']} of {short_lvl:.4f} (the scaled-short level, the same receiver configuration), the residual
short↔long gap reads as **length**; within ±{T['margin_abs']} of {long_lvl:.4f} (the long level), as **the handoffs**; between,
**unattributed**, said so. FULL's own {T['seam_far_bin']} median on the same tokens is stated beside L32's. No hypothesis cell
moves either way; the comparison's figures enter by their own numbered entry and the paper only from that entry.

**Run order, stopping rule, resume.** Within each level the driver scores the included handoffs in the REGISTERED order
`n_sender_desc` (full |S| descending, ties by id): `{order[0].split('/')[-1]}` ({ns[order[0]]:,}) first, `{order[-1].split('/')[-1]}` ({ns[order[-1]]:,})
last, so the longest senders — the only ones the higher levels change — are scored first and a stopped level leaves
a named scored prefix. Controls run on the first handoff in that order at every level. `e9 --close-partial --config
config/e9t-<level>.toml` closes an unfinished level on a PREFIX of its order; the comparison is then defined on the
handoffs scored at EVERY level and the summarizer names the unscored per level. `--resume` after a crash keeps
hash-matching work. Keep subset per level: n = {full.keep_n}, seed {full.keep_seed}, the same draw as {LONG_REG}'s over the same ids
({names(keep)}); kept dumps per level, fingerprinted, re-scored at home under 0028's tolerance.

**Compute bound (R2 — a bound to be replaced by the probe on the granted card).** Prefill budget from the coverage:
FULL {budget[FULL]:,} tokens; {" / ".join(f"{n} {budget[n]:,}" for n in levels if n != FULL)}; total {total_budget:,} = {total_budget / budget[FULL]:.2f}× E9-long's. E9-long's
sitting scored its 35 at {rate} min per handoff (`{RUNBOOK}:{rate_lines[0]}`) in {e9l_minutes} minutes ({LONG}), with a measured peak
of {peak} GiB at |S| = {max(ns.values()):,} (`{RUNBOOK}:{peak_lines[0]}`); memory is bounded by FULL, so an L40S 48 GB fits every level,
and the four levels bound at {total_budget / budget[FULL]:.2f}× E9-long's wall time. The card is requested only after this entry is on the ledger.

**Gate and enforcement.** `e9 --check --config config/e9t-<level>.toml` refuses until entries {"/".join(full.required_entries)} are in
the committed ledger, that config is committed unmodified, the upstream is at the pin with every invoked path clean and
the mapper artifact is present by sha. `summarize_e9 --config config/e9t-<level>.toml` (fail-closed) reads each level
as it read {LONG}'s run, re-deriving every alignment from the raw traces under the truncation; `summarize_e9_trunc`
(fail-closed, the only reader of the comparison) runs those four first, then pairs the levels on M_∩, applies the
floor, states the shrinkage, the statistics and the reading, with every report, score, token record, coverage file
and reference record pinned by sha, and refuses on any disagreement — including a level run under another pin,
another config, or a different trace. Tests: `tests/test_e9_trunc.py` (the key, the exclusion decided on full lengths,
the match set shifted by exactly |S| − L and unchanged by a tail cut, the descending order) and
`tests/test_summarize_e9_trunc.py` (the four configs as one instrument, M_∩ in the FULL frame, the void gate, the
three outcomes of the reading, the pins).

**What this does NOT touch.** The H-E9, H-E9L and H-E9F cells; τ_K, τ_V, τ_agent_K, the rule, the band, the ladder;
entries {LONG}, {SHORT_SCALED} and {CORRECTIVE} and their records; `results/e9/`, `results/e9l/`, `results/e9s/`, `results/e9f*/`,
`results/e8*/`, `results/consolidation/`, `results/cache-behavior/`; `config/e9.toml`, `config/e9l.toml`,
`config/e9s.toml`; entries 0046–0049, the Llama long drafts (0050 / 0051), the second family's E8 amendment drafts
(0052 / 0053) and 0054. Nothing here is a figure of the run; the pre-check figures above are alignment counts, not
deviations.

**Scope.** One pair (Qwen3-0.6B → 1.7B), one direction, one agent family, the long half of one corpus under a scaled
receiver (the bridge control runs at every level as {LONG_REG} registered it); "length" = causal-prefix length of the
reused K/V on the late-S tokens the receiver re-renders, not the number of turns; the {len(above)} handoffs above
{full.context_cap:,} and the {len(empty)} with an empty receiver prompt stay excluded; the comparison is read on the handoffs that keep at least {T['min_common_matched']:,} common matched tokens
({shrink['n_handoffs'] - shrink['n_void']} of {shrink['n_handoffs']} at the pre-check; the {shrink['n_void']} void handoffs are named, never pooled, and are a LIMITATION the
paper states: the result speaks for the handoffs whose receiver re-renders enough of the late sender context to survive truncation,
not for all 35); the L32-native cell is deferred, so nothing here compares native with YaRN on the same tokens, a second
stated LIMITATION (W6's bridge stays the only native-vs-YaRN evidence); f* stays an oracle lower bound; generation quality after reuse not
measured.

prior-entries-sha256: PLACEHOLDER
"""
assert "\nverdict:" not in ENTRY, "a registration entry carries no verdict line"

if a.preview:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(ENTRY)
    raise SystemExit(0)
new = text + ("" if text.endswith("\n") else "\n") + "\n" + ENTRY
head = _ENTRIES_HEAD.search(new)
digest = chain_hash(new, new.index(f"### {NUM} "), head.start())
new = new.replace("prior-entries-sha256: PLACEHOLDER", f"prior-entries-sha256: {digest}")
LEDGER.write_text(new, encoding="utf-8", newline="\n")
print(f"appended {NUM}; chain {digest[:12]}")
r = subprocess.run([sys.executable, "-m", "linear_ceiling.ledger_check"], cwd=R, capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip())
raise SystemExit(r.returncode)

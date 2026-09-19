"""Append entry 0041 -- the E9 SHORT cell of the second model family, registered BEFORE any prefill, with
ONE new hypothesis row (H-E9F, `unresolved`). This is the only verdict-bearing cell of the Llama campaign:
the same experiment as H-E9, on a second pair, under 0023's rule with tau recalibrated on THIS pair's own
k = 1 mapper.

Ordering guard: 0040 present, 0041 absent, and no H-E9F row in the table yet. Nothing under this entry may
exist yet: `results/e9f/` holds no report and no score file (R1). What MUST exist: `config/e9f.toml`
CALIBRATED (the three pair-calibrated tau fields carry real numbers, so the file loads at all) and
committed; the absolute tau ladder and prefix-invariance bound remain the literals entry 0039 registered;
`results/e9f/calibration/tau.json` from `summarize_e9 --calibrate-tau --config config/e9f.toml
--e8-report results/e8f/report.json`, agreeing with the config and with entry 0040's report -- this is
checked HERE, at registration, because `e9 --check` never looks for it and a 2026-09-14 sitting ran 25
handoffs and was refused afterwards for exactly that gap; `results/e9f/align/coverage.json` from
`e9 --align-only --config config/e9f.toml`, written under this exact config sha; and the upstream HEAD at
the pin, clean. Every number below is read from the config, that coverage file, the calibration record or
entry 0040's verified E8 report; nothing is typed.

  --date <YYYY-MM-DD>   (defaults to today; the entry is dated the day it is appended)
  --preview             (print the row and the entry, do not append)

Runs `ledger_check` after appending. Delete once appended, chained to the append with `&&`."""
import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

from linear_ceiling import REPO_ROOT
from linear_ceiling.config import load_e8_config, load_e9_config
from linear_ceiling.e9 import UPSTREAM_PATHS, _PENDING, required_markers
from linear_ceiling.e9_pertoken import SEAM_BIN_EDGES
from linear_ceiling.hashing import sha256_file_bytes, sha256_text_file
from linear_ceiling.ledger_check import _ENTRIES_HEAD, chain_hash
from linear_ceiling.pairs import pair_models

NUM, PREV = "0041", "0040"
FAMILY = f"{int(NUM) - 2:04d}"      # the family registration entry (0039 as staged); shifts with NUM
TAU_TOL = 1e-9
BOX_R2_TOL = 1e-6                    # OPERATIONAL, not registered. 0028 fixes 1e-05/1e-02 for the
                                     # keep-subset PER-TOKEN re-score, a different comparison; no entry
                                     # fixes a tolerance for a scorer-level held-out R^2 across machines.
ap = argparse.ArgumentParser()
ap.add_argument("--date", default=dt.date.today().isoformat())
ap.add_argument("--preview", action="store_true")
a = ap.parse_args()
assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.date), "--date must be YYYY-MM-DD (the ledger heading's form)"

LEDGER = REPO_ROOT / "ledger" / "ledger.md"
text = LEDGER.read_text(encoding="utf-8").replace("\r\n", "\n")
assert f"### {PREV} " in text and f"### {NUM} " not in text, f"ordering: {PREV} present, {NUM} absent"
assert "| H-E9F |" not in text, "H-E9F row already in the table"

cfg = load_e9_config(REPO_ROOT / "config" / "e9f.toml", REPO_ROOT)   # refuses while any tau key is a marker
e9 = load_e9_config(REPO_ROOT / "config" / "e9.toml", REPO_ROOT)
e8f = load_e8_config(REPO_ROOT / "config" / "e8f.toml", REPO_ROOT)
src_id, tgt_id = pair_models(cfg.pair)
assert cfg.pair == e8f.pair and cfg.upstream_sha == e8f.upstream_sha, "the E9 and E8 cells of one family share a pair and a pin"
assert cfg.mapper_k == e8f.verdict_k, "the E9 mapper k must be the k E8 registered as verdict-bearing"

# The instrument is 0023/0025/0027's. Exactly three tau fields are recalibrated on this pair; entry
# 0039 registered the ladder and prefix-invariance bound as absolute literals identical to E9's.
PAIR_CALIBRATED = ("tau_K", "tau_V", "tau_agent_K")
assert set(cfg.rule) == set(e9.rule) and set(cfg.controls) == set(e9.controls), "the rule/controls key sets must be E9's"
for key, mine in cfg.rule.items():
    if key not in PAIR_CALIBRATED:
        assert mine == e9.rule[key], f"[e9.rule] {key} is {mine!r}, not config/e9.toml's {e9.rule[key]!r}"
for key, mine in cfg.controls.items():
    assert mine == e9.controls[key], f"[e9.controls] {key} is {mine!r}, not config/e9.toml's {e9.controls[key]!r}"
assert cfg.rule["tau_ladder"] == e9.rule["tau_ladder"], \
    "tau_ladder is not the absolute literal entry 0039 registered from config/e9.toml"
assert cfg.controls["prefix_invariance_max_delta"] == e9.controls["prefix_invariance_max_delta"], \
    "prefix_invariance_max_delta is not the absolute literal entry 0039 registered from config/e9.toml"
assert list(cfg.controls["seam_bins"]) == list(SEAM_BIN_EDGES), "seam_bins differ from the registered edges (0023)"
assert cfg.context_cap == e9.context_cap and cfg.context_floor == 0, "the short cell registers 0029's numeric cap and no floor"
assert cfg.rope is None and cfg.bridge is None and cfg.profiles is None, "a natively long receiver registers no rope, no bridge"
assert cfg.keep_n == e9.keep_n, "the keep draw size is 0025's"
assert required_markers(cfg)[-1] == f"### {NUM} ", "config/e9f.toml's [e9.gate] does not end at this entry"
assert cfg.e8_report is not None and Path(cfg.e8_report).resolve() == (e8f.results_dir / "report.json").resolve(), \
    "[e9] e8_report must name THIS family's E8 report; unset, the summarizer would calibrate against Qwen's"

# tau: 1 - this pair's own held-out R^2, cross-checked three ways before the row is written.
e8_rep = json.loads(cfg.e8_report.read_text(encoding="utf-8"))
assert e8_rep["pair"] == cfg.pair, "the registered E8 report is for another pair"
kv = str(e8f.verdict_k)
box_tau = {"tau_K": 1.0 - float(e8_rep["per_k"][kv]["generic"]["K"]),
           "tau_V": 1.0 - float(e8_rep["per_k"][kv]["generic"]["V"]),
           "tau_agent_K": 1.0 - float(e8_rep["per_k"][kv]["agent"]["K"])}
# K/V in the E8 report were reduced on the GPU box. The config deliberately takes the HOME re-score
# emitted by tools/emit_tau.py. 1e-6 is this script's operational bound, NOT an entry's: 0028
# registers 1e-05/1e-02 for the keep-subset per-token re-score only. The
# calibration record below is another home re-score and must agree with the config at the tighter 1e-9.
for key in ("tau_K", "tau_V"):
    v = box_tau[key]
    assert abs(float(cfg.rule[key]) - v) <= BOX_R2_TOL * max(1.0, abs(v)), \
        (f"[e9.rule] {key} = {cfg.rule[key]} differs from the box E8 figure ({v}) beyond the registered "
         f"cross-platform tolerance {BOX_R2_TOL:g}")
# Arm (b) has no separate home re-score: tau_agent_K remains derived directly from the verified E8 report.
v = box_tau["tau_agent_K"]
assert abs(float(cfg.rule["tau_agent_K"]) - v) <= TAU_TOL * max(1.0, abs(v)), \
    f"[e9.rule] tau_agent_K = {cfg.rule['tau_agent_K']} is not 1 - this pair's E8 arm (b) K figure ({v})"
cal_path = cfg.results_dir / "calibration" / "tau.json"
assert cal_path.exists(), ("run `summarize_e9 --calibrate-tau --config config/e9f.toml --e8-report "
                           f"{cfg.e8_report}` BEFORE registering: `e9 --check` never looks for it, and a run that "
                           "reaches the summarizer without it is refused after the box is gone (learnings 2026-09-14)")
cal = json.loads(cal_path.read_text(encoding="utf-8"))
assert cal["pair"] == cfg.pair and cal["e8_report_sha256"] == sha256_file_bytes(cfg.e8_report), \
    "the calibration record is for another pair or another E8 report"
assert cal["mapper"]["k"] == cfg.mapper_k and all(cal["generic_dumps_match_e8_fingerprints"].values())
for key in ("K", "V"):
    assert abs(cal["tau"][key] - float(cfg.rule[f"tau_{key}"])) <= TAU_TOL * max(1.0, abs(cal["tau"][key])), \
        f"tau_{key}: the calibration record and config/e9f.toml disagree"
assert abs(cal["tau"]["agent_K"] - float(cfg.rule["tau_agent_K"])) <= TAU_TOL * max(1.0, abs(cal["tau"]["agent_K"]))

# R1: nothing under this entry exists yet.
assert not (cfg.results_dir / "report.json").exists(), f"{cfg.results_dir}/report.json exists: a run happened before registration; refusing"
for sub in ("scores", "controls", "bridge", "scratch"):
    assert not (cfg.results_dir / sub).exists(), f"{cfg.results_dir}/{sub} exists: refusing"

cov_path = cfg.results_dir / "align" / "coverage.json"
assert cov_path.exists(), "run `e9 --align-only --config config/e9f.toml` first: the coverage this entry states comes from the instrument"
cov = json.loads(cov_path.read_text(encoding="utf-8"))
assert cov["config_sha256"] == sha256_text_file(cfg.config_path), "coverage.json was written under another config/e9f.toml"
assert cov["context_cap"] == cfg.context_cap and cov["context_floor"] == 0 and cov["rope"] is None
recs = {r["handoff_id"]: r for r in cov["alignments"]}
order = cov["run_order"]
included = sorted(h for h, r in recs.items() if not r["excluded"])
assert sorted(order) == included and len(order) == cov["coverage"]["included"] > 0, "run order must cover exactly the included set"
assert all(int(recs[h]["n_matched"]) >= 1 for h in order), \
    "an included handoff has no matched positions, so score_positions cannot run"
assert int(recs[order[0]]["n_matched"]) >= 2, \
    "the first run-order handoff has fewer than two matched positions, so the null control cannot run"
keep = cov["keep_subset"]
assert len(keep) == cfg.keep_n and set(keep) <= set(order)
by_reason = {}
for h, r in recs.items():
    if r["excluded"]:
        by_reason.setdefault(r["reason"], []).append(h)
empty = sorted(by_reason.get("receiver prompt is empty in the trace", []))
over = sorted(h for reason, hs in by_reason.items() if "exceeds context cap" in reason for h in hs)
assert len(empty) + len(over) == cov["coverage"]["excluded"], "an exclusion reason this entry does not name"
sum_s = sum(recs[h]["n_sender"] for h in order)
sum_r = sum(recs[h]["n_receiver"] for h in order)
ns = sorted(recs[h]["n_sender"] for h in order)

# The Qwen short cell, for the "never pooled" clause -- read from ITS report, not remembered.
prior = json.loads((e9.results_dir / "report.json").read_text(encoding="utf-8"))
assert prior.get("complete"), "results/e9/report.json is not a complete run"
n_prior = prior["coverage"]["included"]

if not a.preview:
    # Registration claims both the calibrated config and its predecessor ledger state are committed.
    # Check that claim BEFORE this script mutates the ledger; a later E9 gate refusing is too late.
    for rel in (cfg.config_path.resolve().relative_to(REPO_ROOT.resolve()).as_posix(), "ledger/ledger.md"):
        tracked = subprocess.run(["git", "ls-files", "--error-unmatch", rel], cwd=REPO_ROOT,
                                 capture_output=True)
        clean = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", rel], cwd=REPO_ROOT)
        assert tracked.returncode == 0 and clean.returncode == 0, \
            f"{rel} is not tracked and committed unmodified at HEAD; refusing to register over a working-tree state"
    assert _PENDING not in cfg.upstream_sha and re.fullmatch(r"[0-9a-f]{40}", cfg.upstream_sha), \
        "config/e9f.toml still carries the pending upstream pin placeholder"
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=cfg.upstream_path, capture_output=True, text=True).stdout.strip()
    assert head == cfg.upstream_sha, f"upstream HEAD {head[:12]} != the pin {cfg.upstream_sha[:12]}"
    dirty = subprocess.run(["git", "status", "--porcelain", "--", *UPSTREAM_PATHS], cwd=cfg.upstream_path,
                           capture_output=True, text=True).stdout.strip()
    assert not dirty, f"upstream invoked paths are dirty at the pin:\n{dirty}"

tau_K, tau_V, tau_agent = float(cfg.rule["tau_K"]), float(cfg.rule["tau_V"]), float(cfg.rule["tau_agent_K"])
ladder = ", ".join(f"{float(t):.4g}" for t in cfg.rule["tau_ladder"])
names = lambda hs: "; ".join(f"`{h}`" for h in hs)      # noqa: E731
gates = "/".join(cfg.required_entries)
heldout = cal["heldout"]

ROW = (f"| H-E9F | (E9's claim on a second model family) at a re-rendered handoff whose sender and receiver prompts both "
       f"fit {cfg.context_cap:,} tokens under the pair's own tokenizer, same-model KV agreement on content-matched tokens "
       f"retains the transfer-relevant fidelity on {src_id} → {tgt_id} — a matched-KV cross-release pair with a natively "
       f"long receiver, neither side scaled. Rule verbatim from entry 0023: median over the included handoffs of the oracle "
       f"selective-recompute fraction f*(τ_K = {tau_K:.4f}) on the K read-out, HOLDS ≤ {cfg.rule['holds_max']} / "
       f"DEGRADES ≥ {cfg.rule['degrades_min']:.2f} / UNRESOLVED between; τ_K is 1 − THIS pair's own k = {cfg.mapper_k} "
       f"held-out R² (entry {PREV}) and is never Qwen's; decided on this pair's {len(order)} included handoffs only, never "
       f"pooled with entry 0029's {n_prior} — the same numeric cap over a different tokenizer is a different set of "
       f"handoffs; read on a floor (0027). Registered by entry {NUM} before any prefill. | E9-family (entry {NUM}) | unresolved |")

ENTRY = f"""### {NUM} — {a.date} — E9 short cell registered before any prefill on the second model family: H-E9's instrument on {src_id} → {tgt_id}; H-E9F added `unresolved`; τ recalibrated on this pair's own k = {cfg.mapper_k} mapper

**Why, and why now.** H-E9 `HELD` (0029) and H-E9L `HELD` (0036) are claims about one pair. Entry {PREV}
has just run E8 on a second family and produced the one thing a second E9 cell needs: this pair's own
mapper and its own held-out R². This entry registers the cell BEFORE any prefill: `results/e9f/` holds no
report and no score file at append, and the script refuses otherwise (R1). The only things under it are
the instrument's own alignment pass (`e9 --align-only --config config/e9f.toml`, `align/coverage.json`
sha256 `{sha256_file_bytes(cov_path)[:12]}`) and the τ calibration (`summarize_e9 --calibrate-tau`,
`calibration/tau.json` sha256 `{sha256_file_bytes(cal_path)[:12]}`), both checked here against the
committed config. **This is the one verdict-bearing cell of the Llama campaign**: the family registration
({FAMILY}) and the long half are descriptive, and exactly one hypothesis row is added.

**Hypothesis H-E9F (row added to the table, `unresolved`).** The statement is H-E9's on a second model
family; the rule is 0023's verbatim, with only τ recalibrated. Per matched token the centered deviation in
R²'s units between the receiver's own K at the sender position and at the re-rendered position; a token
needs recompute when it exceeds **τ_K = {tau_K:.4f}**; the verdict statistic is the median over included
handoffs of the oracle selective-recompute fraction f*(τ_K) on the K read-out; **HOLDS ≤
{cfg.rule['holds_max']} / DEGRADES ≥ {cfg.rule['degrades_min']:.2f} / UNRESOLVED between**. τ_V =
{tau_V:.4f}, τ_agent_K = {tau_agent:.4f} (alongside, verdict-bearing for nothing), the τ ladder ({ladder}),
the seam bins, the block floor ({cfg.rule['min_block_len']}) and the bootstrap (seed
{cfg.controls['bootstrap_seed']}, {cfg.controls['bootstrap_reps']} reps) are 0025's, unchanged. f* stays an
oracle LOWER BOUND read on a floor (0027).

**τ is this pair's, and the ordering it must satisfy.** τ_K = 1 − {heldout['K_r2_layer_mean']:.4f} =
{tau_K:.4f} and τ_V = 1 − {heldout['V_r2_layer_mean']:.4f} = {tau_V:.4f}, the k = {cfg.mapper_k} mapper's held-out R² over
{heldout['n_tokens']:,} tokens ({heldout['definition']}), recomputed by `summarize_e9 --calibrate-tau`
from the archived mapper (`mappers/{cfg.pair}/k{cfg.mapper_k}`, json
{cal['mapper']['json_sha256'][:12]}) against the archived `r2.json`
({cal['archived_r2_sha256'][:12]}) and entry {PREV}'s E8 report
({cal['e8_report_sha256'][:12]}); τ_agent_K = 1 − that mapper's agent-arm R² (0025's alongside
tolerance). `config.py` refuses any cell whose τ_K is outside (0, 1), whose ladder leaves (0, τ_K) or is
not strictly decreasing, or whose τ_agent_K is outside (τ_K, 1) — so none of the three calibrated
tolerances could have been carried over from the Qwen cells, and none was. The ladder and prefix bound are
instead the exact absolute literals entry {FAMILY} registered, deliberately identical across families.
The summarizer recomputes the three calibrated tolerances and refuses on any disagreement with this file.
**No figure from this cell is ever pooled with a Qwen figure.**

**The verdict set, and why it is not 0029's.** `context_cap = {cfg.context_cap:,}` is the same NUMERIC
threshold entry 0029 registered, and that is all it shares: it is a registered length threshold in this
pair's own tokens, not a hardware bound (both models are natively long), and `e9_align` measures |S| and
|R| under the pair's own tokenizer, so the Llama-3 BPE re-partitions the handoff set. Coverage from the
alignment pass: **{cov['coverage']['observed']} observed · {len(order)} included · {len(over)} excluded
above the cap · {len(empty)} excluded for an empty receiver prompt**. Included |S| runs {ns[0]:,} to
{ns[-1]:,}; the prefill budget is {sum_s:,} sender tokens (both models) + {sum_r:,} receiver tokens =
{2 * sum_s + sum_r:,} tokens. The {len(over)} above the cap are not lost: the long half of this family
(its own later entry) takes those within its own cap and names the residual above it. H-E9F is a claim
about these {len(order)} handoffs; coverage travels with every figure (0032's clause, kept).

**The receiver is NATIVE, and nothing is scaled.** There is no `[e9.rope]` and therefore no `[e9.bridge]`:
the receiver's own checkpoint declares a window that already covers this cap, so there is no scaled arm to
compare and entry 0035's control 4 does not apply here. What replaces it is read off the dumps themselves
(upstream `kvt/data.py` writes each dump's `RopeSpec` — the `inv_freq` and attention factor of the loaded
model's own rotary embedding — halt-checked against the model at every dumped position, and
`linear_ceiling.e9.dump_rope_meta` keeps that record beside every dump's fingerprint BEFORE the non-kept
dumps are deleted): **(i) native window** — the registered cap must be ≤ every dump's recorded
`max_position_embeddings`, the positive statement that no extrapolation happened; **(ii) frequency
identity** — the recorded spec must be identical across every dump OF THE SAME MODEL ROLE. (ii) is
role-scoped and must be: this pair's two sides carry different llama3 scaling factors and build different
inverse-frequency vectors by construction, so an unscoped equality assert would refuse every CORRECT run.
Both are asserted by `summarize_e9`, which also refuses a dump recording an attention factor other than
1.0 — the only positive evidence that the box applied no scaling the registration does not describe.

**Run order, keep subset, controls.** The driver scores the included handoffs in `{cfg.order_by}` order;
the controls run on the first handoff in that order. Keep subset: n = {cfg.keep_n}, seed {cfg.keep_seed},
a fresh draw from THIS cell's sorted included ids (numpy `choice` without replacement is not nested with
0025's draw, so it is not a subset of anything): {names(keep)}. Their three stride-1 dumps are retained,
fingerprinted, pulled home and re-scored from tensors by the summarizer under 0028's tolerance. Controls
(1–3 as 0023/0025; 6 as 0025): (1) pipeline identity HALT (a dump scored against itself, every square
exactly zero); (2) prefix-invariance HALT on the first handoff in run order, max centered δ ≤
{float(cfg.controls['prefix_invariance_max_delta']):.0e} — entry {FAMILY}'s pre-registered absolute
float32 kernel-noise bound, explicitly held identical across families and not derived from τ_K; (3) δ_null,
seeded derangement of sender positions (seed {cfg.controls['null_seed']}); (6) seam profiles b(t) and
b⁻(t), same bins. The cross arm runs through this pair's own k = {cfg.mapper_k} mapper by sha, and its
outcome is descriptive and decides nothing (0027).

**Gate and enforcement.** `e9 --check --config config/e9f.toml` refuses until entries {gates} are in the
committed ledger, `config/e9f.toml` is committed unmodified, the upstream is at the pin
`{cfg.upstream_sha[:12]}` with every invoked path clean, and the mapper artifact is present by sha.
`summarize_e9 --config config/e9f.toml` (fail-closed, the only reader) re-derives every alignment from the
raw traces under the cap, recomputes every figure, re-scores the kept dumps from tensors, recomputes τ and
refuses on disagreement with this config, checks the controls and the two RoPE controls above, and states
f*, the profiles and the band. **The τ calibration is checked at THIS entry, not only by the summarizer:**
`e9 --check` does not look for `calibration/tau.json`, and on 2026-09-14 a sitting printed ready, ran to
completion and was refused at home for exactly that gap (learnings). The record exists and agrees before
this row is written.

**What this does NOT touch.** The H-E8, H-E9 and H-E9L cells; the Qwen τ values, rule, band, ladder, keep
subsets and results directories; `config/e9.toml`, `config/e9l.toml`, `config/e9s.toml`, `config/e9c.toml`
and every `config/e8*.toml` but this family's. Nothing here is a figure: H-E9F's verdict and every number
enter by their own numbered entry, and the paper only from that entry.

**Scope.** One new pair ({src_id} → {tgt_id}), one direction, one agent family, the short half of one
corpus under a natively long receiver; off-policy text for Llama-3 (entry {PREV}); floor not method
(0027); the {len(over)} handoffs above the cap and the {len(empty)} with an empty receiver prompt stay
excluded and counted; generation quality after reuse not measured. `eval_hellaswag.py` and
`compose_mapper.py` remain out of scope for this pair (upstream `apply_mapper` re-applies with a plain θ).

prior-entries-sha256: PLACEHOLDER
"""

if a.preview:
    print(ROW)
    print()
    print(ENTRY)
    raise SystemExit(0)

anchor = "| H-E9L | "
i = text.index(anchor)
row_end = text.index("\n", i) + 1
new = text[:row_end] + ROW + "\n" + text[row_end:]
new = new + ("" if new.endswith("\n") else "\n") + "\n" + ENTRY
head = _ENTRIES_HEAD.search(new)
digest = chain_hash(new, new.index(f"### {NUM} "), head.start())
new = new.replace("prior-entries-sha256: PLACEHOLDER", f"prior-entries-sha256: {digest}")
LEDGER.write_text(new, encoding="utf-8", newline="\n")
print(f"appended {NUM} (+ H-E9F row); chain", digest[:12])
r = subprocess.run([sys.executable, "-m", "linear_ceiling.ledger_check"], cwd=REPO_ROOT, capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip())
raise SystemExit(r.returncode)

"""Append entry 0044 -- the E9 LONG half of the second model family, registered BEFORE any prefill, at a
NATIVE receiver. DESCRIPTIVE: no hypothesis row, no `verdict:` line, no cell moves. It declares entry
0035's D1(a) receiver scaling, its configuration bridge (control 4) and its scaled-receiver reading
INAPPLICABLE here, and states that this cell cannot move, support or refute H-E9L and is never pooled with
entry 0036's handoffs.

Ordering guard: 0043 present, 0044 absent. Nothing under this entry may exist yet: `results/e9fl/` holds no
report and no score file (R1). What MUST exist: `config/e9fl.toml` CALIBRATED against THIS pair's own E8
report and committed; `results/e9fl/calibration/tau.json` (checked here, at registration -- `e9 --check`
never looks for it); `results/e9fl/align/coverage.json` from `e9 --align-only --config config/e9fl.toml`,
written under this exact config sha; the SHORT cell's completed run, whose included set this cell's floor
must exclude EXACTLY (the partition is checked, not asserted in prose); and the upstream HEAD at the pin,
clean. Every number below is read from the config, that coverage file, the calibration record or the short
cell's report; nothing is typed.

  --date <YYYY-MM-DD>   (defaults to today; the entry is dated the day it is appended)
  --preview             (print, do not append)

Runs `ledger_check` after appending. Delete once appended, chained to the append with `&&`."""
import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

from linear_ceiling.config import load_e8_config, load_e9_config
from linear_ceiling import REPO_ROOT
from linear_ceiling.e9 import UPSTREAM_PATHS, _PENDING, required_markers
from linear_ceiling.e9_pertoken import SEAM_BIN_EDGES
from linear_ceiling.hashing import sha256_file_bytes, sha256_text_file
from linear_ceiling.ledger_check import _ENTRIES_HEAD, chain_hash
from linear_ceiling.pairs import pair_models

NUM, PREV = "0044", "0043"
FAMILY = f"{int(NUM) - 4:04d}"      # the family registration entry (0039 as staged); shifts with NUM
SHORT = f"{int(NUM) - 2:04d}"       # the short cell's registration entry (0042 as staged)
CONFIG_TAU_TOL = 1e-9                # config and home calibration are the registered authority
BOX_TAU_TOL = 1e-6                   # the E8 box report may differ by registered cross-platform arithmetic
ap = argparse.ArgumentParser()
ap.add_argument("--date", default=dt.date.today().isoformat())
ap.add_argument("--preview", action="store_true")
a = ap.parse_args()
assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.date), "--date must be YYYY-MM-DD (the ledger heading's form)"

LEDGER = REPO_ROOT / "ledger" / "ledger.md"
text = LEDGER.read_text(encoding="utf-8").replace("\r\n", "\n")
assert f"### {PREV} " in text and f"### {NUM} " not in text, f"ordering: {PREV} present, {NUM} absent"

cfg = load_e9_config(REPO_ROOT / "config" / "e9fl.toml", REPO_ROOT)   # refuses while any tau key is a marker
short = load_e9_config(REPO_ROOT / "config" / "e9f.toml", REPO_ROOT)
e9 = load_e9_config(REPO_ROOT / "config" / "e9.toml", REPO_ROOT)
e9l = load_e9_config(REPO_ROOT / "config" / "e9l.toml", REPO_ROOT)
e8f = load_e8_config(REPO_ROOT / "config" / "e8f.toml", REPO_ROOT)
src_id, tgt_id = pair_models(cfg.pair)
assert cfg.pair == short.pair == e8f.pair and cfg.upstream_sha == short.upstream_sha == e8f.upstream_sha, \
    "the three cells of one family share a pair and a pin"

# The instrument is 0023/0025/0027's. Only the three calibrated tau fields are this pair's own;
# the absolute ladder and prefix-invariance delta were registered as literals equal to config/e9.toml's.
PAIR_CALIBRATED_TAU = ("tau_K", "tau_V", "tau_agent_K")
assert set(cfg.rule) == set(e9.rule) and set(cfg.controls) == set(e9.controls), "the rule/controls key sets must be E9's"
for key, mine in cfg.rule.items():
    if key not in PAIR_CALIBRATED_TAU:
        assert mine == e9.rule[key], f"[e9.rule] {key} is {mine!r}, not config/e9.toml's {e9.rule[key]!r}"
for key, mine in cfg.controls.items():
    assert mine == e9.controls[key], f"[e9.controls] {key} is {mine!r}, not config/e9.toml's {e9.controls[key]!r}"
assert list(cfg.controls["seam_bins"]) == list(SEAM_BIN_EDGES), "seam_bins differ from the registered edges (0023)"
for key in ("tau_K", "tau_V", "tau_agent_K"):
    assert float(cfg.rule[key]) == float(short.rule[key]), \
        f"the two cells of one family must carry the SAME {key}: it is 1 - one mapper's held-out R^2"
# The receiver is native and the bridge is inapplicable, not merely omitted.
assert cfg.rope is None and cfg.bridge is None, \
    "this cell registers no [e9.rope] and no [e9.bridge]: the receiver is natively long and has no scaled arm"
assert e9l.rope is not None and e9l.bridge is not None, \
    "config/e9l.toml no longer carries the scaled receiver and bridge this entry declares inapplicable"
# The partition against the short cell.
assert cfg.context_floor == short.context_cap, \
    f"the long floor {cfg.context_floor} must equal the short cap {short.context_cap}, or the two cells do not partition"
assert cfg.context_cap > cfg.context_floor and cfg.allow_partial and cfg.order_by == "n_sender_asc"
assert cfg.profiles and set(cfg.profiles) == {"s_len_edges", "s_pos_edges"}
assert required_markers(cfg)[-1] == f"### {NUM} ", "config/e9fl.toml's [e9.gate] does not end at this entry"
assert cfg.e8_report is not None and Path(cfg.e8_report).resolve() == (e8f.results_dir / "report.json").resolve()

# Tau: the home calibration is authoritative for K/V. The box-written E8 report may differ within the
# registered 1e-6 cross-platform tolerance; config and calibration must agree at 1e-9. Agent K comes
# directly from E8 arm (b), rather than a home re-score, and must agree across all three records at 1e-9.
e8_rep = json.loads(cfg.e8_report.read_text(encoding="utf-8"))
assert e8_rep["pair"] == cfg.pair
kv = str(e8f.verdict_k)
box_tau = {"K": 1.0 - float(e8_rep["per_k"][kv]["generic"]["K"]),
           "V": 1.0 - float(e8_rep["per_k"][kv]["generic"]["V"]),
           "agent_K": 1.0 - float(e8_rep["per_k"][kv]["agent"]["K"])}
cal_path = cfg.results_dir / "calibration" / "tau.json"
assert cal_path.exists(), ("run `summarize_e9 --calibrate-tau --config config/e9fl.toml --e8-report "
                           f"{cfg.e8_report}` BEFORE registering: `e9 --check` never looks for it (learnings 2026-09-14)")
cal = json.loads(cal_path.read_text(encoding="utf-8"))
assert cal["pair"] == cfg.pair and cal["e8_report_sha256"] == sha256_file_bytes(cfg.e8_report)
assert cal["mapper"]["k"] == cfg.mapper_k and all(cal["generic_dumps_match_e8_fingerprints"].values()), \
    "the calibration mapper or generic dumps do not match the E8 artifacts they claim to re-score"
for key in ("K", "V"):
    home = float(cal["tau"][key])
    assert abs(home - box_tau[key]) <= BOX_TAU_TOL * max(1.0, abs(home), abs(box_tau[key])), \
        f"tau_{key}: home calibration and box E8 report differ beyond the registered 1e-6 tolerance"
    assert abs(float(cfg.rule[f"tau_{key}"]) - home) <= CONFIG_TAU_TOL * max(1.0, abs(home)), \
        f"tau_{key}: config/e9fl.toml and the authoritative home calibration disagree"
agent = float(cal["tau"]["agent_K"])
assert abs(agent - box_tau["agent_K"]) <= CONFIG_TAU_TOL * max(1.0, abs(agent), abs(box_tau["agent_K"])), \
    "tau_agent_K: calibration and E8 arm (b) disagree"
assert abs(float(cfg.rule["tau_agent_K"]) - agent) <= CONFIG_TAU_TOL * max(1.0, abs(agent)), \
    "tau_agent_K: config/e9fl.toml and calibration disagree"

# R1: nothing under this entry exists yet.
assert not (cfg.results_dir / "report.json").exists(), f"{cfg.results_dir}/report.json exists: a run happened before registration; refusing"
for sub in ("scores", "controls", "bridge", "scratch"):
    assert not (cfg.results_dir / sub).exists(), f"{cfg.results_dir}/{sub} exists: refusing"

cov_path = cfg.results_dir / "align" / "coverage.json"
assert cov_path.exists(), "run `e9 --align-only --config config/e9fl.toml` first: the coverage this entry states comes from the instrument"
cov = json.loads(cov_path.read_text(encoding="utf-8"))
assert cov["config_sha256"] == sha256_text_file(cfg.config_path), "coverage.json was written under another config/e9fl.toml"
assert cov["context_cap"] == cfg.context_cap and cov["context_floor"] == cfg.context_floor and cov["rope"] is None
recs = {r["handoff_id"]: r for r in cov["alignments"]}
order = cov["run_order"]
included = sorted(h for h, r in recs.items() if not r["excluded"])
assert sorted(order) == included and len(order) == cov["coverage"]["included"] > 0
assert all(int(recs[h]["n_matched"]) >= 1 for h in order), \
    "an included handoff has no matched positions, so score_positions cannot run"
assert int(recs[order[0]]["n_matched"]) >= 2, \
    "the first run-order handoff has fewer than two matched positions, so the null control cannot run"
expected_order = sorted(included, key=lambda h: (recs[h]["n_sender"], h))
assert order == expected_order, "run order must be |S| ascending with ties broken by handoff id"
ns = [recs[h]["n_sender"] for h in order]
keep = cov["keep_subset"]
assert len(keep) == cfg.keep_n and set(keep) <= set(order)
by_reason = {}
for h, r in recs.items():
    if r["excluded"]:
        by_reason.setdefault(r["reason"], []).append(h)
empty = sorted(by_reason.get("receiver prompt is empty in the trace", []))
residual = sorted(h for reason, hs in by_reason.items() if "exceeds context cap" in reason for h in hs)
prior_cap = sorted(by_reason.get(f"S and R within context floor {cfg.context_floor} (decided under the prior cap)", []))
assert len(empty) + len(residual) + len(prior_cap) == cov["coverage"]["excluded"], "an exclusion reason this entry does not name"

# The partition, checked against the short cell's OWN completed run rather than asserted in prose.
short_rep = json.loads((short.results_dir / "report.json").read_text(encoding="utf-8"))
assert short_rep.get("complete") and short_rep["pair"] == cfg.pair, "the short cell's run is not complete"
short_included = sorted(a_["handoff_id"] for a_ in short_rep["alignments"] if not a_["excluded"])
assert prior_cap == short_included, \
    ("the handoffs this cell excludes under its floor are not exactly the short cell's included set; the two "
     "Llama cells do not partition and the residual count below would be wrong")
sum_s = sum(recs[h]["n_sender"] for h in order)
sum_r = sum(recs[h]["n_receiver"] for h in order)

if not a.preview:
    # R1 is a statement about committed bytes, not merely files that happen to exist in the worktree.
    # Require both the calibrated long config and the preceding ledger to be tracked and byte-identical
    # to HEAD immediately before appending; preview remains useful while those commits are being staged.
    for rel, path in (("config/e9fl.toml", cfg.config_path), ("ledger/ledger.md", LEDGER)):
        tracked = subprocess.run(["git", "ls-files", "--error-unmatch", "--", rel], cwd=REPO_ROOT,
                                 capture_output=True)
        assert tracked.returncode == 0, f"{rel} is not tracked; registration requires committed inputs"
        clean = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", rel], cwd=REPO_ROOT)
        assert clean.returncode == 0, f"{rel} differs from HEAD; commit it before registration"
        committed = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=REPO_ROOT, capture_output=True)
        assert committed.returncode == 0 and committed.stdout == path.read_bytes(), \
            f"{rel} is not byte-identical to HEAD; commit the calibrated config and preceding ledger first"
    assert _PENDING not in cfg.upstream_sha and re.fullmatch(r"[0-9a-f]{40}", cfg.upstream_sha), \
        "config/e9fl.toml still carries the pending upstream pin placeholder"
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=cfg.upstream_path, capture_output=True, text=True).stdout.strip()
    assert head == cfg.upstream_sha, f"upstream HEAD {head[:12]} != the pin {cfg.upstream_sha[:12]}"
    dirty = subprocess.run(["git", "status", "--porcelain", "--", *UPSTREAM_PATHS], cwd=cfg.upstream_path,
                           capture_output=True, text=True).stdout.strip()
    assert not dirty, f"upstream invoked paths are dirty at the pin:\n{dirty}"

tau_K, tau_V, tau_agent = float(cfg.rule["tau_K"]), float(cfg.rule["tau_V"]), float(cfg.rule["tau_agent_K"])
ladder = ", ".join(f"{float(t):.4g}" for t in cfg.rule["tau_ladder"])
names = lambda hs: "; ".join(f"`{h}`" for h in hs)      # noqa: E731
lens = lambda hs: ", ".join(f"{recs[h]['n_sender']:,}" for h in hs)      # noqa: E731
sl, sp = cfg.profiles["s_len_edges"], cfg.profiles["s_pos_edges"]
sl_bins = " / ".join(f"({sl[i]:,}, {sl[i + 1] - 1:,}]" if i == 0 else f"[{sl[i]:,}, {sl[i + 1] - 1:,}]"
                     for i in range(len(sl) - 1)) + f" / [{sl[-1]:,}, {cfg.context_cap:,}]"
sp_bins = " / ".join(f"[{sp[i]:,}, {sp[i + 1] - 1:,}]" for i in range(len(sp) - 1)) + f" / [{sp[-1]:,}, {cfg.context_cap:,}]"
gates = "/".join(cfg.required_entries)
heldout = cal["heldout"]

ENTRY = f"""### {NUM} — {a.date} — E9 long half registered before any prefill on the second model family, at a NATIVE receiver: entry 0035's D1(a), its configuration bridge and its scaled-receiver reading declared INAPPLICABLE; descriptive, no cell moves

**Why, and why now.** The short cell of this family ({SHORT}, decided by {PREV}) covers the handoffs whose
longer side fits {cfg.context_floor:,} tokens. The handoffs above it are the same question at greater
length, and on this pair they can be asked WITHOUT scaling anything: the receiver {tgt_id} ships a native
window that already covers the cap below. This entry registers that run before any prefill —
`results/e9fl/` holds no report and no score file at append, and the script refuses otherwise (R1) — and
registers, equally explicitly, what it is NOT. The only things under it are the alignment pass
(`e9 --align-only --config config/e9fl.toml`, `align/coverage.json` sha256
`{sha256_file_bytes(cov_path)[:12]}`) and the τ calibration (`calibration/tau.json` sha256
`{sha256_file_bytes(cal_path)[:12]}`), both checked here against the committed config.

**Descriptive, and what that forecloses.** **No hypothesis row is added and no `verdict:` line will
follow.** In particular this cell **cannot move, support or refute H-E9L, and is never pooled with entry
0036's handoffs.** H-E9L is a claim about a receiver pushed PAST its pretraining window by static YaRN
(entry 0035's D1(a)): the question there was whether a SCALED receiver keeps transfer-relevant fidelity at
those lengths. Here nothing is scaled. Two experiments sharing a length axis and nothing else; the numbers
are stated beside each other, never added, averaged or compared as if one were a replication of the other.

**Entry 0035's three scaled-receiver instruments, declared INAPPLICABLE by construction.** (i) **D1(a),
the receiver configuration**: there is no `[e9.rope]` — the receiver's own checkpoint declares a window
covering {cfg.context_cap:,}, so no scaling is needed and applying one would measure an artifact of our own
construction. (Imposing YaRN here to preserve the comparison with 0036 was considered and rejected:
upstream `scaled_config` merges the override OVER the checkpoint's own rope parameters, replacing this
family's native `rope_type` while leaving its band factors behind — it would REMOVE the checkpoint's own
scaling rather than compose with it.) (ii) **Control 4, the configuration bridge**: its entire content is
scaled arm versus native arm on the same tokens, and a natively long receiver has no scaled arm;
`config.py` refuses a `[e9.bridge]` without an `[e9.rope]`, and that refusal is correct here rather than an
obstacle. (iii) **The scaled-receiver reading** ("if the bridge control exceeds its maximum, H-E9L is a
claim about the scaled receiver only") has no referent and is not carried over. What replaces all three is
stated below and costs no GPU time.

**The two controls that replace the bridge.** Read off the dumps themselves: upstream `kvt/data.py` writes
each dump's `RopeSpec` — the `inv_freq` and attention factor of the loaded model's OWN rotary embedding —
halt-checks the reconstruction against the model at every dumped position, and
`linear_ceiling.e9.dump_rope_meta` keeps that record beside every dump's fingerprint BEFORE the non-kept
dumps are deleted. **(1) Native window:** `context_cap` = {cfg.context_cap:,} must be ≤ EVERY dump's
recorded `max_position_embeddings` — the positive statement that no extrapolation happened, which is
exactly what the bridge used to establish by measurement. A run whose dumps carry NO RoPE block at all (a
pin older than the RoPE-spec commit, where the strip is plain-θ and therefore silently wrong for this
family) **FAILS** this control; it does not pass it vacuously, and the summarizer refuses such a run
outright for this cell. **(2) Frequency identity, scoped by model ROLE:** the recorded spec must be
identical across every dump of the receiver, and across every dump of the source, compared separately.
Role-scoped is not a weakening: this pair's two sides carry different scaling factors and build different
inverse-frequency vectors by construction, so an unscoped equality assert would refuse every CORRECT run.
Both are fail-closed in `summarize_e9` and both survive the deletion of the non-kept dumps.

**The verdict set is a band of token counts, and the thresholds are not hardware bounds.**
`context_floor = {cfg.context_floor:,}`, `context_cap = {cfg.context_cap:,}`: registered LENGTH thresholds
in this pair's own tokens. {cfg.context_cap:,} is NOT "{cfg.context_floor:,} × 2.5" here — there is no
scaling factor to multiply — it is the same numeric band entry 0036 reported, kept only so the two long
cells are DEFINED over the same token counts. A handoff whose |S| and |R| both fit the floor was covered by
the short cell and is EXCLUDED here with its own reason; this script checks that those excluded ids are
EXACTLY the short cell's included set, so the partition is audited rather than asserted. Coverage from the
alignment pass: **{cov['coverage']['observed']} observed · {len(order)} included · {len(prior_cap)}
excluded as covered by the short cell · {len(residual)} excluded above the cap · {len(empty)} excluded for
an empty receiver prompt**. Together the two cells cover every handoff whose longer side is within
{cfg.context_cap:,} tokens; the **residual — {len(residual)} handoffs above {cfg.context_cap:,} — is scored
by NEITHER cell** and is named here so it cannot be mistaken for absence: {names(residual) if residual else 'none'}
{f'(|S| {lens(residual)})' if residual else ''}. Included |S| runs {ns[0]:,} to {ns[-1]:,}; the prefill
budget is {sum_s:,} sender tokens (both models) + {sum_r:,} receiver tokens = {2 * sum_s + sum_r:,} tokens.

**The instrument, unchanged.** 0023's rule verbatim, with τ this pair's own and IDENTICAL to the short
cell's (one mapper, one calibration): τ_K = {tau_K:.4f} = 1 − {heldout['K_r2_layer_mean']:.4f}, the
k = {cfg.mapper_k} mapper's held-out R² over {heldout['n_tokens']:,} tokens; τ_V = {tau_V:.4f}; τ_agent_K =
{tau_agent:.4f}. The HOME calibration is authoritative for K/V: this config agrees with it at 1e-9 and
the box-written E8 report agrees within the registered 1e-6 cross-platform tolerance; agent K agrees
across config, calibration and E8 arm (b) at 1e-9. The τ ladder ({ladder}); the seam bins; the block floor
({cfg.rule['min_block_len']}); the bootstrap (seed {cfg.controls['bootstrap_seed']},
{cfg.controls['bootstrap_reps']} reps). The band words
HOLDS ≤ {cfg.rule['holds_max']} / DEGRADES ≥ {cfg.rule['degrades_min']:.2f} are **computed and reported
here and are verdict-bearing for nothing**: this cell has no row. f* stays an oracle LOWER BOUND read on a
floor (0027).

**Run order, stopping rule, resume.** The driver scores the included handoffs in the registered order
`{cfg.order_by}` (|S| ascending, with any ties broken by id): `{order[0].split('/')[-1]}` ({ns[0]:,})
first, `{order[-1].split('/')[-1]}` ({ns[-1]:,}) last. Controls run on the first handoff in that order.
**This is the campaign's cuttable stage.** If the sitting must end before all {len(order)} are scored,
`e9 --close-partial --config config/e9fl.toml` closes the run: allowed only by this config, refused unless
the scored set is a PREFIX of the registered order, stamping the close time and naming every unscored
handoff; the figures entry then states "n scored of {len(order)} registered" beside every number. The
cutoff is the operator's, is recorded with its reason, and may not depend on any score. A relaunch after a
crash uses `--resume`.

**Keep subset.** n = {cfg.keep_n}, seed {cfg.keep_seed}, a fresh draw from THIS cell's sorted included ids
(numpy `choice` without replacement is not nested, so this is not a subset of the short cell's):
{names(keep)}. Small on purpose — at this cap one kept handoff is tens of GB of fp16 dumps. Their
stride-1 dumps are retained, fingerprinted, pulled home and re-scored from tensors by the summarizer under
0028's tolerance.

**Controls (1–3 as 0023/0025; 5 re-cut; 6 as 0025).** (1) Pipeline identity HALT. (2) Prefix-invariance
HALT on the first handoff in run order, max centered δ ≤
{float(cfg.controls['prefix_invariance_max_delta']):.0e} — entry {FAMILY}'s
pre-registered absolute float32 kernel-noise bound, exactly `config/e9.toml`'s and never a function of
τ_K. (3) δ_null, seeded derangement (seed
{cfg.controls['null_seed']}). **(5) Length profiles (descriptive):** f*(τ_K) and median δ_K (i) by |S| bin
{sl_bins}, and (ii) by matched-token position in S {sp_bins} — (ii) is the long-context figure, and its
edges are re-cut at this family's OWN boundary (the point where its RoPE frequency rescaling begins),
because entry 0035's edges were the midpoint of a YaRN window that does not exist here. (6) Seam profiles
b(t) and b⁻(t) as 0025, same bins.

**Gate and enforcement.** `e9 --check --config config/e9fl.toml` refuses until entries {gates} are in the
committed ledger, `config/e9fl.toml` is committed unmodified, the upstream is at the pin
`{cfg.upstream_sha[:12]}` with every invoked path clean, and the mapper artifact is present by sha.
`summarize_e9 --config config/e9fl.toml` (fail-closed, the only reader) re-derives every alignment from the
raw traces with the floor, re-derives the run order, checks a partial close is a prefix, recomputes every
figure, re-scores the kept dumps from tensors, recomputes τ, checks the controls and the two RoPE controls
above, and states the profiles and the band. The τ calibration is checked at THIS entry as well as by the
summarizer, for the reason entry {SHORT} gives.

**What this does NOT touch.** The H-E8, H-E9, H-E9L and H-E9F cells; entry 0036's figures and its 35
handoffs; τ, the rule, the band, the ladder and the keep subsets of every other cell; `results/e9/`,
`results/e9l/`, `results/e9s/`, `results/e9f/`, `results/e8*/`; `config/e9.toml`, `config/e9l.toml`,
`config/e9s.toml`, `config/e9c.toml`, `config/e9f.toml`. Nothing here is a figure: this cell's enter by
their own numbered entry, and the paper only from that entry.

**Scope.** One pair ({src_id} → {tgt_id}), one direction, one agent family, the long band of one corpus at
a NATIVE receiver; off-policy text for Llama-3; floor not method (0027); the {len(residual)} handoffs above
{cfg.context_cap:,} and the {len(empty)} with an empty receiver prompt stay excluded and counted;
generation quality after reuse not measured. `eval_hellaswag.py` and `compose_mapper.py` remain out of
scope for this pair (entry {FAMILY}).

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

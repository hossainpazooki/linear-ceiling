"""Append entry 0061 -- REGISTER, before any operator prefill, the cache-behavior REPAIR amendment: entry 0047's
instrument on the same 35 long handoffs (entry 0036), same prepared inputs as the operator's registered run (entry
0049), same FRESH / REUSE-ALL / RANDOM / CYCLIC arms and numerical controls, PLUS the repair arms 0047 switched off
(`oracle_fractions = []`): at each budget f in {0.05, 0.10, 0.20} the top-f matched tokens by archived token-mean
delta_K are recomputed IN PLACE against the reused predecessors (`oracle_ranked_<f>pct`), and, as the SELECTION
control at the same budget, a seeded uniformly random subset of the same size (`random_ranked_<f>pct`). The oracle
arm is CacheBlend's selection shape; the random arm separates "recomputing the worst tokens" from "recomputing any
tokens". DESCRIPTIVE: no hypothesis row, no `verdict:` line, no band, no cell moves. Operator rulings B and F of
2026-10-13 (private design, ~/dev/briefs/2026-10-13-linear-ceiling-experimental-gaps-plan.md, section 9).

Ordering guard: 0060 present, 0061 absent. Refuses unless the amendment config and the driver are in the tree at the
hashes below (text files hashed newline-normalized, as the ledger cites configs), the registered 0047 config is
unchanged, and nothing exists under the registered output tree (R1).

  --date YYYY-MM-DD   --preview   --repo-root <path>
Runs `ledger_check` after appending. Delete once appended, chained to the append with `&&`.
"""
import argparse
import datetime as dt
import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))
from linear_ceiling.config import load_e9_config                       # noqa: E402
from linear_ceiling.hashing import sha256_file_bytes, sha256_text_file  # noqa: E402
from linear_ceiling.ledger_check import _ENTRIES_HEAD, chain_hash     # noqa: E402

NUM, PREV = "0061", "0060"
REG, RUN_ENTRY, LONG = "0047", "0049", "0036"
CONFIG_SHA = "97aa99b1958eb55badf095955f44f2d6c0d67868a0f4196f6c5851f94e82d563"      # config/cache-behavior-repair.toml
BASE_CONFIG_SHA = "53c664556d18792401db8c1b930e487a90b88ab19c65ad94a1ab982094443a28"  # config/cache-behavior.toml, 0047's
CORE_SHA = "f346b5fdf3d3feff5918e3a0e95f1e084f154317213ba68ce1913ec5acdcade5"        # tools/cache_behavior/core.py, unchanged since 0047
RUN_SHA = "e137f1d8b8c5ce7f7747c8b06508ed7b09f6dc49a0731225dc8bcece9d8c2c33"         # tools/cache_behavior/run.py, the amended driver
RUN_SHA_0047 = "15e1ff8c1dbc7925398edc11ed68d91b6cdba4f335a49adcb29baa1b10729de5"    # the driver 0047 pinned, for the diff sentence
INPUT_MANIFEST_SHA12 = "2aeee5769c0a"   # the operator's prepared inputs, asserted by 0049
OUTPUT, BASE_OUTPUT = "results/cache-behavior-repair", "results/cache-behavior"

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
assert f"### {REG} " in text and f"### {RUN_ENTRY} " in text, "0047 and 0049 must be on the ledger"
assert f"`{INPUT_MANIFEST_SHA12}" in text, "0049's inputs-manifest sha is not on the ledger as expected"

cfg_path, base_path = R / "config" / "cache-behavior-repair.toml", R / "config" / "cache-behavior.toml"
core, run = R / "tools" / "cache_behavior" / "core.py", R / "tools" / "cache_behavior" / "run.py"
tests = R / "tests" / "test_cache_behavior.py"
for p in (cfg_path, base_path, core, run, tests):
    assert p.exists(), f"{p.relative_to(R)} missing"
assert sha256_text_file(cfg_path) == CONFIG_SHA, "config/cache-behavior-repair.toml is not the registered config"
assert sha256_text_file(base_path) == BASE_CONFIG_SHA, "config/cache-behavior.toml must be 0047's, unchanged"
assert sha256_text_file(core) == CORE_SHA, "core.py must be the driver 0047 pinned"
assert sha256_text_file(run) == RUN_SHA, "run.py is not the amended driver this entry pins"
cfg, base = tomllib.loads(cfg_path.read_text(encoding="utf-8")), tomllib.loads(base_path.read_text(encoding="utf-8"))
for key in base:
    assert key == "oracle_fractions" or cfg[key] == base[key], f"{key} differs from 0047's config; only the fraction lists may"
assert set(cfg) - set(base) == {"random_control_fractions"}, "the amendment adds exactly one key"
assert cfg["oracle_fractions"] == cfg["random_control_fractions"] == [0.05, 0.10, 0.20], "ruling B's budgets"
assert base["oracle_fractions"] == [] and "random_control_fractions" not in base
e9l = load_e9_config(R / "config" / "e9l.toml", R)
assert cfg["tau_K"] == e9l.rule["tau_K"] and cfg["rope"] == e9l.rope and cfg["context_cap"] == e9l.context_cap == 81920
src = run.read_text(encoding="utf-8")
assert 'cfg.get("random_control_fractions", [])' in src and 'arm.startswith("random_ranked_")' in src
assert "1_000_003" in src, "the selection control's seed offset must be the registered one"
assert "random_ranked_" in tests.read_text(encoding="utf-8"), "the selection control is untested"

# R1: nothing under this entry exists yet; 0049's tree is untouched and must stay so.
out = R / OUTPUT
assert not (out / "report.json").exists() and not (out / "summary.json").exists(), f"{out} holds a run; refusing"

# The 0049 figures this entry restates are READ from the summary file 0049 pins, never typed.
SUMMARY_0049_SHA12 = "5228de0dd8c4"
summary_path = R / BASE_OUTPUT / "summary.json"
assert summary_path.exists(), f"{summary_path.relative_to(R)} missing: the verified 0049 mirror is required"
assert sha256_file_bytes(summary_path)[:12] == SUMMARY_0049_SHA12, "results/cache-behavior/summary.json is not the file 0049 pins"
assert f"`{SUMMARY_0049_SHA12}" in text, "0049's summary sha is not on the ledger as expected"
_arms = json.loads(summary_path.read_text(encoding="utf-8"))["arms"]
F = {arm: (_arms[arm]["mean_kl"]["median"], _arms[arm]["top1_agreement"]["median"]) for arm in ("reuse", "random", "scrambled")}

s12 = lambda s: s[:12]  # noqa: E731
ENTRY = f"""### {NUM} — {a.date} — Cache-behavior REPAIR amendment registered before any operator prefill: oracle-ranked recompute of the top 5 / 10 / 20 % of matched tokens against the reused cache, with a random-selection control at each budget, on entry {LONG}'s 35 long handoffs; descriptive, no band, no cell moves

**Why, and why now.** Entry {REG} registered the cache-behavior comparison with no repair arm (`oracle_fractions = []`)
and its run, entry {RUN_ENTRY}, measured how far reading the assembled same-model cache moves the receiver's next-token
predictions (reuse median mean-KL {F['reuse'][0]:.4f} nats, top-1 {F['reuse'][1]:.4f}, against {F['random'][0]:.4f} / {F['random'][1]:.4f} for a
norm-matched random cache and {F['scrambled'][0]:.4f} / {F['scrambled'][1]:.4f} for the cyclic permutation; read from `{BASE_OUTPUT}/summary.json`
`{SUMMARY_0049_SHA12}…`, the file {RUN_ENTRY} pins).
Reviewer weakness W3 (`docs/2026-09-30-review-response-map.md`) and the CacheBlend line it cites ask what a bounded
repair buys: entry 0045 states the mean after REMOVING the top 10 % / 20 % of tokens, and entry 0058 reads f* as the
oracle REMOVAL fraction, not a repair cost. This entry registers the achieved counterpart: the same tokens RECOMPUTED in
place, against the reused predecessors, and the prediction sensitivity that remains. Operator ruling B, 2026-10-13.

**What is registered, by hash (text files newline-normalized, as the ledger cites configs).** `config/cache-behavior-repair.toml`
(`{s12(CONFIG_SHA)}…`): every key equal in value to entry {REG}'s `config/cache-behavior.toml` (`{s12(BASE_CONFIG_SHA)}…`,
unchanged) except `oracle_fractions = [0.05, 0.10, 0.20]` and the one added key `random_control_fractions = [0.05, 0.10, 0.20]`;
receiver `{cfg['model']}@{s12(cfg['revision'])}`, Transformers {cfg['transformers']}, PyTorch {cfg['torch']}, fp32, SDPA, the long cell's YaRN schedule, cap
{cfg['context_cap']:,}, seed {cfg['seed']}, τ_K = {cfg['tau_K']!r} used only to rank and to name the archived tail. Driver `tools/cache_behavior/core.py`
`{s12(CORE_SHA)}…` (byte-identical to {REG}'s) and `run.py` `{s12(RUN_SHA)}…`, which differs from {REG}'s `{s12(RUN_SHA_0047)}…` in exactly two
places: the arm list reads the optional `random_control_fractions` (absent in {REG}'s config, so that registration's arms are
unchanged) and adds one branch that draws the random-selection subset; tests `tests/test_cache_behavior.py` (the
budget equality and the selection difference, on a real tiny-model CPU forward). Inputs: the operator's prepared inputs of
entry {RUN_ENTRY} (manifest `{INPUT_MANIFEST_SHA12}…`, the 35 handoffs of {LONG} in archived order, the archived alignment
pairs as M, the recorded continuation C capped at {cfg['continuation_tokens']} tokens), reused byte for byte; `--prepare` is not re-run.

**Arms.** FRESH, REUSE-ALL, RANDOM and CYCLIC exactly as {REG} registered them (the same code path; their figures are
restated by this run as a within-run control against {RUN_ENTRY}, never re-read as new figures). Added, per budget
f ∈ {{0.05, 0.10, 0.20}} of each handoff's |M| (⌈|M| × f⌉ tokens): **ORACLE-f** — the ⌈|M| × f⌉ matched tokens with the
largest archived token-mean δ_K (stable descending argsort) are recomputed in receiver order against the cache assembled
so far, so a recomputed token reads reused predecessors and later tokens read recomputed ones; the other matched tokens
keep the relocated sender states. **RANDOM-f** — the same number of matched tokens drawn uniformly without replacement by
`make_rng(seed + handoff index + 1000003)`, a stream distinct from the RANDOM arm's noise. No arm recomputes the
unmatched tokens differently from REUSE-ALL. All arms score the same C[1:] under the same teacher-forced history.

**Numerical controls, readout, stopping rule.** As {REG}, unchanged: fresh repeat exact, prefix copy over
{cfg['prefix_control_tokens']} tokens ≤ {cfg['control_max_logit_error']}, archive bridge within {cfg['bridge_absolute_tolerance']} + {cfg['bridge_relative_tolerance']} × |archived|, TF32 off,
deterministic algorithms; per token KL(p_FRESH ‖ p_ARM) and top-1 agreement; per handoff mean KL, p90 KL, top-1 rate; over
the 35, median with p10 / p90 by `e7_stats`, handoffs weighted equally; largest sender first as the memory probe; stop on
any failed control, bridge, hash or OOM, keep the completed prefix, resume only unchanged. The attention slice of {REG}
is recorded as before and is not the object of this entry.

**The reading, fixed now (descriptive).** For each budget, ORACLE-f's and RANDOM-f's median mean-KL and top-1 are stated
beside REUSE-ALL's and FRESH's (KL 0 by definition); the pair (ORACLE-f, RANDOM-f) at one budget is the only comparison
this entry registers — whether ranked selection buys more than its budget. **No band is registered** and no threshold
on KL or top-1 is read: {RUN_ENTRY}'s "no downstream task-quality number is claimed" stands; an achieved KL is a
prediction-sensitivity figure on fixed text, not task accuracy and not a serving cost.

**The registered run (the operator's).** Requested only after this entry is committed. Card: 80 GB (entry {RUN_ENTRY}'s
peak was 24.95 GiB with nine arm passes per handoff now instead of three: the bound is three times {RUN_ENTRY}'s run,
92 minutes by its own launched and finished timestamps,
replaced by the probe on the largest case). R2–R8 of `docs/gpu-experiment-protocol.md`; output tree `{OUTPUT}/`
(`report.json`, per-case `.npz`, `summary.json`), {RUN_ENTRY}'s `{BASE_OUTPUT}/` untouched; mirrored home, verified, and
backed up to a Hub dataset by `tools/hf_verify_backup.py` before the figures entry.

**Gate and enforcement.** The driver asserts the config hash and every input's hash and records the source hashes,
runtime and GPU in `report.json`; this script refuses if any pinned file differs, if {REG}'s config changed, or if
`{OUTPUT}` holds a run (R1). The figures enter by their own entry, which calls `tools.cache_behavior.run.summarize`
in-process over the operator's verified output, asserts the report's source hashes equal the hashes above, checks
the restated REUSE-ALL / RANDOM / CYCLIC figures against {RUN_ENTRY}'s within the summarizer's own tolerance, and
refuses on any disagreement; no figure is typed.

**What this does NOT touch.** Every cell and verdict; τ, the rule, the bands; entries 0029, {LONG}, 0038, 0044, 0045,
{REG}, {RUN_ENTRY}, 0058 and their records; `config/cache-behavior.toml` and `{BASE_OUTPUT}/`; `config/e9*.toml`; the E9
drivers and summarizers.

**Scope.** One receiver, one corpus, the 35 long handoffs; fixed proprietary-model text; same-model only; three budgets
and two selection rules; selection by archived δ_K is an oracle (it reads the fresh states), so ORACLE-f bounds what a
δ-informed selector could achieve and is not a deployable policy; generation quality after reuse not measured.

prior-entries-sha256: PLACEHOLDER
"""

if a.preview:
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

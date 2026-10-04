"""Append entry 0047 -- REGISTER, before any operator prefill, the cache-behavior comparison: E-BEH's core question
(reviewer weakness W1) on the 35 long handoffs of entry 0036 -- how much does reading an ASSEMBLED cache built from the
receiver's own KV at the archived matched positions change its next-token predictions on the recorded continuation,
against a fresh prefill -- with a norm-matched random control, a cyclic-permutation control, and numerical
correctness controls. DESCRIPTIVE: no hypothesis row, no `verdict:` line, no band (the 0.95 / 0.90 proposal is
withdrawn: those numbers have no established task-quality meaning), no cell moves. The design, driver and frozen
config come from a co-author's PR #14 (design revisions in #13); the co-author also RAN it on a fork (an H100,
2026-10-01) before any upstream registration existed. That run is the PILOT, recorded with its chronology and gaps,
its figures NOT stated (evidence private). The registered run is the OPERATOR's; its figures enter by `append_0049.py`
from `tools.cache_behavior.run.summarize` in-process.

Ordering guard: 0046 present, 0047 absent. Refuses until PR #14's files are in the tree at their frozen hashes, if the
freeze record disagrees with them, and if anything already exists under the registered output tree.

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
from linear_ceiling.config import load_e9_config                # noqa: E402
from linear_ceiling.hashing import sha256_file_bytes            # noqa: E402
from linear_ceiling.ledger_check import _ENTRIES_HEAD, chain_hash  # noqa: E402

NUM, PREV = "0047", "0046"
LONG = "0036"
CONFIG_SHA = "53c664556d18792401db8c1b930e487a90b88ab19c65ad94a1ab982094443a28"
CORE_SHA = "f346b5fdf3d3feff5918e3a0e95f1e084f154317213ba68ce1913ec5acdcade5"
RUN_SHA = "15e1ff8c1dbc7925398edc11ed68d91b6cdba4f335a49adcb29baa1b10729de5"
INPUT_MANIFEST_SHA = "9a6f2923d3beda90cebde009ba80a12c5363c43a440fc19a356d6b3f11d4e2dc"   # the pilot's prepared inputs
PILOT = {"fork": "neuriv/linear-ceiling", "execution_commit": "9a18ce73af8655361dfb7c4f201a871a073958e6",
         "authored_utc": "2026-10-01T23:07:08Z", "committed_utc": "2026-10-01T23:40:23Z", "freeze_utc": "2026-10-01T23:40:22Z",
         "tag": "archive/cache-behavior-h100-2026-10-01", "gpu": "NVIDIA H100 PCIe 80 GB", "torch": "2.14.0+cu130",
         "transformers": "5.17.0", "cuda": "13.0", "handoffs": 35, "scored_tokens": 8908, "peak_gib": 24.95}
OUTPUT = "results/cache-behavior"

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

cfg_path = R / "config" / "cache-behavior.toml"
core, run = R / "tools" / "cache_behavior" / "core.py", R / "tools" / "cache_behavior" / "run.py"
freeze = R / "docs" / "2026-10-01-cache-behavior-freeze.json"
runbook = R / "docs" / "2026-10-01-cache-behavior-runbook.md"
tests = R / "tests" / "test_cache_behavior.py"
for p in (cfg_path, core, run, freeze, runbook, tests):
    assert p.exists(), f"{p.relative_to(R)} missing: merge PR #14 before registering"
assert sha256_file_bytes(cfg_path) == CONFIG_SHA, "config/cache-behavior.toml is not the frozen config"
assert sha256_file_bytes(core) == CORE_SHA and sha256_file_bytes(run) == RUN_SHA, "the driver is not the frozen driver"
fz = json.loads(freeze.read_text(encoding="utf-8"))
assert fz["config_sha256"] == CONFIG_SHA and fz["input_manifest_sha256"] == INPUT_MANIFEST_SHA
assert fz["source_sha256"]["tools/cache_behavior/core.py"] == CORE_SHA and fz["source_sha256"]["tools/cache_behavior/run.py"] == RUN_SHA
assert fz["handoffs"] == PILOT["handoffs"] == 35 and fz["excluded_continuations"] == 0
cfg = tomllib.loads(cfg_path.read_text(encoding="utf-8"))
e9l = load_e9_config(R / "config" / "e9l.toml", R)
assert cfg["model"] == "Qwen/Qwen3-1.7B" and len(cfg["revision"]) == 40
assert cfg["tau_K"] == e9l.rule["tau_K"], "tau_K must be the registered long-cell reference"
assert cfg["rope"] == e9l.rope, "the receiver's YaRN schedule must be the long cell's"
assert cfg["expected_handoffs"] == 35 and cfg["context_cap"] == e9l.context_cap == 81920
assert cfg["oracle_fractions"] == [], "no repair arms in the first registration"
assert cfg["transformers"] == PILOT["transformers"] and cfg["torch"].startswith("2.14.0")

# R1: nothing under this entry exists yet.
out = R / OUTPUT
assert not (out / "report.json").exists() and not (out / "summary.json").exists(), f"{out} holds a run; refusing"

s12 = lambda s: s[:12]  # noqa: E731
ENTRY = f"""### {NUM} — {a.date} — Cache-behavior comparison registered before any operator prefill: next-token sensitivity of the receiver to reading an assembled same-model cache on the 35 long handoffs, fresh vs reused with two perturbation controls; a co-author's prior fork run recorded as the pilot; descriptive, no band, no cell moves

**Why, and why now.** Reviewer weakness W1 (`docs/2026-09-30-review-response-map.md`): the tolerance τ_K is a weak
linear map's error and is not validated against anything the receiver does. Entry 0023's `[STRETCH]` proposal named
the experiment that would answer it: actually read the reused cache. This entry registers its core, as revised in
`docs/drafts/e-beh-design.md` (2026-10-01 update): FRESH against REUSE-ALL on the 35 handoffs of entry {LONG}, teacher-forced
on the recorded continuation. It measures **prediction sensitivity on fixed text**, not coding-task quality, not free
generation, not speed. The standing sentence "No downstream task-quality number is claimed" is **not** retired by this
entry or by its figures.

**What is registered, by hash.** `config/cache-behavior.toml` (`{s12(CONFIG_SHA)}…`): receiver `{cfg['model']}@{s12(cfg['revision'])}`,
Transformers {cfg['transformers']}, PyTorch {cfg['torch']}, fp32, SDPA, the long cell's YaRN schedule ({cfg['rope']['rope_type']} factor {cfg['rope']['factor']}, original
{cfg['rope']['original_max_position_embeddings']:,}), cap {cfg['context_cap']:,}, {cfg['chunk_tokens']}-token prefill chunks; seed {cfg['seed']}; τ_K = {cfg['tau_K']!r} used only to name the archived
high-error tail. Driver `tools/cache_behavior/core.py` `{s12(CORE_SHA)}…` and `run.py` `{s12(RUN_SHA)}…`, byte-identical to the
pilot's execution commit; freeze record `docs/2026-10-01-cache-behavior-freeze.json`; runbook `docs/2026-10-01-cache-behavior-runbook.md`;
tests `tests/test_cache_behavior.py`. Inputs: the 35 handoffs of {LONG} in its archived order, their archived alignment
pairs as the matched set M (one-token matches included; no new alignment), the recorded receiver response as the
continuation C capped at {cfg['continuation_tokens']} tokens including the unscored conditioning token C[0]; a handoff with fewer than two
continuation tokens is excluded and counted. The prepared input manifest the pilot froze hashes `{s12(INPUT_MANIFEST_SHA)}…`;
the operator's `--prepare` must reproduce it byte-for-byte from the verified e9l mirror and the manifest-pinned traces,
or the run refuses.

**Arms.** FRESH: the receiver's own prefill of R. REUSE-ALL: the receiver's KV from a prefill of S copied at p_S for
every token of M, keys relocated to p_R under the same fixed schedule and amplitude (amplitude applied once; a schedule
mismatch is refused), values unrotated; the unmatched tokens computed in receiver order against the cache assembled so
far, so later gaps and the continuation can depend on earlier reused states. Controls: RANDOM, a perturbation of the
fresh states with K and V norms matched to the reuse perturbation separately per token, layer and KV head (seeded via
`make_rng`); CYCLIC, the matched source states permuted across M with keys relocated (norms not matched). No
oracle-ranked or CacheBlend-style repair arm (`oracle_fractions = []`). All arms score the same C[1:] under the same
teacher-forced history.

**Numerical controls, fixed now; a failure stops expansion and is never relaxed after the fact.** Fresh repeat: a
second FRESH pass must reproduce the first's logits exactly. Prefix copy over {cfg['prefix_control_tokens']} tokens: maximum logit error ≤ {cfg['control_max_logit_error']}.
Archive bridge: the current runtime's same-model centered K/V mean deviation per handoff within {cfg['bridge_absolute_tolerance']} + {cfg['bridge_relative_tolerance']} × |archived|
of the {LONG} record. TF32 off, deterministic algorithms, `CUBLAS_WORKSPACE_CONFIG=:4096:8`. The largest sender is scored
first as the retained memory probe. Stopping rule: stop on any failed control, bridge, hash or OOM; keep the completed
prefix; resume only with unchanged code, inputs, config and runtime.

**Readout, fixed now.** Per scored token: KL(p_FRESH ‖ p_ARM) over the vocabulary and top-1 agreement. Per handoff: mean
KL, p90 KL, top-1 agreement rate, scored |C|. Over the 35: median with p10 / p90 by `e7_stats` (no interpolation),
handoffs weighted equally; a handoff is one unit and hardware replicas are never handoffs. Beside it, descriptive and
bounded: at the last {cfg['attention_queries']} receiver query positions, the fresh pass's attention (reconstructed from the SDPA forward's
queries and cached keys, GQA mapping kept, no full attention matrix retained) gives the attention mass on M, the mass on
the archived tail (tokens whose token-average δ_K exceeds τ_K, the set 0045 counts), and the attention-weighted archived
δ_K with its conditional value where mass is positive. This is a slice of E-TAIL Part B, not the all-query experiment,
and establishes no mechanism. **No band is registered**: the first run is descriptive; a later entry may register one
only against a quality measurement that does not exist yet.

**The pilot, recorded and not credited with a figure.** The co-author who designed this (PRs #13, #14) ran it on a fork:
execution commit `{PILOT['execution_commit'][:7]}` (authored {PILOT['authored_utc']}, committed {PILOT['committed_utc']}; tag `{PILOT['tag']}`), freeze
record written {PILOT['freeze_utc']},
one {PILOT['gpu']}, PyTorch {PILOT['torch']}, Transformers {PILOT['transformers']}, CUDA {PILOT['cuda']}; {PILOT['handoffs']} of {PILOT['handoffs']} handoffs, {PILOT['scored_tokens']:,} scored continuation tokens,
peak allocation {PILOT['peak_gib']} GiB with allocator retries. **Upstream R1 was not met by that run**: the card preceded the freeze,
which the freeze record says itself, and no upstream entry existed. Its evidence (report, 35 case records, summary,
inputs, logs) is on the co-author's machine and not on the Hub. **No figure from it is stated here or in any paper**; if
its bundle is published and recomputed under `docs/2026-10-03-co-author-run-admission.md`, that is a separate, later
entry, and its agreement with the run registered here is a cross-platform control.

**The registered run (the operator's).** Requested only after this entry is committed. Card: 80 GB preferred; the
pilot's 24.95 GiB peak with retries does not establish a smaller fit, so a 48 GB card needs the protocol's probe of the
largest case first. R2–R8 apply; output tree `{OUTPUT}/` (`report.json`, per-case `.npz`, `summary.json`, `inputs/`),
mirrored home, verified, and backed up to a Hub dataset (public or private, operator ruling 2026-10-04) by
`tools/hf_verify_backup.py` before the figures entry.

**Gate and enforcement.** The driver asserts the config hash and every input's hash and records the source hashes,
runtime and GPU in `report.json`; this script refuses if any frozen file differs or if `{OUTPUT}` holds a run (R1). The
figures enter by `append_0049.py`, which calls `tools.cache_behavior.run.summarize` in-process over the operator's
verified output, asserts the report's source hashes equal the committed driver, and refuses on any disagreement.

**What this does NOT touch.** Every cell and verdict; τ, the rule, the bands; entries 0029, {LONG}, 0038, 0044, 0045 and their
records; `config/e9*.toml`; the Qwen3 short cells, which stay Condition-1-bound and are not run here; the Llama drafts
(0050 / 0051). The registered E9 drivers and `summarize_e9` are unchanged.

**Scope.** One receiver, one corpus, 35 handoffs of 34,974–80,111 sender tokens read by receiver prompts of
3,433–25,073 tokens; fixed proprietary-model text, so KL and top-1 are not task outcomes; same-model only; no repair
arm, so nothing here bounds practical repair cost; fresh attention at 32 query positions is an association, not a cause.

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

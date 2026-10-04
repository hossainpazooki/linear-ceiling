"""Append entry 0046 -- REGISTER, before any operator prefill, the same-model extension of the E9 instrument to two
further models on the original 60 handoff texts: Qwen3-4B and SmolLM3-3B, with a six-case Qwen3-1.7B bridge.
DESCRIPTIVE: no hypothesis row, no `verdict:` line, no cell moves. The design, driver, frozen config and input
manifest come from a co-author's PRs #8 / #9; the co-author also RAN the design on a fork (an A100, 2026-10-01) before
any upstream registration existed. That run is recorded here as the PILOT, with its chronology and its gaps; its
figures are NOT stated (its evidence is private) and enter, if ever, only through
`docs/2026-10-03-co-author-run-admission.md`. The run this entry registers is the OPERATOR's, on a box requested after
this entry is on the ledger (R1), under R2-R8, with its figures entered by `append_0048.py` from
`tools/consolidation/summarize.py` run in-process over the operator's verified mirror.

Ordering guard: 0045 present, 0046 absent. Refuses until PR #8's files are in the tree at their frozen hashes, until
the manifest's 60 texts are exactly the 0036 / 0038 handoffs by text hash (checked against the local alignment
records), and if anything already exists under the registered output tree.

  --date YYYY-MM-DD   --preview   --repo-root <path> (dry-run against another checkout; default: this repository)
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

NUM, PREV = "0046", "0045"
LONG, SHORT_SCALED = "0036", "0038"       # the cells whose 35 + 25 handoff texts are replayed; fixed numbers
CORRECTIVE = "0045"
# Frozen by the co-author before the pilot's forwards (fork commit 3cb4bb3, 2026-10-01 02:41:37Z); verified byte-identical
# to PR #8's files by the operator's session on 2026-10-02.
CONFIG_SHA = "857cc92320cb6adcba02591506c32cc6fc439636636cf649cdba363363b673bc"
MANIFEST_SHA = "99185c5891fcebd1c61cd3e23ec899dbfce88b1053d20948c03407ecd6fd1a0e"
PILOT = {
    "fork": "neuriv/linear-ceiling", "registration_commit": "3cb4bb37157aa3443bd68cb49a8f1df41e6c1fd7",
    "registration_utc": "2026-10-01T02:41:37Z", "results_commit": "2fb44649feb4b0d7b88d2eeca03387ac3b163c08",
    "results_utc": "2026-10-01T05:28:11Z", "gpu": "A100-SXM4-80GB",            # as the fork's entry 0046 states it
    "lock": {"torch": "2.14.0", "transformers": "5.17.0", "numpy": "2.5.3", "cuda_runtime": "13.0.96"},  # requirements-linux.lock
    "run_py_sha": "f544ae87408517c481b448eac553e43978721ce69748b8fb14f3e46ce6a79411",
    "capture_py_sha": "b713473055aa6fa1cc3bd99a9d44fc2fdea2a7ff3cd210a1ac6dc1483d240c3f",
}
MODELS = {"qwen17_bridge": 6, "qwen4": 60, "smollm3": 60}
MIRROR = "results/consolidation"          # the operator's evidence tree, laid out as summarize.py reads it

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

# --- the frozen instrument and inputs (PR #8), at their hashes ---------------------------------------------------
cfg_path, man_path = R / "config" / "consolidation.toml", R / "config" / "consolidation-manifest.json"
tools = {n: R / "tools" / "consolidation" / n for n in ("run.py", "capture.py", "prepare.py", "summarize.py", "setup.sh",
                                                         "requirements-linux.lock")}
runbook = R / "docs" / "2026-09-30-consolidation-runbook.md"
for p in (cfg_path, man_path, runbook, *tools.values()):
    assert p.exists(), f"{p.relative_to(R)} missing: merge PR #8 (and #9 for summarize.py) before registering"
assert sha256_file_bytes(cfg_path) == CONFIG_SHA, "config/consolidation.toml is not the frozen config"
assert sha256_file_bytes(man_path) == MANIFEST_SHA, "config/consolidation-manifest.json is not the frozen manifest"
cfg = tomllib.loads(cfg_path.read_text(encoding="utf-8"))
man = json.loads(man_path.read_text(encoding="utf-8"))
assert man["config_sha256"] == CONFIG_SHA, "the manifest does not pin this config"
tool_sha = {n: sha256_file_bytes(p) for n, p in tools.items()}   # recorded in the entry; the pilot's differ (see PILOT)

# --- the registered numerical reference is the long cell's --------------------------------------------------------
e9l = load_e9_config(R / "config" / "e9l.toml", R)
assert cfg["tau_K"] == e9l.rule["tau_K"] and cfg["tau_V"] == e9l.rule["tau_V"], "tau must be the registered Qwen reference"
assert sorted(cfg["tau_ladder"]) == sorted(float(t) for t in e9l.rule["tau_ladder"]), "ladder must be the registered one"
assert cfg["context_cap"] == e9l.context_cap == 81920 and cfg["dtype"] == "float32" and cfg["attention"] == "sdpa"
assert {m["name"] for m in cfg["models"]} == set(MODELS)
spec = {m["name"]: m for m in cfg["models"]}
for m in cfg["models"]:
    assert m["rope_type"] == "yarn" and len(m["revision"]) == 40, m["name"]
assert spec["qwen4"]["factor"] == spec["qwen17_bridge"]["factor"] == 2.5 and spec["smollm3"]["factor"] == 2.0

# --- the 60 texts are exactly 0036's 35 and 0038's 25, by text hash against the local alignment records --------------
def text_hashes(cell: str) -> dict:
    d = R / "results" / cell / "align"
    assert d.exists(), f"{d} missing: the registrant's machine must hold the verified {cell} mirror"
    out = {}
    for p in d.glob("*.json"):
        rec = json.loads(p.read_text(encoding="utf-8"))
        if "handoff_id" not in rec:          # coverage.json sits beside the records
            continue
        if not rec.get("excluded"):
            out[rec["handoff_id"]] = rec["text_sha256"]
    return out
known = {**{h: ("e9l", s) for h, s in text_hashes("e9l").items()}, **{h: ("e9s", s) for h, s in text_hashes("e9s").items()}}
for name, n in MODELS.items():
    recs = man["models"][name]
    inc = [r for r in recs if not r["excluded"]]
    assert len(recs) == len(inc) == n, f"{name}: {len(inc)} included of {len(recs)}, registered {n}"
    for r in recs:
        assert r["handoff"] in known and known[r["handoff"]][1] == r["text_sha256"], f"{name}: {r['handoff']} is not a 0036/0038 text"
        assert known[r["handoff"]][0] == r["cohort"], f"{name}: {r['handoff']} cohort label disagrees with the archive"
cohorts = {name: sorted({r["cohort"] for r in man["models"][name]}) for name in MODELS}
assert all(c == ["e9l", "e9s"] for c in cohorts.values())
n_long = sum(1 for r in man["models"]["qwen4"] if r["cohort"] == "e9l")
n_short = 60 - n_long
assert (n_long, n_short) == (35, 25)
max_sender = {name: max(r["sender_tokens"] for r in man["models"][name]) for name in MODELS}

# --- R1: nothing under this entry exists yet ----------------------------------------------------------------------
mirror = R / MIRROR
for name in MODELS:
    for p in (mirror / "a100" / "results" / name / "report.json", mirror / "results" / name / "report.json"):
        assert not p.exists(), f"{p} exists: a run happened before registration; refusing"

sha12 = lambda s: s[:12]  # noqa: E731
ENTRY = f"""### {NUM} — {a.date} — Same-model extension registered before any operator prefill: the E9 instrument on the original 60 handoff texts replayed through Qwen3-4B and SmolLM3-3B, with a six-case Qwen3-1.7B bridge; a co-author's prior fork run recorded as the pilot; descriptive, no cell moves

**Why, and why now.** Reviewer weakness W7 (`docs/2026-09-30-review-response-map.md`): one model pair. The second
family (0039–0044) answers it at one more pair. This entry registers the cheapest further answer the instrument
allows: the SAME 60 handoff texts that decided H-E9L and the scaled short cell (entries {LONG} and {SHORT_SCALED}; 35 long,
25 short) replayed through two more receivers on the same-model arm only, at the registered Qwen reference τ. It
asks whether the zero floor is a property of one small Qwen pair. It does not ask about cross-model reuse, length
(the cohorts are different handoffs), or quality. **No hypothesis row is added and no verdict is read**: a new
model's mean deviation against another model's mapper tolerance is a descriptive comparison, stated as such.

**What is registered, by hash.** `config/consolidation.toml` (`{sha12(CONFIG_SHA)}…`): models and revisions
`Qwen/Qwen3-1.7B@{sha12(spec['qwen17_bridge']['revision'])}` (bridge, {MODELS['qwen17_bridge']} handoffs: shortest, middle and
longest sender of each cohort), `Qwen/Qwen3-4B@{sha12(spec['qwen4']['revision'])}` ({MODELS['qwen4']}), `HuggingFaceTB/SmolLM3-3B@{sha12(spec['smollm3']['revision'])}`
({MODELS['smollm3']}); fp32, SDPA, {cfg['chunk_tokens']}-token chunked prefill with the full causal KV history, cap {cfg['context_cap']:,}; YaRN factor
{spec['qwen4']['factor']} on the Qwen models and {spec['smollm3']['factor']} on SmolLM3 (its rotary-free layers unchanged); τ_K = {cfg['tau_K']!r} and τ_V = {cfg['tau_V']!r},
**the 0023 Qwen3-0.6B→1.7B mapper's held-out shortfall, used as a common numerical reference and NOT a calibrated
threshold for either new model**; ladder {sorted(cfg['tau_ladder'])}; seed {cfg['seed']}. `config/consolidation-manifest.json`
(`{sha12(MANIFEST_SHA)}…`) pins every input byte: the 60 texts re-tokenized per model (max sender {max_sender['qwen4']:,} / {max_sender['smollm3']:,} tokens, no exclusion),
each text's sha256 equal to the archived alignment's `text_sha256` (checked here against `results/e9l/align` and
`results/e9s/align`), and exact ordered token matching by `e9_align.matching_pairs`. Keys are captured after any key
normalization and before rotation, values after projection; no fp16 serialization.

**Controls and bridge, fixed now.** (1) Per model, before any handoff: a 1,024-token full prefill against the chunked
prefill of the same prefix plus one later token; maximum normalized token deviation ≤ {cfg['control_max_delta']} or the run refuses.
(2) The bridge: the original receiver re-run on six archived handoffs; relative mean-deviation gap ≤ {cfg['bridge_mean_relative_tolerance']} and
absolute f* gap ≤ {cfg['bridge_fstar_absolute_tolerance']} against the archived records at every τ, or expansion to the new models stops.
(3) The longest sender runs first as the memory probe and is retained. (4) One raw matched-vector witness per model
(the shortest included sender) is kept for independent re-scoring; other vectors are transient and removed only after
their compact record and atomic checkpoint exist. (5) Resume refuses changed code, runtime, device, dtype or inputs,
and refuses a `complete` flag with missing handoffs. Readout per handoff and arm: per-token δ (0023's unit: a token's
share of the layer-head's unexplained variance; mean = 1 − R²), its mean, maximum, tail fraction over τ, f*(τ) at τ_K and
the ladder, all by `e9_pertoken.centered_delta` / `token_mean` / `f_star`.

**Instrument, as committed:** `tools/consolidation/run.py` `{sha12(tool_sha['run.py'])}…`, `capture.py` `{sha12(tool_sha['capture.py'])}…`,
`prepare.py` `{sha12(tool_sha['prepare.py'])}…`, `summarize.py` `{sha12(tool_sha['summarize.py'])}…` (the fail-closed reader: bundle hashes, report-to-config and
report-to-manifest pins, every record and witness re-hashed, token deltas recomputed, the mean/R² identity, witnesses
re-scored from raw tensors, a seeded trajectory-cluster bootstrap with `e7_stats` quantiles), `setup.sh`, the Linux lock,
and the runbook `docs/2026-09-30-consolidation-runbook.md`. The committed driver differs from the pilot's by the
resume-identity and cohort checks and comments; its arithmetic is the same functions.

**The pilot, recorded and not credited with a figure.** The co-author who designed this (PRs #8, #9) ran it on a fork:
registration commit `{PILOT['registration_commit'][:7]}` ({PILOT['registration_utc']}, the fork's own ledger), results commit
`{PILOT['results_commit'][:7]}` ({PILOT['results_utc']}); the fork's entry says one {PILOT['gpu']}, FP32 prefill, all 60 texts per model scored
without exclusion, bridge gaps within tolerance; the environment it pins is `requirements-linux.lock` (torch {PILOT['lock']['torch']},
transformers {PILOT['lock']['transformers']}, numpy {PILOT['lock']['numpy']}, CUDA runtime {PILOT['lock']['cuda_runtime']}); the exact runtime, GPU name and `code_sha256` are in its
unpublished reports; driver at the registration commit `run.py` `{sha12(PILOT['run_py_sha'])}…`, `capture.py` `{sha12(PILOT['capture_py_sha'])}…`
(re-hashed from the fork by the operator's session, 2026-10-04). **Upstream R1 was not met by that run**: the card was
provisioned before the fork registration and no upstream entry existed. Its evidence (compact records, one witness
per model, logs) is on the co-author's machine and not on the Hub (R8 not met). Therefore **no figure from the pilot is
stated here or in any paper**; if its bundle is published and recomputed under `docs/2026-10-03-co-author-run-admission.md`,
that is a separate, later entry, and the pilot's agreement with the run registered here becomes a cross-platform
control in the sense of 0028.

**The registered run (the operator's).** Requested only after this entry is committed. Card: an L40S 48 GB is the
expectation (fp32 weights ≈ 16 GB for the 4B, full-cap KV < 3 GB), confirmed by the protocol's probe before any paid
forward; a larger card if the probe says so. R2–R8 of `docs/gpu-experiment-protocol.md` apply: fresh output tree,
detached launch, log rotation, pull → verify → delete per handoff, release checklist, mirror at `{MIRROR}/` laid out as
`summarize.py` reads it (`provenance/`, `a100/inputs/`, `a100/results/<model>/`, `archive/records/{{e9s,e9l}}`, `SHA256SUMS`;
the `a100/` directory name is the reader's and does not assert the card), backup to a Hub dataset (public or private,
operator ruling 2026-10-04) verified by `tools/hf_verify_backup.py` before the figures entry.

**Gate and enforcement.** The driver asserts the config and manifest hashes at start and every input's hash; this
script refuses if either file differs from the frozen bytes or if any report exists under `{MIRROR}` (R1). The figures
enter by `append_0048.py`, which runs `summarize.py` in-process over the verified mirror, asserts the reports' `code_sha256`
equal the committed driver files, and refuses on any disagreement; no figure is typed.

**What this does NOT touch.** H-E9, H-E9L, H-E9F and every cell; τ, the rule, the bands, the ladder; entries 0029,
{LONG}, {SHORT_SCALED}, 0044 and their records; `config/e9*.toml`; the Llama long drafts (now 0050 / 0051). Nothing here is pooled with
any Qwen3-0.6B→1.7B figure: the new models are reported separately, beside the original, never in one statistic.

**Scope.** Same-model arm only; one corpus; the original 60 texts, so the long/short difference is a difference of
handoffs and configuration, not an isolated length effect (W2 is E-TRUNC's); τ is one map's shortfall; nothing about
generation quality, serving speed, or cross-model transfer is measured. Hardware replicas are never handoffs.

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

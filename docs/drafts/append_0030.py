"""Append entry 0030 -- the E8 amendment, registered BEFORE anything is rescored.

Ordering guard: 0029 present, 0030 absent; `results/e8a/` holds no report (nothing scored under this entry);
every parameter is read from `config/e8a.toml` and the prior run's record from `results/e8/report.json`
(the dumps this amendment reuses, by fingerprint). Runs `ledger_check` after appending. Delete once appended."""
import json
import subprocess
import sys
from pathlib import Path

from linear_ceiling import REPO_ROOT
from linear_ceiling.config import load_e8_config
from linear_ceiling.e8 import agent_holdout_frac, dump_fingerprint, required_entries
from linear_ceiling.hashing import sha256_file_bytes
from linear_ceiling.ledger_check import _ENTRIES_HEAD, chain_hash

LEDGER = REPO_ROOT / "ledger" / "ledger.md"
text = LEDGER.read_text(encoding="utf-8").replace("\r\n", "\n")
assert "### 0029 " in text and "### 0030 " not in text, "ordering: 0029 present, 0030 absent"
cfg = load_e8_config(REPO_ROOT / "config" / "e8a.toml", REPO_ROOT)
assert cfg.amendment and cfg.amendment["entry"] == "0030" and required_entries(cfg)[-1] == "### 0030 "
assert not (cfg.results_dir / "report.json").exists(), "results/e8a already holds a report: nothing may be registered after a score"
prior_path = Path(cfg.reuse_agent_dumps_from)
prior = json.loads(prior_path.read_text(encoding="utf-8"))
for w in ("source", "target"):   # the dumps to be reused are 0020's, byte for byte, at append time
    assert dump_fingerprint(cfg.agent_dumps / w) == prior["dumps"]["agent"][w], f"agent/{w} dump differs from 0020's record"
k1 = prior["per_k"][str(cfg.verdict_k)]
r2_prior = json.loads((Path(REPO_ROOT) / "results" / "e8" / "r2" / f"agent_k{cfg.verdict_k}.json").read_text(encoding="utf-8"))
n_seqs, seq_len, stride = int(cfg.text["n_seqs"]), int(cfg.text["seq_len"]), int(cfg.stride)
per_seq_tokens = seq_len // stride
frac_a, frac_b = cfg.holdout_frac, agent_holdout_frac(cfg)
import math
n_prior_seqs = math.ceil(frac_a * n_seqs)
ks = ", ".join(str(k) for k in cfg.report_k)

ENTRY = f"""### 0030 — 2026-09-04 — E8 amended before any rescoring: arm (b) over every agent sequence, per-sequence moments, a seeded bootstrap of the drop; descriptive; the H-E8 cell and τ_agent_K do not move

**Why, and why now.** 0016 matched arm (b)'s protocol to arm (a)'s "exactly": the agent-text dumps were split
by sequence with `holdout_frac` {frac_a}, and only the last ⌈{frac_a} × {n_seqs}⌉ = {n_prior_seqs} sequences ({n_prior_seqs * per_seq_tokens:,} tokens at stride
{stride}) were scored. That match was the wrong instinct for arm (b): the k = 1 mapper was fit on the GENERIC
calibration dumps (arm (a)'s training rows), never on agent text, so nothing in the agent dumps needs holding
out and the split threw away {n_seqs - n_prior_seqs} of {n_seqs} sequences. Track B (2026-09-01/02) tried to register this and stopped:
the pinned `score_mapper.py` refused `--holdout-frac 1.0` (empty training mask) and wrote no per-sequence
moments — upstream changes. They are made now (below), after the E9 verdict (0029) and before anything is
rescored: `results/e8a/` holds no report at append and this entry's script refuses otherwise.

**What is registered.** A rescoring of 0020's OWN tensors — the agent dumps at `{cfg.agent_dumps.relative_to(REPO_ROOT).as_posix()}`
and the token file they were dumped from are reused and must match the fingerprints recorded in
`{prior_path.relative_to(REPO_ROOT).as_posix()}` (sha256 `{sha256_file_bytes(prior_path)[:12]}`) byte for byte; nothing is resampled
or re-dumped, and the generic dumps are the archived ones. For each k ∈ {{{ks}}}:

- arm (a), generic: the mapper's own held-out sequences, `holdout_frac` {frac_a} — unchanged; scoring more of
  its own calibration dumps would be in-sample and is not done;
- arm (b), agent: `--holdout-frac {frac_b}` — every one of the {n_seqs} sequences ({n_seqs * per_seq_tokens:,} tokens), the mapper's
  transfer measured on all the agent text 0016 sampled;
- the drop (a − b) and its 0009 band word, **read descriptively**: the H-E8 cell was decided by 0020 under the
  registered protocol and does not move here; this entry carries no `verdict:` line;
- per-sequence R² for both arms from the per-token record (upstream `per_sequence_moments`: SSE and SST per
  sequence per head, SST around the GLOBAL held-out mean, so the sums reproduce the pooled moments exactly and a
  sequence's R² is its share of the same decomposition, not a re-centred fit); median (p10, p90) over sequences
  with the pinned quantile convention (`e7_stats`);
- a seeded percentile bootstrap over agent sequences (seed {cfg.amendment['bootstrap_seed']} + k, {cfg.amendment['bootstrap_reps']} reps) of arm (b)'s pooled R² and of the
  drop, 2.5% / 97.5%; reported, read by nothing;
- the change from 0020's arm (b) figure at the same k, named as such.

**What this does NOT touch.** τ_agent_K = 1 − 0020 arm (b) K R² (= 1 − {k1['agent']['K']:.4f} = {1 - k1['agent']['K']:.4f}) is 0025's registered
alongside tolerance and stays as registered; the all-sequence figure is reported beside it, never substituted
(0029 has already read τ_agent_K). τ_K, the E9 rule, band and cells are untouched. `results/e8/` is not
rewritten — E9's calibration checks read it — and this amendment writes only under `results/e8a/`.

**Upstream change (re-pin).** `scripts/score_mapper.py` accepts `--holdout-frac 1.0` when only scoring (train
figures null; an empty held-out mask is still refused) and, with `--per-token`, writes `seq_idx`, `seq_ids`,
`sse_seq_*`, `sst_seq_*` plus a `per_sequence` block whose sums it checks against the layer moments before
writing; `kvt/pertoken.py::per_sequence_moments` carries the decomposition with a test that the sequence sums
reproduce the layer moments exactly. Re-pin recorded in `config/e8a.toml` and `UPSTREAM.md` by the operator after
committing upstream (the placeholder refuses by name); parent `d5786df` (the 0026 pin). E8's original pin
`71df4504` is unchanged for `results/e8/`, whose gate now refuses by drift (three later re-pins touched its
invoked paths) — a known state, recorded here, not repaired: 0020 stands on its own record.

**Instrument and enforcement.** `config/e8a.toml` (separate results dir; `agent_holdout_frac`, `reuse_agent_dumps_from`,
`[e8.amendment]`), `e8.reuse_agent_dumps` (fingerprint + token-file check before any scoring), `e8.required_entries`
(the gate requires THIS entry beside 0009 and 0016), `summarize_e8` amendment figures (per-sequence recompute from
the record, refused on disagreement with the report and with the re-scored json; bootstrap; the prior report's
hash re-checked). Tests: reuse by fingerprint, refusal on a changed dump, gate entries, per-sequence recompute and
bootstrap, refusal on a tampered per-sequence list and on a changed prior report.

**Scope.** All of 0009's, 0016's and 0020's limits (off-policy text for Qwen; one pair; one direction; visible
messages only). No hypothesis cell changes with this entry; no `verdict:` line. The figures enter by their own
numbered entry from a passing `summarize_e8 --config config/e8a.toml`.

prior-entries-sha256: PLACEHOLDER
"""

new = text + ("" if text.endswith("\n") else "\n") + "\n" + ENTRY
head = _ENTRIES_HEAD.search(new)
digest = chain_hash(new, new.index("### 0030 "), head.start())
new = new.replace("prior-entries-sha256: PLACEHOLDER", f"prior-entries-sha256: {digest}")
LEDGER.write_text(new, encoding="utf-8", newline="\n")
print("appended 0030; chain", digest[:12])
r = subprocess.run([sys.executable, "-m", "linear_ceiling.ledger_check"], cwd=REPO_ROOT, capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip())
raise SystemExit(r.returncode)

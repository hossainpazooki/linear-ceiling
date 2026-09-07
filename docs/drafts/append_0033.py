"""Append entry 0033 -- the calibration-size sensitivity, registered BEFORE the upstream fit exists.

Ordering guard: 0032 present, 0033 absent. Nothing under this entry may exist yet: the tagged mapper
(`mappers/<pair>/<tag>/k*`) must be ABSENT upstream, `results/e8c/` and `results/e9c/` must hold no report. The
n = 420 calibration dumps must exist (they are the pre-existing upstream artifacts of 2026-08-24) and are
fingerprinted here so the fit is bound to bytes named before it ran. 0031 must have run (its report is the record
the E8 change is measured from). Every parameter is read from `config/e8c.toml` and `config/e9c.toml`. Runs
`ledger_check` after appending. Delete once appended."""
import json
import subprocess
import sys
import tomllib
from pathlib import Path

from linear_ceiling import REPO_ROOT
from linear_ceiling.config import load_e8_config, load_e9_config, load_e9_rescore_config
from linear_ceiling.e8 import agent_holdout_frac, dump_fingerprint, required_entries
from linear_ceiling.e9_rescore import kept_handoffs
from linear_ceiling.hashing import sha256_file_bytes
from linear_ceiling.ledger_check import _ENTRIES_HEAD, chain_hash

LEDGER = REPO_ROOT / "ledger" / "ledger.md"
text = LEDGER.read_text(encoding="utf-8").replace("\r\n", "\n")
assert "### 0032 " in text and "### 0033 " not in text, "ordering: 0032 present, 0033 absent"
e8c = load_e8_config(REPO_ROOT / "config" / "e8c.toml", REPO_ROOT)
e9c = load_e9_rescore_config(REPO_ROOT / "config" / "e9c.toml", REPO_ROOT)
e9 = load_e9_config(REPO_ROOT / "config" / "e9.toml", REPO_ROOT)
with open(REPO_ROOT / "config" / "e8c.toml", "rb") as f:
    cal = tomllib.load(f)["e8"]["calibration"]
assert e8c.amendment and e8c.amendment["entry"] == "0033" == e9c.amendment["entry"] and required_entries(e8c)[-1] == "### 0033 "
assert e8c.mapper_tag == e9c.mapper_tag and e8c.upstream_sha == e9c.upstream_sha and e8c.verdict_k == e9c.mapper_k
assert not (e8c.results_dir / "report.json").exists(), "results/e8c already holds a report: nothing may be registered after a score"
assert not (e9c.results_dir / "report.json").exists(), "results/e9c already holds a report: nothing may be registered after a score"
tag_dir = e8c.upstream_path / "mappers" / e8c.pair / e8c.mapper_tag
assert not tag_dir.exists(), f"{tag_dir} already exists: the fit ran before registration; refusing"
assert not (e8c.upstream_path / "results" / "mapper" / e8c.pair / e8c.mapper_tag).exists(), "tagged r2.json already exists"
n420 = {w: e8c.upstream_path / e8c.generic_dumps / w for w in ("source", "target")}
for w, p in n420.items():
    assert (p / "meta.json").exists(), f"n = 420 calibration dump missing at {p}"
n420_meta = json.loads((n420["source"] / "meta.json").read_text(encoding="utf-8"))
assert int(n420_meta.get("n_seqs", 0)) == int(cal["n_seqs"]), f"n420 dump meta n_seqs {n420_meta.get('n_seqs')} != {cal['n_seqs']}"
n420_fp = {w: sha256_file_bytes(p / "meta.json") for w, p in n420.items()}
n420_files = {w: len(dump_fingerprint(p)) for w, p in n420.items()}
prior_path = Path(e8c.reuse_agent_dumps_from)
assert prior_path.exists(), "results/e8a/report.json (0031) must exist: the E8 change is measured from its all-sequence figures"
prior = json.loads(prior_path.read_text(encoding="utf-8"))
assert prior.get("amendment", {}).get("entry") == "0030", "the prior report is not 0031's (amendment 0030) record"
for w in ("source", "target"):
    assert dump_fingerprint(e8c.agent_dumps / w) == prior["dumps"]["agent"][w], f"agent/{w} dump differs from the 0031 record"
e9_prior = json.loads((e9c.prior_results_dir / "report.json").read_text(encoding="utf-8"))
kept = kept_handoffs(e9_prior)
e9_summary = e9c.prior_results_dir / "summary.json"
assert e9_summary.exists(), "results/e9/summary.json (0029's summarizer output) must exist"
ks = ", ".join(str(k) for k in e8c.report_k)
tau_K, tau_agent = float(e9.rule["tau_K"]), float(e9.rule["tau_agent_K"])
ladder = ", ".join(f"{float(t):.4g}" for t in e9.rule["tau_ladder"])

ENTRY = f"""### 0033 — 2026-09-06 — Calibration-size sensitivity registered before any fit: the k = {e8c.verdict_k} mapper refit on n = {cal['n_seqs']} sequences, E8 arms and the E9 kept-subset cross arm re-scored; descriptive; no cell moves

**Why, and why now.** Every transfer figure on the record (0020, 0029, 0031) reads through ONE mapper: the k = {e8c.verdict_k}
content-space map fit upstream on 50 calibration sequences (10,240 training tokens). The source paper calibrates on
roughly 128K tokens, 12.5× more (upstream ledger, H2 probe), and the upstream's own curve hypotheses H-L1–L4 asked
whether the collapse at larger k was calibration size; no run of them is on this record. An independent review
(2026-09-06) named the mapper's provenance as the submission's first rejection risk. The n = {cal['n_seqs']} calibration dumps
already exist upstream (`{e8c.generic_dumps}`, nested over the n = 50 draw by the upstream's own check, 2026-08-24)
and no mapper has been fit on them: this entry registers that fit and what is re-scored with it, before the fit runs —
`{tag_dir.relative_to(e8c.upstream_path).as_posix()}` is absent and both results directories are empty at append, and this
script refuses otherwise.

**What is registered.**

- **The fit (upstream, no code change, no re-pin):** `{cal['fit']}` at the pin
  `{e8c.upstream_sha[:12]}` (λ {cal['lam']}, hold-out {cal['holdout_frac']}, {cal['space']} space: `fit_mapper.py` defaults, stated); k ∈ {{{ks}}}
  fitted, k = {e8c.verdict_k} the compared one. Inputs bound by fingerprint at append: `meta.json` sha256 source `{n420_fp['source'][:12]}` /
  target `{n420_fp['target'][:12]}` ({n420_files['source']} / {n420_files['target']} files per dump; n_seqs {n420_meta['n_seqs']}). The artifacts land where
  `--tag` puts them and every downstream report fingerprints them (`mapper` block).
- **E8 under `config/e8c.toml` → `results/e8c/`:** 0030's protocol exactly — arm (a) on the tagged mapper's OWN
  held-out sequences (`holdout_frac` {e8c.holdout_frac}; the last ⌈{e8c.holdout_frac} × {cal['n_seqs']}⌉ of the n = {cal['n_seqs']} dumps; in-sample otherwise),
  arm (b) over every one of the {int(e8c.text['n_seqs'])} agent sequences (`--holdout-frac {agent_holdout_frac(e8c)}`), 0020's agent dumps and token
  file reused by fingerprint through 0031's record (`{prior_path.relative_to(REPO_ROOT).as_posix()}`, sha256 `{sha256_file_bytes(prior_path)[:12]}`),
  per-sequence moments, seeded bootstrap (seed {e8c.amendment['bootstrap_seed']} + k, {e8c.amendment['bootstrap_reps']} reps), the change measured from
  0031's all-sequence figures at the same k, and arm (a) cross-checked against the tagged `r2.json`.
- **E9 cross arm under `config/e9c.toml` → `results/e9c/`:** `score_positions.py` re-run over the {len(kept)} kept
  handoffs' retained stride-1 dumps (0025's seeded draw; fingerprints of 0029's record) and 0029's alignments, with
  the tagged k = {e9c.mapper_k} mapper. Nothing is prefilled. **Control, refusing:** the same-model arm does not depend on the
  mapper, so its per-token squares must reproduce 0028's home re-score within 0028's tolerance (sums 1e-5, squares
  1e-2 relative) on every handoff, or no cross figure is read. Reported: cross-arm f*(τ_K = {tau_K:.4f}) beside 0029's
  cross figure on the same {len(kept)} handoffs (recomputed from 0028's record by the same arithmetic, not read from a
  summary); f* under the tagged mapper's own tolerance τ_K′ = 1 − its verified arm (a) K R² (from `results/e8c/`);
  f*(τ_agent_K = {tau_agent:.4f}); the τ ladder ({ladder}); bridge R²; a seeded bootstrap of the median (seed
  {e9c.amendment['bootstrap_seed']}, {e9c.amendment['bootstrap_reps']} reps). Band words at 0023's edges are descriptive.

**What this does NOT touch.** H-E8 (0020) and H-E9 (0029) stay as decided; τ_K, τ_V, τ_agent_K, the E9 rule, band,
keep subset, and every existing results directory are unchanged; no `verdict:` line here or in the figures entry.
The n = {cal['n_seqs']} figures are reported BESIDE the n = 50 record, never substituted; whichever way they fall, the decided
cells were decided under the registered protocol. The kept subset is {len(kept)} of 25 included handoffs and the cross
re-score is a claim about those {len(kept)}.

**Instrument and enforcement.** `E8Config.mapper_tag` (tagged mapper + tagged archived `r2.json`; `mapper` fingerprint
in every E8 report, re-checked by `summarize_e8`); `linear_ceiling.e9_rescore` (`check` / `run` / `summarize`;
gate = this entry + 0019/0023/0025/0027/0029 + both configs committed unmodified + the 0030 pin by ancestry with
E9's invoked paths unchanged + the tagged artifact present; the same-arm control; τ_K′ taken from the E8 report
scored with byte-identical mapper files). Tests: tagged paths and fingerprints, refusal on swapped mapper bytes, the
control firing, refusal on a changed kept dump / prior report / foreign E8 report.

**Scope.** 0009/0016/0020/0030's limits (off-policy text; one pair; one direction) and 0029's (one pair, {len(kept)} kept of
25 included of 68 observed, floor not method). The figures enter by their own numbered entry from passing
`summarize_e8 --config config/e8c.toml` and `e9_rescore summarize`.

prior-entries-sha256: PLACEHOLDER
"""

new = text + ("" if text.endswith("\n") else "\n") + "\n" + ENTRY
head = _ENTRIES_HEAD.search(new)
digest = chain_hash(new, new.index("### 0033 "), head.start())
new = new.replace("prior-entries-sha256: PLACEHOLDER", f"prior-entries-sha256: {digest}")
LEDGER.write_text(new, encoding="utf-8", newline="\n")
print("appended 0033; chain", digest[:12])
r = subprocess.run([sys.executable, "-m", "linear_ceiling.ledger_check"], cwd=REPO_ROOT, capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip())
raise SystemExit(r.returncode)

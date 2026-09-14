"""Append entry 0037 -- the E9 scaled short cell registered BEFORE any prefill: 0029's 25 handoffs under 0036's
receiver configuration; descriptive, decides nothing.

Ordering guard: 0036 present, 0037 absent (if another entry lands as 0037 first, rename this script and the number in
`config/e9s.toml` [e9.gate] and below; the README allocates). Nothing under this entry may exist yet: `results/e9s/`
holds no report and no score file (R1). What MUST exist: `results/e9s/align/coverage.json` from `e9 --align-only
--config config/e9s.toml`, whose included set and keep draw must equal 0029's exactly (read from
`results/e9/report.json`); `config/e9s.toml` committed with 0036's pin and rope block; the upstream HEAD at that pin.
Every number below is read from the config, that coverage file or 0029's report; nothing is typed. `--preview`
prints the entry without appending. Runs `ledger_check` after appending. Delete once appended."""
import json
import subprocess
import sys
from pathlib import Path

from linear_ceiling import REPO_ROOT
from linear_ceiling.config import load_e9_config
from linear_ceiling.e9 import UPSTREAM_PATHS, required_markers
from linear_ceiling.hashing import sha256_file_bytes, sha256_text_file
from linear_ceiling.ledger_check import _ENTRIES_HEAD, chain_hash

NUM, PREV = "0037", "0036"
PREVIEW = "--preview" in sys.argv
LEDGER = REPO_ROOT / "ledger" / "ledger.md"
text = LEDGER.read_text(encoding="utf-8").replace("\r\n", "\n")
assert f"### {PREV} " in text and f"### {NUM} " not in text, f"ordering: {PREV} present, {NUM} absent"
cfg = load_e9_config(REPO_ROOT / "config" / "e9s.toml", REPO_ROOT)
e9 = load_e9_config(REPO_ROOT / "config" / "e9.toml", REPO_ROOT)
e9l = load_e9_config(REPO_ROOT / "config" / "e9l.toml", REPO_ROOT)
assert cfg.rule == e9.rule and cfg.controls == e9.controls and cfg.mapper_k == e9.mapper_k, "rule/tau/band/controls must be byte-for-byte E9's"
assert cfg.context_cap == e9.context_cap and cfg.context_floor == 0 and cfg.keep_seed == e9.keep_seed and cfg.keep_n == e9.keep_n
assert cfg.rope == e9l.rope and cfg.upstream_sha == e9l.upstream_sha, "the receiver configuration and pin must be 0036's"
assert cfg.required_entries[-1] == NUM and required_markers(cfg)[-1] == f"### {NUM} "
assert cfg.bridge is None and cfg.profiles is None
assert not (cfg.results_dir / "report.json").exists(), "results/e9s/report.json exists: a run happened before registration; refusing"
assert not (cfg.results_dir / "scores").exists() and not (cfg.results_dir / "controls").exists(), "results/e9s/ holds score or control files: refusing"
cov_path = cfg.results_dir / "align" / "coverage.json"
assert cov_path.exists(), "run `e9 --align-only --config config/e9s.toml` first: the coverage this entry states comes from the instrument"
cov = json.loads(cov_path.read_text(encoding="utf-8"))
assert cov["config_sha256"] == sha256_text_file(cfg.config_path), "coverage.json was written under another config/e9s.toml"
assert cov["context_cap"] == cfg.context_cap and cov["context_floor"] == 0 and cov["rope"] == cfg.rope
prior = json.loads((e9.results_dir / "report.json").read_text(encoding="utf-8"))
assert prior.get("complete") and prior["config_sha256"] == sha256_text_file(e9.config_path), "0029's report is not the committed config/e9.toml's"
recs = {a["handoff_id"]: a for a in cov["alignments"]}
included = sorted(h for h, r in recs.items() if not r["excluded"])
assert included == sorted(prior["scores"]), "the scaled cell must cover exactly 0029's scored handoffs"
prior_al = {a["handoff_id"]: a for a in prior["alignments"]}
for h in included:
    for k in ("n_sender", "n_receiver", "n_matched", "text_sha256"):
        assert recs[h][k] == prior_al[h][k], f"{h}: alignment {k} differs from 0029's"
keep = cov["keep_subset"]
assert sorted(keep) == sorted(prior["keep_subset"]) and len(keep) == cfg.keep_n, "the keep draw must reproduce 0025's eight"
order = cov["run_order"]
assert sorted(order) == included and len(order) == cov["coverage"]["included"] == 25
ns = [recs[h]["n_sender"] for h in order]
assert ns == sorted(ns), "run order must be |S| ascending"
excluded = {h: r for h, r in recs.items() if r["excluded"]}
assert len(excluded) == cov["coverage"]["excluded"] == prior["coverage"]["excluded"] == 43
if not PREVIEW:
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=cfg.upstream_path, capture_output=True, text=True).stdout.strip()
    assert head == cfg.upstream_sha, f"upstream HEAD {head[:12]} != the pin {cfg.upstream_sha[:12]}"
    dirty = subprocess.run(["git", "status", "--porcelain", "--", *UPSTREAM_PATHS], cwd=cfg.upstream_path, capture_output=True, text=True).stdout.strip()
    assert not dirty, f"upstream invoked paths are dirty at the pin:\n{dirty}"
tau_K, tau_V, tau_agent = float(cfg.rule["tau_K"]), float(cfg.rule["tau_V"]), float(cfg.rule["tau_agent_K"])
ladder = ", ".join(f"{float(t):.4g}" for t in cfg.rule["tau_ladder"])
rope = cfg.rope
sum_s, sum_r = sum(recs[h]["n_sender"] for h in order), sum(recs[h]["n_receiver"] for h in order)
names = lambda hs: "; ".join(f"`{h}`" for h in hs)      # noqa: E731

ENTRY = f"""### {NUM} — 2026-09-13 — E9 scaled short cell registered before any prefill: 0029's {len(order)} handoffs under 0036's receiver configuration; descriptive, decides nothing

**Why, and why now.** The 4-pager's two cells differ in receiver configuration as well as length: 0029 (H-E9, the 25
handoffs within 32,768) was measured on the native receiver, 0036 (H-E9L, the 35 handoffs of 35K–80K) on a receiver
scaled by static YaRN 2.5. 0036's configuration bridge (control 4) measured, on three short handoffs at pairs (p, p),
that YaRN alone moves the content key by a median δ_K of 0.071–0.089 — the same order as the cross-cell difference in
the far-from-seam floor (16+ bin: 0.019 in 0029, 0.063 in 0036) and a plausible part of the τ = 0.03 ladder's move
(0.1433 → 0.5255). Every "what length changes" figure in the paper (outline v3 §5.2) is therefore length AND
configuration. This entry registers, before any prefill, the run that removes the configuration from that comparison:
0029's 25 handoffs, re-rendered under 0036's receiver, scored by 0029's instrument unchanged. `results/e9s/` holds
no report and no score file at append; this script refuses otherwise (R1). The only thing under it is the
instrument's own alignment pass (`e9 --align-only --config config/e9s.toml`, `align/coverage.json` sha256
`{sha256_file_bytes(cov_path)[:12]}`), which reproduces 0029's coverage and keep draw exactly (checked by this script
against `results/e9/report.json`: the same {len(order)} included ids with the same `n_sender`/`n_receiver`/`n_matched` and
text hashes, the same {len(excluded)} excluded, the same eight kept).

**What is measured, and what is not decided.** The instrument is 0023/0025/0027's verbatim (`[e9.rule]`, `[e9.controls]`,
`[e9.alignment]`, `[e9.mapper]`, `[e9.keep]` byte-for-byte `config/e9.toml`): per matched token the centered deviation
in R²'s units between the receiver's own K at the sender position and at the re-rendered position; f*(τ_K = {tau_K:.4f})
as the oracle selective-recompute fraction defined on the MEAN of the remaining tokens (0023), read on a floor (0027);
τ_V = {tau_V:.4f}, τ_agent_K = {tau_agent:.4f}, the τ ladder ({ladder}), the seam bins, the block floor ({cfg.rule['min_block_len']}), the
bootstrap (seed {cfg.controls['bootstrap_seed']}, {cfg.controls['bootstrap_reps']} reps), the cross arm through 0029's n = 50 k = 1 mapper by sha. **No hypothesis row is
added and no `verdict:` line will follow:** H-E9 (0029) and H-E9L (0036) are immutable; this run's band word, if
stated, is descriptive. Cap {cfg.context_cap:,}, no floor, so the verdict set of 0029 is the whole included set: **{cov['coverage']['observed']}
observed · {len(order)} included · {len(excluded)} excluded** (0029's reasons, unchanged). Prefill budget {sum_s:,} sender tokens (1.7B and
0.6B) + {sum_r:,} receiver tokens = {2 * sum_s + sum_r:,} tokens.

**The receiver configuration.** Both models under static YaRN in the HF form `{json.dumps(rope, sort_keys=True)}`,
exactly 0036's, on every dump of the run, at the upstream pin `{cfg.upstream_sha[:12]}` (0035's RoPE-spec commit: the
spec is read from the model's own rotary embedding, halt-checked at dump time, and stripped as R^T/m). The native
run's pin `d5786df` is NOT usable here: its strip is plain-θ and would be wrong under YaRN (0035).

**The registered reading (`linear_ceiling.e9_compare`, fail-closed; descriptive).** After a passing
`summarize_e9 --config config/e9s.toml`, the comparison reads the native run (`results/e9/`) and the scaled run
(`results/e9s/`) token by token: it refuses unless both are complete under their committed configs, cover the same
{len(order)} handoffs, share every alignment array byte for byte, and every score and per-token record matches the hash its
report recorded. It states, per handoff and in the median over handoffs, the paired difference of the mean δ_K
(scaled − native; seeded bootstrap of the median, seed 37, 2000 reps), f*(τ) at τ_K and on the ladder under both
receivers, the fraction of tokens over τ_K under both, the pooled per-token difference, and the seam profile b⁻(t)
under both. Against `results/e9l/summary.json` it states the **configuration share**: (scaled − native) / (long −
native) for the far-from-seam (16+) median δ_K and for each ladder τ's median f*. **Reading fixed now:** a share near
1 says the receiver configuration accounts for the cross-cell difference and the paper's "what length changes"
figures are re-stated as configuration effects; a share near 0 says the handoffs do and length is the remaining
candidate; in between the paper reports both. None of these is a claim about length alone: the two cells are
different handoffs. The one thing this run can change in the paper is which sentence follows each 0036 descriptive.

**Run order, stopping rule, resume.** As 0035: `n_sender_asc` (|S| ascending, ties by id), controls on the first handoff
in that order, `--close-partial` allowed only on a prefix of the registered order with every unscored handoff named,
`--resume` after a crash. A partial close leaves the comparison undefined on the unscored handoffs, which
`e9_compare` refuses; the entry recording the figures states "n scored of {len(order)} registered".

**Keep subset.** 0025's draw reproduced: seed {cfg.keep_seed}, n {cfg.keep_n} over the same sorted ids → the same eight handoffs
({names(keep)}). Their scaled stride-1 dumps are retained, fingerprinted, pulled home beside their native twins
under `results/e9/scratch/`, and re-scored from tensors by the summarizer under 0028's tolerance. A (p, p)
native-vs-scaled read on these eight at home, CPU only, is available and is not registered here.

**Controls (1–3 as 0023/0025; 6 as 0025).** (1) Pipeline identity HALT. (2) Prefix-invariance HALT on the first handoff in
run order, max centered δ ≤ {cfg.controls['prefix_invariance_max_delta']:.0e}. (3) δ_null (seed {cfg.controls['null_seed']}). No configuration bridge (control 4) and no length
profiles (control 5): the whole run is the bridge, over all {len(order)} handoffs at the pairs the instrument actually reads.
(6) Seam profiles b(t) and b⁻(t) as 0025, same bins.

**Gate and enforcement.** `e9 --check --config config/e9s.toml` refuses until entries {'/'.join(cfg.required_entries)} are in the
committed ledger, `config/e9s.toml` is committed unmodified, the upstream is at the pin with every invoked path clean,
and the mapper artifact is present by sha; `summarize_e9 --config config/e9s.toml` is the only reader of the run's
figures and `e9_compare` the only reader of the comparison; both refuse on any disagreement. Tests:
`tests/test_e9_scaled_short.py` (the config is 0029's instrument under 0036's receiver; the comparison refuses on a
different handoff set, a different pairing, an incomplete run, a report under another config, and an edited record).

**What this does NOT touch.** The H-E9 and H-E9L cells, τ_K, τ_V, τ_agent_K, the rule, the band, the ladder, 0025's keep
subset, `results/e9/`, `results/e9l/`, `results/e8*/`, `results/e9c/`, `config/e9.toml` and `config/e9l.toml`. The
n = 420 arm is not run under this entry. Nothing here is a figure; the comparison's figures enter by their own
numbered entry, and the paper only from that entry.

**Scope.** One pair (Qwen3-0.6B → 1.7B), one direction, one agent family, the short half of one corpus under a
receiver that is not the trained-range model; floor not method (0027); generation quality after reuse not measured.

prior-entries-sha256: PLACEHOLDER
"""

if PREVIEW:
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

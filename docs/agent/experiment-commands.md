# Experiment command reference

The command catalog that used to live in the root `CLAUDE.md`. The rules that govern these commands are in
`CLAUDE.md`, `docs/gpu-experiment-protocol.md` (R1–R12) and each experiment's registering ledger entry; where
a comment below and an entry disagree, the entry wins.

**Interpreter.** `$PY` below means the repository's own virtual environment:

- Windows: `.venv/Scripts/python.exe`
- Linux / macOS: `.venv/bin/python`

If the repo venv is unavailable, say so. Do not silently substitute another environment for a scientific run:
gates, summarizers and recorded hashes assume the pinned environment.

**Status words.** Each section states what the ledger records about that experiment, by entry number. Decided and
completed entries do not change. For anything registered, staged or unrun, the live state is in the ledger tail
and `docs/drafts/README.md` (the only allocator), not here.

## Common checks

Run after any change; the definition of done in `CLAUDE.md`.

```
$PY -m pytest -q                 # suite (synthetic, offline)
$PY -m linear_ceiling.seal verify
$PY -m linear_ceiling.lint_scope
$PY -m linear_ceiling.ledger_check
```

## E0 — the screen gate (completed: entries 0003–0004)

```
$PY -m linear_ceiling.e0 --config config/e0.toml   # refuses until entry 0003 sets the rule
$PY -m linear_ceiling.summarize_e0
$PY -m linear_ceiling.summarize_e0_depth   # per-layer depth structure (entry 0006)
```

## E7 — replay over public traces (completed: H-E7a NOT CONFIRMED, H-E7b UNESTIMABLE; entries 0013–0018, 0022, 0024)

The corpus manifest is `config/e7-manifest.json`; real trajectories live under `traces/` (gitignored) and never
enter history. Corpus formats and what they omit: `docs/2026-09-01-swe-bench-trace-recon.md`.

```
$PY -m linear_ceiling.e7_manifest write     # NETWORK, once: hash traces/ + S3 keys/ETags + selection rule -> config/e7-manifest.json (commit it)
$PY -m linear_ceiling.e7_manifest fetch     # NETWORK: rebuild traces/ from the committed manifest (S3 for SWE-bench, sha256+size refused on mismatch; tau files listed by sha for manual restore, LF-normalize a Windows clone)
$PY -m linear_ceiling.e7_manifest check     # disk vs the committed manifest, both directions + bytes
$PY -m linear_ceiling.e7 --check           # E7 gate only; refuses until 0006/0007 + config/e7.toml + config/e7-manifest.json are committed
$PY -m linear_ceiling.e7 --config config/e7.toml   # replay over ALL corpora under traces/ (gitignored); refuses if disk != manifest
$PY -m linear_ceiling.summarize_e7          # fail-closed: recomputes EVERY E7 figure from RAW traces (all 3 suites, headroom, reported usage); refuses if disk, report or manifest disagree
$PY -m linear_ceiling.summarize_e7 --strategy-override composio_swekit=exact   # entry 0022's sensitivity as a flag (after full verification; `sensitivity` in recon.json; ships only in the 0009 successor)
LC_REAL_TRACES=1 $PY -m pytest -q tests/test_e7_sensitivity.py   # the 0022 pin (565,025 / 255,690,850 = 0.2210%) against the real corpus; skipped without traces/
$PY -m linear_ceiling.summarize_e7 --overlap-null --cache-aware-ratio   # entry 0024 recon (after full verification): null controls + H-E7a under four denominator readings -> results/e7/recon.json
```

## E8 family — content shift of the cross-model mapper

### E8 (completed: H-E8 NOT CONFIRMED, entry 0020)

```
$PY -m linear_ceiling.e8 --check           # E8 gate: refuses until 0016 + config/e8.toml committed AND upstream HEAD == pinned sha, clean
$PY -m linear_ceiling.e8                   # CPU: sample agent text (0016 s4) -> upstream dump_kv -> score_mapper both arms -> results/e8/report.json
$PY -m linear_ceiling.summarize_e8          # fail-closed: re-runs the upstream scorer on fingerprinted dumps (~25 min CPU) and compares
```

### E8a — amendment, all agent sequences (registered 0030, ran 0031; descriptive)

```
$PY -m linear_ceiling.e8 --check --config config/e8a.toml   # E8 amendment gate (entry 0030): 0009 + 0016 + 0030 committed, the 0030 upstream re-pin, 0020's dumps by fingerprint
$PY -m linear_ceiling.e8 --config config/e8a.toml           # CPU (~10 min): rescores 0020's agent dumps with --holdout-frac 1.0 + per-token records -> results/e8a/report.json; re-dumps nothing
$PY -m linear_ceiling.summarize_e8 --config config/e8a.toml # fail-closed: re-scores, per-sequence R^2 from the record, seeded bootstrap over agent sequences, change from 0020 -> results/e8a/summary.{md,json}
```

### E8fa — the second family's amendment (registered 0052, ran 0053; descriptive)

```
$PY -m linear_ceiling.e8 --check --config config/e8fa.toml  # second family's E8 amendment gate (entry 0052): 0009 + 0016 + 0039 + 0052 committed, the family pin 06f8d55 (contains 0030's 223f469), 0040's dumps and token file by fingerprint
$PY -m linear_ceiling.e8 --config config/e8fa.toml          # CPU (~10 min): rescores 0040's agent dumps with --holdout-frac 1.0 + per-token records -> results/e8fa/report.json; re-dumps nothing; results/e8f untouched
$PY -m linear_ceiling.summarize_e8 --config config/e8fa.toml # fail-closed, as e8a: per-sequence R^2 from the record, seeded bootstrap, change from 0040 -> results/e8fa/summary.{md,json}; the figures entry reads it in-process
```

### E8c — calibration-size sensitivity, n = 420 mapper (registered 0033, ran 0034; descriptive)

```
$PY -m linear_ceiling.e8 --check --config config/e8c.toml   # entry 0033 gate: 0009 + 0016 + 0033 committed, the 0030 pin, the TAGGED n = 420 mapper present, 0031's dumps by fingerprint
$PY -m linear_ceiling.e8 --config config/e8c.toml           # CPU: 0030's protocol with the n = 420 mapper (mappers/<pair>/n420) -> results/e8c/report.json (mapper bytes fingerprinted)
$PY -m linear_ceiling.summarize_e8 --config config/e8c.toml # fail-closed, as e8a; also refuses on swapped mapper bytes
```

## E9 — native short cell (completed: H-E9 HELD, entry 0029; gate entries 0019 + 0023 + 0025 + 0026 + 0027)

Calibrate τ before the GPU run; the gate does not check for it and the summarizer refuses without it.

```
$PY -m linear_ceiling.e9 --check           # E9 gate: refuses until 0019 + 0023 + 0025 + 0026 + 0027 + config/e9.toml committed AND the 0026 upstream re-pin holds (and the mapper artifact is present)
$PY -m linear_ceiling.e9 --align-only      # entry 0025: every alignment + results/e9/align/coverage.json (coverage, reasons, keep draw, block counts) before any prefill; CPU, no gate
$PY -m linear_ceiling.summarize_e9 --calibrate-tau   # 0023, before the GPU run: tau = 1 - archived k=1 held-out R^2 via upstream score_mapper --per-token; writes results/e9/calibration/tau.json (~1 min CPU)
$PY -m linear_ceiling.e9                   # GPU-scale: identity + null controls on the first handoff, then per handoff 3 stride-1 dumps + score_positions --per-token; checkpoints per handoff; keep-subset dumps retained
$PY -m linear_ceiling.summarize_e9          # fail-closed: alignments from raw traces, R^2 from moments, per-token sums to moments, keep subset re-scored under 0028's cross-platform tolerance (sums 1e-5, squares 1e-2), tau recomputed, controls checked -> f*(tau), seam/depth profiles, band
```

## E9 scaled short cell (registered 0037, ran 0038; descriptive)

```
$PY -m linear_ceiling.e9 --align-only --config config/e9s.toml   # scaled short cell (0037): must reproduce 0029's 25 + keep draw; the registration script checked it
$PY -m linear_ceiling.e9 --check --config config/e9s.toml        # gate: 0019/0023/0025/0027/0035/0037 committed, upstream at 0036's pin 063f402, mapper by sha
$PY -m linear_ceiling.summarize_e9 --calibrate-tau --config config/e9s.toml   # BEFORE the GPU run (0023): the gate does not check it and the summarizer refuses without it (learnings 2026-09-14)
$PY -m linear_ceiling.summarize_e9 --config config/e9s.toml      # fail-closed, as e9l minus bridge/profiles; then:
$PY -m linear_ceiling.e9_compare --native config/e9.toml --scaled config/e9s.toml --long results/e9l/summary.json   # paired native-vs-scaled per token + the configuration share -> results/e9s/compare.{json,md}; refuses on any seam
```

## E9 long — H-E9L (registered 0035; decided HELD, entry 0036)

Runbook: `docs/2026-09-10-e9l-gpu-runbook.md`.

```
$PY -m linear_ceiling.e9 --check --config config/e9l.toml        # E9-long gate (entry 0035): 0019/0023/0025/0027/0035 committed, config/e9l.toml committed, the RoPE-spec upstream pin, mapper by sha
$PY -m linear_ceiling.e9 --align-only --config config/e9l.toml   # cap 81,920 / floor 32,768: the 35 newly included handoffs, run order, keep draw -> results/e9l/align/coverage.json (what 0035 cites)
$PY -m linear_ceiling.summarize_e9 --calibrate-tau --config config/e9l.toml   # tau recomputed under the e9l pin -> results/e9l/calibration/tau.json (needed before the e9l summary; ~2 min CPU)
$PY -m linear_ceiling.e9 --config config/e9l.toml [--resume]    # GPU box: bridge control first (native vs YaRN receiver on 3 short handoffs), then the 35 by |S| ascending; every dump under --rope-scaling; --resume keeps hash-matching checkpoint work
$PY -m linear_ceiling.e9 --close-partial --config config/e9l.toml   # entry 0035 stopping rule: close an unfinished run at the operator's cutoff; scored set must be a prefix of the registered order; unscored named
$PY -m linear_ceiling.summarize_e9 --config config/e9l.toml     # fail-closed as above plus: floor re-derived, run order re-derived, partial prefix checked, bridge re-scored from tensors + its registered reading, length profiles (by |S| bin, by position in S)
```

## E9 rescore and tail

### e9c — kept-subset cross arm with the n = 420 mapper (registered 0033, ran 0034; descriptive)

```
$PY -m linear_ceiling.e9_rescore check --config config/e9c.toml   # entry 0033 gate: 0019/0023/0025/0027/0029 + 0033, both configs committed, pin by ancestry, tagged mapper present
$PY -m linear_ceiling.e9_rescore run                              # CPU: score_positions over the 8 kept handoffs' retained dumps + 0029's alignments with the n = 420 mapper -> results/e9c/
$PY -m linear_ceiling.e9_rescore summarize                        # fail-closed: same-arm CONTROL vs 0028's recheck (refuses), cross f* under tau_K / tau_K' / ladder beside 0029's, bootstrap -> results/e9c/summary.{md,json}
```

### e9_tail — per-token tail (read by the corrective entry 0045)

```
$PY -m linear_ceiling.e9_tail --config config/<cell>.toml       # runs summarize_e9 first (the gate), then the per-token TAIL from the same pinned records: tokens over each tau, means after removing the top 10/20 %, seam and position bin MEANS beside medians, native-window subset, |R| -> results/<cell>/tail.{json,md}, pinned to summary.json + report.json (W3/W4/W5; the corrective entry reads it)
```

## E-TRUNC — sender head truncation (registered 0055)

Runbook: `docs/2026-10-04-e-trunc-gpu-runbook.md`. Check the ledger tail and `docs/drafts/README.md` for whether
the figures entry has landed; claim no E-TRUNC result until it has.

```
$PY -m linear_ceiling.e9 --align-only --config config/e9t-<level>.toml   # the alignment pass per level (full / l65 / l49 / l32); the truncated levels see S' = S[-L:] via [e9.alignment] sender_head_truncate; inclusion is decided on the full |S| so every level keeps 0036's 35
$PY -m linear_ceiling.summarize_e9_trunc --shrinkage           # BEFORE any prefill, CPU: M_cap (tokens matched under every level) and |M_cap|/|M_FULL| per handoff from the four passes -> results/e9t/shrinkage.{json,md}; append_0055.py ran it in-process
$PY -m linear_ceiling.e9 --check --config config/e9t-<level>.toml        # gate per level: 0019/0023/0025/0027/0035/0055 committed, the four configs committed, upstream at 0036's pin 063f402, mapper by sha
$PY -m linear_ceiling.summarize_e9_trunc                        # after the four runs: summarize_e9 per level (fail-closed, the gate), then the paired comparison on M_cap, the |M_cap| >= 2000 void gate, and the registered +/-0.005 reading of L32's far-from-seam median against 0038 / 0036 (READ from results/e9s/compare.json and results/e9l/summary.json) -> results/e9t/compare.{json,md}
```

## Second model family — Llama long cell (registered 0050)

As written in entry 0050 (gate and reader for `config/e9fl.toml`); the short cell is entries 0042–0044 with
`config/e9f.toml`. Upstream pin `06f8d55`, one clone detached per cell (`UPSTREAM.md`). Whether the figures entry
has landed: the ledger tail and `docs/drafts/README.md`.

```
$PY -m linear_ceiling.e9 --align-only --config config/e9fl.toml   # the alignment pass 0050 cites (align/coverage.json)
$PY -m linear_ceiling.e9 --check --config config/e9fl.toml        # gate: 0019/0023/0025/0027/0050 committed, config committed unmodified, upstream at 06f8d55559257, mapper by sha
$PY -m linear_ceiling.e9 --close-partial --config config/e9fl.toml   # 0050's stopping rule: scored set must be a prefix of n_sender_asc
$PY -m linear_ceiling.summarize_e9 --config config/e9fl.toml      # fail-closed, the only reader; includes the native-window and per-role RoPE-identity controls
```

## GPU and backup tooling

Rules: `docs/gpu-experiment-protocol.md` R1–R12 and the run's own dated runbook. Runbooks:
`docs/2026-09-02-e9-gpu-runbook.md` (E9), `docs/2026-09-08-n420-target-dump-runbook.md` (n = 420 target dump),
`docs/2026-09-10-e9l-gpu-runbook.md` (E9-long), `docs/2026-09-13-e9s-gpu-runbook.md` (scaled short),
`docs/2026-09-18-llama-gpu-runbook.md` (second family), `docs/2026-09-30-consolidation-runbook.md` (same-model
extension, 0046), `docs/2026-10-01-cache-behavior-runbook.md` (cache behavior, 0047),
`docs/2026-10-04-e-trunc-gpu-runbook.md` (E-TRUNC).

```
tools/hf_backup.sh --check <repo_id> <staging_dir>        # run first: preflight only, uploads nothing
tools/hf_backup.sh <repo_id> <staging_dir>                # the R8 push: records, tree, card last; then the verifier
tools/hf_backup.sh --verify-only <repo_id> <staging_dir>  # preflight, then the verifier; uploads nothing
$PY tools/hf_verify_backup.py <repo_id> <local_root>       # exit 0 only when every file matches in both directions
$PY tools/hf_prune_backup.py <repo_id> <staging_dir>       # R8 repair: dry run; then --apply --expect-ops N, one delete commit
```

`tools/hf_backup.sh` retries only the Hub's 128-commits/hour 429; it refuses a missing dataset, a public one unless
`ALLOW_PUBLIC=1`, a concurrent upload or summarizer, and a token without the `hf_` prefix; it ends in
`tools/hf_verify_backup.py`, whose exit is the script's. Tokens come from the environment only (R9).

Box drivers: `tools/jupyterhub/` (a JupyterHub-only box, e.g. Algoverse, driven from home), `tools/ec2/` (a
rented EC2 GPU instance over ssh), `tools/runpod/` (the second family's RunPod sittings). Pre-rental checks:
`tools/preflight_pair.py` (a pair against its models' own config and tokenizer files, CPU-only) and
`tools/emit_tau.py` (a second family's τ lines from its own E8 report, before its config can load). The
consolidation (`tools/consolidation/`) and cache-behavior (`tools/cache_behavior/`) drivers are run as their
runbooks say.

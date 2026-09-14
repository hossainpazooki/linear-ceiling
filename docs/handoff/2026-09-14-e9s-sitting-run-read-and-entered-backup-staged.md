# Handoff — E9 scaled short cell: run on a rented L40S, both readers passed, 0038 appended, R8 backup staged

2026-09-14 ~03:45Z (session `e9l-aws-run`, the GPU-sitting session; the builds session's seed is
`docs/2026-09-13-seed-e9-scaled-short-cell.md`). Newest commit this brief describes: linear-ceiling `12c113c` = origin/main
(0037 at `c360950`, tooling `83419c8`, PR #4 merged) plus this session's UNCOMMITTED post-run work; upstream
`kv-transfer-replication` at `063f402`. Runbook with every timestamp and hash: `docs/2026-09-13-e9s-gpu-runbook.md` §6.

## Current state

- **verified — the sitting.** g6e.4xlarge (1× L40S 48 GB), us-east-1c, `i-03c1b238426ff218c`; setup from fresh clones at
  `12c113c` / `063f402`, `e9 --check --config config/e9s.toml` ready on the box (R1), R2 probe 16.70 GiB (1.7B) / 10.89 GiB
  (0.6B) at T = 32,768; driver 02:26:08Z → **EXIT=0 at 02:56Z**, 25 `[i/25]` lines, 0 Tracebacks, no partial close.
  re-verify: `grep -ac '^\[[0-9]*/25\]' results/e9s/logs/box/e9s.log` → 25; `cat results/e9s/logs/box/e9s.rc` → `EXIT=0`.
- **verified — mirror and release.** `tools/ec2/verify_mirror.py e9s` → 770/770 fingerprinted files, 48,927,599,343 B, ALL VERIFIED
  (report.json `abd1e456…`); the box's 196 small-record hashes all OK at home; R7 sweep rc 0 (nothing foreign, 0 tensors left,
  0 credential hits, HF cache removed); **terminated 03:09:57Z**, read back from EC2. ≈ $7.
  re-verify: `.venv/Scripts/python.exe tools/ec2/verify_mirror.py e9s`; `(cd results/e9s && sha256sum -c logs/box/e9s.records.sha256 | grep -vc ': OK$')` → 0.
- **verified — both readers passed at home.** `summarize_e9 --config config/e9s.toml` (after the τ calibration below): 25/25,
  keep-subset re-score within 0028's tolerance, same-model median f*(τ_K) 0.0000, cross K 0.9500, rule line HOLDS
  (descriptive). `e9_compare --native config/e9.toml --scaled config/e9s.toml --long results/e9l/summary.json`: 155,257 tokens,
  paired mean δ_K (scaled − native) median 0.0165 [0.0152, 0.0171]; configuration share 0.4285 (16+ seam bin) and 0.3916
  (τ = 0.03); τ = 0.1 share 0 by construction (both short medians 0). Native/long inputs cross-checked against 0029/0036's
  figures and the shares recomputed by hand (runbook 03:19:59).
  re-verify: rerun both commands (≈ 3 min each); `compare.json` → `a0699a82…` (deterministic across three runs).
- **verified — entry 0038 APPENDED** (chain `c9128ee936cd`, `ledger ok`; descriptive, no `verdict:` line, no row change;
  script retired). It states the two departures from 0037's text (calibration after the run; kept dumps in
  `results/e9s/scratch/`, not `results/e9/scratch/`).
  re-verify: `grep -n "^### 0038 " ledger/ledger.md` → line 2310; `.venv/Scripts/python.exe -m linear_ceiling.ledger_check` → `ledger ok`.
- **verified — R8 stage, NOT PUSHED.** `~/dev/hf-staging/linear-ceiling-e9s-2026-09-13/` = `results/e9s/` + mapper by hardlink +
  card; 980 = 980 files, 0 not hardlinked; mapper shas OK; credential sweep with a firing control: 0 hits; 49,478,265,328 B.
  The dataset `anon/linear-ceiling-e9s-2026-09-13` exists, public, empty (Hub API, 03:2xZ). Operator push below.
- **built — docs.** Runbook §6 through staging; learnings entry 2026-09-14 (the gate never checks the cell's τ calibration)
  + index row; `CLAUDE.md` and `tools/ec2/README.md` now name `--calibrate-tau` before launch; `tools/ec2/release_sweep.sh`
  allowlists `${EXP}.records.sha256` (was hard-coded `e9l`); drafts README, seed status line, README objective row.

## Deviations, stated

- **τ calibration written after the GPU run.** `summarize_e9` refused (`results\e9s\calibration\tau.json does not exist`);
  E9-long had run `--calibrate-tau` as a separate step on 09-09 and the e9s runbook omitted it. It reads no run artifact, the
  summarizer recomputes it against config, and τ came out identical to E9-long's at the same pin. In 0038 and the learnings entry.
- **Staging script's sweep died silently** on zero hits (`xargs grep -l` → 123 under `pipefail`); re-run by hand with a guard.
  The script lives in the session scratchpad only, not the repo.

## Open — not this session's to close

- **R8 push** (operator; token): commands below. Then add the e9s row to README's dataset table ("All three" → four).
- **Paper:** outline v3 §5.2 (lines ~171–190) still says "not attributable to length alone until the scaled short cell is
  measured". It is measured; 0037's reading gives "in between → the paper reports both". The paper session rewrites from 0038.
- **Corrective f* entry** (another session, 2026-09-11) still not on origin; README's H-E9 row still reads "f* = 0 at every
  matched token", which f*'s definition does not support ([[ledger-sentence-is-not-the-definition]] in operator memory).
- Paper condition 1 (co-author refutation of 0025–0029), unchanged.
- Not ours, untouched: stopped t3.micro `i-0785c090815238989` (`eks-instance`) in us-east-1; untracked `.claude/` (09-01 Track B
  patches) and `docs/paper/tex/` (`main.tex`, `refs.bib`, 09-13 23:18 local). Key pair `lc-e9l-2026-09-10` and SG
  `sg-03021d0b6c09b4c75` still exist (harmless, deletable).

## Invariants

`results/`, `data/`, `traces/` never enter history; `results/e9/` and `results/e9l/` untouched; `results/e9s/` written only by
the driver (box), the puller, the summarizer, `e9_compare` and the calibration; entries 0025–0038 immutable; no number enters
the ledger or paper that a reader did not produce; git history is the operator's. Never run a summarizer or an append while the
hardlinked stage is uploading.

## R8 backup — operator, from Git Bash, each line alone

```bash
read -s HF_TOKEN && export HF_TOKEN        # fine-grained WRITE token scoped to the dataset; nothing pasted after this line
~/dev/linear-ceiling/.venv/Scripts/hf.exe auth whoami
ALLOW_PUBLIC=1 ~/dev/linear-ceiling/tools/hf_backup.sh anon/linear-ceiling-e9s-2026-09-13 ~/dev/hf-staging/linear-ceiling-e9s-2026-09-13
```

Exit 0 = verified by `tools/hf_verify_backup.py` in both directions; exit 75 = rate-limited, rerun the same line after the hour.

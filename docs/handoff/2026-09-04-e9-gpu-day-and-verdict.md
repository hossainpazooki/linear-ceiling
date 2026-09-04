# Handoff — E9 GPU day and the H-E9 verdict (2026-09-04)

Read this first. Every claim here is re-verifiable from the tree; the ledger entries are the authority
and this brief only points at them.

## State

- linear-ceiling working tree on `0a19b56` plus uncommitted: entries **0028** and **0029** appended to
  `ledger/ledger.md` (chain ok), `summarize_e9` re-score tolerance + agreement figures, tests, two
  learnings entries, `docs/probes/`, `docs/drafts/append_0028.py` / `append_0029.py`, doc updates
  (CLAUDE.md program state, drafts README, runbook, this brief, HANDOFF row). Upstream
  `kv-transfer-replication` at `d5786df` (entry 0026's re-pin), pushed.
- **H-E9 = HELD** (0029): median f*(τ_K) on the same-model K arm 0.0000 on every one of 25 included
  handoffs; bootstrap [0, 0]; read on a floor (0027). Cross arm beyond the DEGRADES edge (descriptive).
- Results at home only: `results/e9/` — `report.json` (complete, 25/68), `scores/`, `tokens/` (727 MB),
  `controls/`, `align/`, `recheck/`, `summary.json`, `scratch/` with the 8 kept dumps (45 GB, fingerprints
  verified). `results/` never enters history. The box was released 18:30 UTC; it is deleted at 04:20 UTC.

## What happened, in order (each step has its record)

1. Pinned run (0023 pin `36d73b3`) OOMed at the first handoff: 51.49 GiB requested inside SDPA = 16 × 29,391² × 4 B,
   the float32 attention scores (transformers passes `enable_gqa`; PyTorch takes the math kernel in f32). Not the
   logits. → **0026** upstream re-pin `d5786df`: `sdpa_repeat_kv` attention + `logits_to_keep=1`; measured on the slice
   before the entry (probe table in 0026; `docs/probes/2026-09-04-sdpa-*.py`).
2. Second attempt died at the first score: the gitignored k=1 mapper artifact was not on the box → gate now refuses
   without it; runbook §3b.
3. **0027** before any score: cross-arm outcome named (descriptive), HOLDS-on-a-floor caveat, the kernel change as a
   bound (ε ≤ 2.2e-6 → ≤ 2.5e-6 in δ), box discipline; precondition names both refused runs and their deletion.
4. Run: 17:35–18:13 UTC, 25 handoffs, ~2 min each; puller mirrored everything home and deleted each kept dump on
   the box only after sha256 verification (`pull.py`, session scratch; described in runbook §5).
5. `summarize_e9` REFUSED: per-token squares of the home re-score vs the box record failed `rtol 1e-5, atol 0` on
   132 near-zero squares. Measured: same-model arrays reproduce **bit-for-bit** on Linux with the box's torch build;
   cross arrays move with thread count alone; f* unchanged everywhere (0028 table; `docs/probes/2026-09-04-rescore-*.sh`).
   → **0028** registers sums 1e-5 / squares 1e-2 and the summarizer reports the agreement figures.
6. Summary passed → **0029** (verdict), appended by `docs/drafts/append_0029.py` from the in-process summary.

## Locked decisions (do not reopen)

- The rule, τ_K = 0.3186, the band and the four cells are 0023's; nothing after 0023 moved them.
- 0028's tolerance is enforcement, registered post-run pre-verdict, with its basis measured (matching platform,
  determinism, thread count). Do not tighten or loosen it without a new entry and a new measurement.
- Verdict vocabulary is the ledger's: the cell says `HELD`; the band word is HOLDS.

## Reuse map

- `docs/2026-09-02-e9-gpu-runbook.md` — amended 09-04 (cu128 index, MIG, JupyterHub-only, mapper step, pull/verify/
  delete discipline, done-note). `docs/probes/` — the four probes, runnable.
- Driving a JupyterHub-only box from Windows: `jh.py` / `pull.py` in this session's scratch (8e4ab089); shape
  documented in memory `jupyterhub-box-driving`.

## Next

1. Commit set (operator): summarizer + tests + probes + learnings; ledger 0028/0029 + scripts; docs; then delete the
   two append scripts (README convention). CI must be green.
2. Learnings gate (`check-learnings`) was red on pre-existing entries before this session; the two new entries follow
   the format but were not run through it here.
3. `[STRETCH]` partial-prefill experiment on the retained dumps (0023) and the E8 amendment (queued, unnumbered).
4. Runbook pre-flight block still carries the 3-handoff figures in its body (superseded by the 09-04 amendment text).

## Re-verify

```
.venv/Scripts/python.exe -m linear_ceiling.ledger_check          # ledger ok
.venv/Scripts/python.exe -m linear_ceiling.summarize_e9          # passes; prints HOLDS, median f*(tau_K) same K 0.0000
.venv/Scripts/python.exe -m pytest -q                           # 382 passed, 1 skipped at hand-off time
grep -n "^verdict: H-E9" ledger/ledger.md                        # verdict: H-E9 = HELD (entry 0029)
```

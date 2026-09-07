# Handoff — pick-up of the sprint-close brief: 0031 and 0032 landed; 0033 and the §3.5 freeze both blocked on a ruling

2026-09-07 (session `73d64579-4856-4085-a6d8-19989f5bf384`, pick-up of `2026-09-07-lcfm-sprint-close.md`). Newest
commit this brief describes: linear-ceiling `6d20680` = origin/main plus the uncommitted work listed in the session
log's commit block. Upstream `kv-transfer-replication` at `0bff303` = origin (two Run 8 commits pushed by the operator
today; neither touches an invoked path), checkout back at `../kv-transfer-replication`. Supersedes the sprint-close
brief's "Open / next" item 1 only.

## Current state

- **built / verified** — the rename block is cleared: `e8 --check --config config/e8a.toml` reads ready; the chain ran
  `e8 --config config/e8a.toml` (10 min) → `summarize_e8 --config config/e8a.toml` (clean, 10 min) → `append_0031.py`
  → `append_0032.py`. 0031's header date was corrected from the draft's hard-coded 09-04 to the run date 09-07 before
  the final append (ledger restored to HEAD and re-appended; precedent 0020/0029 date the run). Both drafts retired.
  re-verify: `grep -n "^### 003[12]" ledger/ledger.md` → 0031 dated 2026-09-07, 0032 dated 2026-09-06; `-m linear_ceiling.ledger_check` → `ledger ok`; `results/e8a/summary.md` k = 1 row reads `0.5708 / 0.3230`, drop `+0.1106 / +0.1903`, `UNRESOLVED / DEGRADES`.
- **built / verified** — gates green on the edited tree: `pytest -q` → `401 passed, 1 skipped`; `lint_scope` → `scope ok`;
  `seal verify` → OK; `git diff --check` clean; learnings gate red on the same 7 pre-existing entries, 0 on today's.
- **built** — outline: §3.4 FROZEN with 0031's table beside 0020's; §3.5 and §5.1 rows state their blocks; freeze
  checklist header dated 2026-09-07. `docs/drafts/README.md` current-state sentence rewritten. Learnings entry
  `2026-09-07-a-config-comment-is-not-an-existence-check.md` + index row.
- **BLOCKED (found at pick-up)** — **0033/0034:** the n = 420 TARGET dump does not exist upstream. Only `source/`
  (28 layers, 12 GB) exists; `target/` is an empty directory; the upstream's own learnings entry of 2026-08-25 records
  the dump killed at 358/420 with zero bytes written (`dump_kv` writes only after its loop), never re-run.
  `config/e8c.toml`, `append_0033.py` (which asserts `target/meta.json`) and the outline all say "existing".
  re-verify: `cd ~/dev/kv-transfer-replication && .venv/Scripts/python.exe -c "from pathlib import Path; d=Path('data/kv/qwen3-0.6b-to-1.7b-n420'); [print(w, len(list((d/w).glob('layer*.npz'))), (d/w/'meta.json').exists()) for w in ('source','target')]"` → `target 0 False`.
- **BLOCKED (found at pick-up)** — **§3.5 freeze run:** `summarize_e9` REFUSES at upstream HEAD: its pin is `d5786df`
  (0026) and 0030's re-pin `223f469` changed `scripts/score_mapper.py` and added `kvt/pertoken.py`, both on E9's
  invoked-path list. Present since 09-04; recorded nowhere until today. 0032 admits E9 only "from a run that passes
  every check", so E9 is not in the 4-pager as things stand.
  re-verify: `.venv/Scripts/python.exe -m linear_ceiling.summarize_e9` → `E9 SUMMARY REFUSED: upstream paths ... changed between the pin d5786df91f55 and HEAD`; `cd ~/dev/kv-transfer-replication && git diff --stat d5786df 223f469 -- scripts/score_mapper.py kvt` → 2 files changed.

## Locked decisions — premises checked

- **Rename back, not re-path** — done by the operator; premise held.
- **Calibration-size shape on "the existing n = 420 dumps"** — premise CONTRADICTED (target half never existed). Not
  relitigated here; the fit was not run and 0033's prose was not edited. Ruling needed: re-dump the target (~2 h CPU
  detached, or minutes on the Algoverse GPU in fp32 with the pinned code, then a 12 GB pull) and amend 0033's
  "pre-existing" wording to state the two halves' provenance (source CPU 12 threads 08-24, target GPU/CPU 09-07;
  08-24 learning: fp16-ULP differences across thread counts), or drop §5.1 from the freeze.
- **E9 in the 4-pager (0032)** — premise ("behind the summarizer gate") holds only if the gate can be run; it cannot at
  upstream HEAD. Ruling needed: run `summarize_e9` with the upstream checked out at `d5786df` (a detached checkout;
  the gate compares HEAD; restore `main` after), or register a re-pin entry. Not done here: CLAUDE.md names the
  upstream read-only and a checkout changes its working tree.
- **E9's 4-pager section is conditional on the co-author refutation** — still not recorded; the conditional stands.
- **Numbering by staging order** — 0031, 0032 appended; 0033, 0034 remain the staged numbers.

## Reuse map

- `results/e8a/{report,summary}.{json,md}` — 0031's inputs, local by rule; `summary.md` is the table the outline quotes.
- `docs/drafts/append_0033.py`, `append_0034.py` — still staged; 0033's asserts at lines 32–45 are the guard that found the dump.
- `tools/jupyterhub/` + `docs/2026-09-02-e9-gpu-runbook.md` — the driver and box facts if the target dump goes to the GPU.
- `config/e9.toml` line 12 (E9's pin) vs `config/e8a.toml` / `e8c.toml` / `e9c.toml` (0030's pin) — the two-pin state behind the §3.5 block.
- Reviewer assessment of the upstream (pasted 2026-09-07, unattributed, likely LLM-assisted): its item 7 is answered by the upstream's Run 8, now on origin at `0bff303`; items 2, 3, 5, 6 touch the 4-pager's §3.4/§3.5 foundations; a compute plan is in the session log.

## Invariants (unchanged)

`results/`, `data/`, `traces/` never enter history; `results/e8/`, `results/e9/` never rewritten; amendments write only
under `results/e8a/`, `results/e8c/`, `results/e9c/`. No number enters the ledger or the 4-pager that a summarizer did
not produce. Entries 0025–0029 immutable. `UPSTREAM.md` = `UPSTREAM_SHA` = `223f469` (E8 family); E9's own pin `d5786df`
lives in `config/e9.toml`. Double-blind rules.

## Open / next

1. **Operator:** the commit block in the session log; then two rulings — (a) n = 420 target dump: re-dump + amend, or
   drop §5.1; (b) §3.5 freeze: detached checkout at `d5786df` for one `summarize_e9` run, or a re-pin entry.
2. If (b) = detached checkout: `cd ~/dev/kv-transfer-replication && git checkout d5786df && cd ~/dev/linear-ceiling &&
   .venv/Scripts/python.exe -m linear_ceiling.summarize_e9 && cd ~/dev/kv-transfer-replication && git checkout main`;
   then the outline's §3.5 row → FROZEN with the run date. E8-family gates need `main` (223f469 ancestry) restored.
3. If (a) = re-dump: 0033's registration is the prereg and the dump is an input; launch detached, never under a harness
   timeout; pull home; re-run the 08-24 nesting check on the new target; then `append_0033.py` (after its prose
   amendment) → fit → `e8 --config config/e8c.toml` → summarize → `e9_rescore run` → `summarize` → `append_0034.py`.
4. Freeze EOD 2026-09-08; 4-pager; PI review. Co-author refutation of 0025–0029 still owed. `check-learnings` red on 7
   pre-existing entries. The Algoverse GPU re-request is immediate this month (operator, 2026-09-07).

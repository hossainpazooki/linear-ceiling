# Handoff — LCFM sprint staged (outline, 0032–0034, calibration-size instrument); every run blocked on one rename

2026-09-06 23:30 UTC. Newest commit this brief describes: linear-ceiling `7ce63cf` = origin/main, with this session's work
UNCOMMITTED in the working tree (file list under Current state; commit block at the end of the session log). Upstream
`kv-transfer-replication` at `223f469` (0/0 with origin) but living at `~/dev/kv-transfer` since 2026-09-06 12:49 local.
Pick-up measures drift from `7ce63cf` and from the directory name.

## The one blocker

`~/dev/kv-transfer-replication` was renamed to `~/dev/kv-transfer` on 2026-09-06 at 12:49:13 local, in the same second
`~/dev/traverse/` appeared (another session reorganizing the workspace; actor not established). Every `upstream_path`
(e8, e8a, e8c, e9, e9c, seal) is `../kv-transfer-replication`; the upstream's editable install still maps `kvt` to the old
path (7 of its `tests/test_scripts.py` fail with `No module named 'kvt'`; 138 pass). `mv` back was refused with
`Permission denied`: running Claude Code sessions hold handles on every depth-1 repo (memory note `claude-locks-depth1-repos`).
**Operator ruling: rename back.** Close every Claude Code session on the machine, then in Git Bash:
`cd ~/dev && mv kv-transfer kv-transfer-replication && ls -d kv-transfer-replication/.git`.
re-verify: `ls -d ~/dev/kv-transfer-replication/.git` exists; `cd ~/dev/kv-transfer-replication && .venv/Scripts/python.exe -m pytest -q` → `145 passed`; `cd ~/dev/linear-ceiling && .venv/Scripts/python.exe -m linear_ceiling.e9 --check` prints READY.

## Current state

- **verified** — pick-up of the two 09-05 briefs: 0030 landed (`e844516`), CI green on both pushes, `UPSTREAM_SHA` = e8a pin
  = upstream HEAD `223f469`; 0020's agent dumps + token file + manifest match `results/e8/report.json` (sha `5c4e70a097c2`);
  `results/e8a/` absent; E9 mirror `results/e9/report.json` sha `1b2153e3…feda29`. HF backup NOT re-verified (no token in env).
  re-verify: the 09-05 briefs' own lines, all of which held except the upstream suite (path) and the e8a gate (path).
- **built / verified** — `docs/2026-09-06-gap-map-revisited.md` (the 08-26 gap map read against the ledger at 0030; table up
  top; every figure grepped into its cited entry; the "who's nearby" attribution footnote is UNCLOSED — no lit-sweep verdict
  is on the record). README docs map row added.
  re-verify: `.venv/Scripts/python.exe -m linear_ceiling.lint_scope` → `scope ok`; the doc's figures vs `ledger/ledger.md` by grep.
- **built** — `docs/paper/2026-09-06-lcfm-outline.md`: the 4-pager outline (LCFM @ NeurIPS 2026, deadline 09-10 AoE, 4 pages,
  double-blind, non-archival, dual submission allowed — CFP checked at source 09-06, silent on negative results; topic hook
  "Robust evaluation"). Gap-map preface; every figure with entry + freeze status; **registered reading for H-E7a (ruling
  09-06)**; anonymity rules; page budget. E7 figures FROZEN (`summarize_e7` ran clean 09-06, 11 s); E8 PENDING 0031; E9
  PENDING 0032 + the co-author leads; §5.1 PENDING 0033/0034.
- **built** — `docs/drafts/append_0032.py`: E9 admitted to the 4-pager on 0016's terms (descriptive; guards: 0031 present,
  `results/e9/summary.json` reads 25 included; the E9 section is cut to one "ongoing" sentence if the co-author refutation is
  not recorded by the freeze).
  re-verify: `.venv/Scripts/python.exe -m py_compile docs/drafts/append_0032.py` exits 0.
- **built / tested** — calibration-size sensitivity instrument (entry 0033, registration script staged; 0034 figures script
  staged): `E8Config.mapper_tag` (tagged mapper `mappers/<pair>/<tag>/k<k>` + tagged archived `r2.json`; `mapper` fingerprint
  block in every E8 report, re-checked by `summarize_e8`), `config/e8c.toml` (0030's protocol, generic arm on the n = 420
  dumps, agent dumps via 0031's report, results/e8c), `linear_ceiling.e9_rescore` (`check`/`run`/`summarize`: the 8 kept
  handoffs re-scored with the tagged mapper; **same-arm control refuses** unless the same-model squares reproduce 0028's
  recheck within 0028's tolerance; cross f* under τ_K / τ_K′ / ladder / τ_agent_K beside 0029's recomputed from 0028's
  record; τ_K′ from the E8 report scored with byte-identical mapper files), `config/e9c.toml`. `upstream_gate` now refuses by
  name on a missing checkout instead of raising NotADirectoryError.
  re-verify: `.venv/Scripts/python.exe -m pytest -q` → `401 passed, 1 skipped`; `ledger_check` → `ledger ok`; `git diff --check` clean;
  `e8 --check --config config/e8c.toml` → `E8 REFUSED: config/e8c.toml is not committed as-is` (designed state before the commit).
- **planned (blocked on the rename, in this order)** — `e8 --check --config config/e8a.toml` READY → `e8 --config config/e8a.toml`
  (~10 min CPU) → `summarize_e8 --config config/e8a.toml` → `append_0031.py` → `append_0032.py` → `append_0033.py` (refuses if
  the tagged mapper already exists: register BEFORE the fit) → upstream fit
  `scripts/fit_mapper.py --pair qwen3-0.6b-to-1.7b --k 1 4 8 --tag n420 --dump-root data/kv/qwen3-0.6b-to-1.7b-n420` at `223f469`
  (upstream's own venv; artifacts are gitignored there) → `e8 --config config/e8c.toml` → `summarize_e8 --config config/e8c.toml` →
  `e9_rescore run` → `e9_rescore summarize` → `append_0034.py` → retire 0031–0034 scripts, drafts README current-state line →
  numbers-freeze EOD 2026-09-08 → 4-pager from the outline → PI review (arranged by the Algoverse Program Director).
- **open, not this repo's** — Ritvik's refutation of 0025–0029 (two leads first: τ-ladder sensitivity; the exactly-zero prefix
  control); the write token used 09-04/05 to be revoked; a scoped read token for Ritvik; the author list for the anonymity check.

## Locked decisions (operator, 2026-09-06)

- **Rename back, not re-path.** Reason: zero config change; the editable install, every config, UPSTREAM.md, CLAUDE.md and
  the runbook are all correct at the old name. A junction was explicitly NOT created (the 09-02 learning: a recursive delete
  goes through a junction).
- **Go on the calibration-size entry; E9 in the 4-pager; registered reading for H-E7a; outline in `docs/paper/`; the gap-map
  preface frames the LCFM target.** Reasons in the session log; the request-level reading of 0024 appears once, in Limitations.
- **Calibration-size shape (assumptions stated, not objected to):** k = 1/4/8 fit at n = 420 under one tag, k = 1 compared;
  E8 both arms under 0030's protocol; E9 cross arm on the 8 kept handoffs only; τ_K′ reported beside 0023's τ_K, never
  substituted; everything descriptive; the n = 50 record stays the decided one.
- **Register before the fit.** `append_0033.py` refuses if `mappers/<pair>/n420/` or the tagged `r2.json` exists; the fit runs
  only after 0033 is on the record.
- **Numbering by staging order** (drafts README): 0031 E8 figures, 0032 E9 admission, 0033 calibration registration, 0034 its figures.

## Reuse map

- `docs/drafts/append_0030.py` → the registration-script shape; `append_0031.py` → figures-from-summarizer shape.
- `linear_ceiling.e9_rescore._same_arm_control` — the mapper-independent control; `summarize_e9._rescore_agreement` is its parent.
- `linear_ceiling.e8.mapper_path` / `mapper_fingerprint` — tagged artifact resolution and bytes.
- `docs/2026-09-06-gap-map-revisited.md` table — the preface's source; `docs/paper/2026-09-06-lcfm-outline.md` freeze checklist.
- Memory notes: `linear-ceiling-e8-amendment`, `linear-ceiling-team`, `claude-locks-depth1-repos`.

## Invariants

- `results/`, `data/`, `traces/` never enter history; `results/e8/` and `results/e9/` are never rewritten (E9's τ calibration
  and 0028's recheck are read from them); the amendments write only under `results/e8a/`, `results/e8c/`, `results/e9c/`.
- No number enters the ledger that a summarizer did not produce; the outline's slots stay slots until then.
- `UPSTREAM.md` holds exactly one full sha, equal to `linear_ceiling.UPSTREAM_SHA`; no re-pin is needed for 0033.
- Entries 0025–0029 are immutable; refutation is recomputation.

## Open / next

1. **Operator:** close sessions → rename → reopen → run the commit block (session log) → CI green → the planned chain above.
2. **Operator:** Ritvik's read token + the artifact share; revoke the write token.
3. Whoever holds the pen: the 4-pager from the outline once 0031 (and 0032/0034 if they land) are on the record.
4. Still open elsewhere: `check-learnings docs/learnings` is red on 7 pre-existing entries (3 ts-vs-filename dates, 4 missing
   `status`); the lit-sweep verdict for the gap map's attributions; the `[STRETCH]` partial-prefill experiment.

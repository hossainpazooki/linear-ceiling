# Handoff — LCFM sprint: everything staged and committed; one rename gates every run

2026-09-07 04:00 UTC. Newest commit this brief describes: linear-ceiling `74c35fd` = origin/main, tree clean except
this brief, two learnings entries and their index rows (untracked; commit block in the session log). Upstream
`kv-transfer-replication` at `223f469` = origin, but the checkout lives at `~/dev/kv-transfer` (renamed 2026-09-06
12:49 local). Supersedes `2026-09-06-lcfm-sprint-staged-and-path-blocked.md` (same session, written before the four
commits landed and before the README rewrite); that brief's file list is now history `6f7c2ec..74c35fd`.
Pick-up measures drift from `74c35fd` and from the directory name.

## Current state

- **built / verified** — four commits landed and pushed by the operator: `6f7c2ec` (gap map revisited, LCFM outline,
  README rewritten to aims + status, 72 lines), `4eb2a04` (upstream gate refuses by name on a missing checkout),
  `b37914d` (calibration-size instrument; drafts 0032–0034 staged), `74c35fd` (the 09-06 brief + rename learnings).
  re-verify: `git log --oneline -4` shows exactly those four above `7ce63cf`; `git status -sb` → `## main...origin/main` with no ahead/behind.
- **built / verified** — gates green at `74c35fd`: suite, scope lint, ledger chain, seal, whitespace.
  re-verify: `.venv/Scripts/python.exe -m pytest -q` → `401 passed, 1 skipped`; `-m linear_ceiling.lint_scope` → `scope ok`; `-m linear_ceiling.ledger_check` → `ledger ok`; `git diff --check` clean.
- **built / verified** — E7 figures are freeze-ready: the summarizer reproduces the record from raw traces.
  re-verify: `.venv/Scripts/python.exe -m linear_ceiling.summarize_e7 | grep "0.20%"` → the H-E7a line, `BELOW the cutoff` (~11 s).
- **built** — `docs/paper/2026-09-06-lcfm-outline.md` (gap-map preface; registered reading for H-E7a; every figure tagged
  FROZEN / PENDING / NOT IN; anonymity rules; page budget); `docs/2026-09-06-gap-map-revisited.md` (verdict table up top;
  attribution footnote recorded as unclosed).
  re-verify: `grep -c "PENDING" docs/paper/2026-09-06-lcfm-outline.md` > 0 until 0031/0032/0034 land; `grep -n "never closed\|UNCLOSED\|not closed" docs/2026-09-06-gap-map-revisited.md` names the footnote.
- **built** — drafts staged in `docs/drafts/`: `append_0031.py` (E8 amendment figures), `append_0032.py` (E9 admitted to the
  4-pager), `append_0033.py` (calibration-size registration; refuses if the tagged mapper already exists), `append_0034.py`
  (its figures from both summarizers in-process). All compile; all refuse until their ordering guard holds.
  re-verify: `for f in docs/drafts/append_003[1-4].py; do .venv/Scripts/python.exe -m py_compile $f; done` exits 0; `grep -c "^### 003" ledger/ledger.md` → 1 (only 0030 on the record).
- **built / tested** — instrument for 0033: `E8Config.mapper_tag` + `config/e8c.toml`; `linear_ceiling.e9_rescore` +
  `config/e9c.toml` (same-arm control refuses unless the same-model squares reproduce 0028's recheck within 0028's tolerance).
  re-verify: `.venv/Scripts/python.exe -m pytest -q tests/test_e9_rescore.py tests/test_e8.py tests/test_summarize_e8.py tests/test_upstream_gate.py` → `35 passed`; `.venv/Scripts/python.exe -m linear_ceiling.e9_rescore check` on the clean tree → `E9 rescore REFUSED: committed ledger has no entry 0033` (the designed state: both configs are committed at `b37914d`, 0033 is not appended yet).
- **built** — learnings entries this session (3): the workspace rename (09-06), the unclosed attribution footnote and the
  LCFM CFP silence (09-07). The learnings gate passes on all three; it is still red on 7 pre-existing entries.
  re-verify: `node ~/dev/rigor/scripts/check-learnings.mjs docs/learnings 2>&1 | grep -c "2026-09-0[67]"` → 0.
- **not started (blocked)** — everything that touches the upstream: `e8 --config config/e8a.toml` → 0031; 0032; 0033; the
  upstream fit under tag `n420`; `e8 --config config/e8c.toml`; `e9_rescore run`; 0034. Nothing on this list can run until
  the upstream checkout is back at `../kv-transfer-replication`.
  re-verify: `ls -d ~/dev/kv-transfer-replication/.git` → missing until the rename; `.venv/Scripts/python.exe -m linear_ceiling.e8 --check --config config/e8a.toml` → `E8 REFUSED: upstream checkout ... does not exist`.

## Locked decisions (operator, 2026-09-06)

- **Rename back, not re-path.** Reason: every config, UPSTREAM.md, CLAUDE.md, the runbook and the upstream's own editable
  install are correct at the old name; a re-path is a post-registration edit of registered configs. `mv` was refused
  (`Permission denied`) because running Claude Code sessions hold handles on depth-1 repos: close every session, then
  `cd ~/dev && mv kv-transfer kv-transfer-replication`. No junction (09-02 learning).
- **Go on the calibration-size entry (0033/0034); E9 in the 4-pager (0032); registered reading for H-E7a; outline in
  `docs/paper/`; gap-map preface; README minimal (aims + status only).** Reasons in the session log and the outline header.
- **Calibration-size shape:** k = 1/4/8 fit at n = 420 under one tag, k = 1 compared; E8 both arms under 0030's protocol with
  the change measured from 0031's all-sequence figures; E9 cross arm on the 8 kept handoffs only; τ_K′ reported beside
  0023's τ_K, never substituted; everything descriptive; the n = 50 record stays decided.
- **Register before the fit.** `append_0033.py` refuses if `mappers/<pair>/n420/` or the tagged `r2.json` exists.
- **Numbering by staging order** (drafts README): 0031, 0032, 0033, 0034.
- **E9's 4-pager section is conditional:** if Ritvik's refutation of 0025–0029 is not recorded by the freeze (EOD 09-08),
  the section is one sentence marked ongoing and the figures are withheld (written into 0032's text).

## Reuse map

- `docs/drafts/append_0030.py` / `append_0031.py` — registration and figures-from-summarizer shapes; 0033/0034 follow them.
- `linear_ceiling.e9_rescore._same_arm_control` — the mapper-independent control; `summarize_e9._rescore_agreement` its parent.
- `linear_ceiling.e8.mapper_path` / `mapper_fingerprint`; `summarize_e8` re-checks the `mapper` block.
- `docs/paper/2026-09-06-lcfm-outline.md` "Freeze checklist" — the table to update as figures freeze.
- `docs/2026-09-06-gap-map-revisited.md` table — the preface's source.
- Memory notes: `linear-ceiling-e8-amendment`, `linear-ceiling-team`, `claude-locks-depth1-repos`.

## Invariants

- `results/`, `data/`, `traces/` never enter history; `results/e8/` and `results/e9/` are never rewritten (E9's τ calibration
  and 0028's recheck read them); amendments write only under `results/e8a/`, `results/e8c/`, `results/e9c/`.
- No number enters the ledger or the 4-pager that a summarizer did not produce; the outline's slots stay slots until then.
- Entries 0025–0029 are immutable; refutation is recomputation. 0032–0034 carry no `verdict:` line.
- `UPSTREAM.md` holds exactly one full sha equal to `linear_ceiling.UPSTREAM_SHA`; 0033 needs no re-pin.
- Double-blind: no repo name, HF dataset name, handle or artifact link in the submission.

## Open / next

1. **Operator:** close sessions → `mv kv-transfer kv-transfer-replication` → reopen → `/rigor:pickup` on this brief → run the
   chain in order: `e8 --check --config config/e8a.toml` → `e8 --config config/e8a.toml` (~10 min) → `summarize_e8 --config
   config/e8a.toml` → `append_0031.py` → `append_0032.py` → `append_0033.py` → upstream `scripts/fit_mapper.py --pair
   qwen3-0.6b-to-1.7b --k 1 4 8 --tag n420 --dump-root data/kv/qwen3-0.6b-to-1.7b-n420` (upstream venv, at `223f469`) →
   `e8 --config config/e8c.toml` → `summarize_e8 --config config/e8c.toml` → `e9_rescore run` → `e9_rescore summarize` →
   `append_0034.py` → retire the four scripts + drafts README line → commit → freeze EOD 09-08 → 4-pager → PI review.
2. **Operator:** Ritvik's read token + the artifact share; revoke the write token; fix the author list.
3. **Open:** the lit-sweep verdict for the gap map's attributions (learnings 09-07); `check-learnings` red on 7 pre-existing
   entries; the `[STRETCH]` partial-prefill experiment.

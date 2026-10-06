# linear-ceiling — agent contract

A pre-registered experiment record on KV-cache reuse at agent handoffs. `README.md` explains the science;
`docs/2026-08-26-kv-handoff-screen-design.md` is the authority on scope; `ledger/ledger.md` is the source of truth
for hypotheses, rules, results and verdicts. This file holds only the stable rules. Commands:
`docs/agent/experiment-commands.md`. Modules and layout: `docs/agent/repo-architecture.md`.

## Invariants — never break these
- `../kv-transfer-replication` is **read-only** and pinned (`UPSTREAM.md`). Never write there, never `import kvt`,
  never copy its code; it is invoked only by subprocess. Borrowed facts carry `{sourceRepo, filePath, commitSha}`.
- `ledger/ledger.md` is append-only by numbered entry and hash-chained in file order; `ledger_check --against <rev>`
  makes the trailing entry immutable too. A verdict cell changes only through an entry with a `verdict:` line.
- Never write a number into the ledger that was not recomputed from `results/` by a summarizer. Summarizers are
  fail-closed; a refusal is a finding, not an obstacle to route around.
- Never edit a hypothesis after its experiment starts; never edit a sealed prediction.
- Seeds and thresholds live in `config/*.toml`; a registered config is committed unmodified before its run and
  its gate checks that. Randomness only via `linear_ceiling.rng.make_rng`.
- One owner per rule: upstream pins only via `upstream_gate`, quantiles only via `e7_stats`, entry numbers only
  via `docs/drafts/README.md`.
- `traces/`, `results/` and `data/` never enter git history.

## Domain traps — the rules newcomers break first
- Lane A ALONE decides H-E7a; Lane B never resolves anything (0007/0010).
- Unmeasurable is never a zero: every taxonomy class carries its own NOT MEASURABLE state (0006).
- A narrow detector is a defect, not a null: search `model|model_id|model_name` at minimum (0010).
- A trajectory is one agent run on one task instance, not one file (0011).
- Every trace-only cost figure is a LOWER BOUND and headroom an UPPER BOUND, both labelled (0010/0012).
- Per-token deviation is in R²'s own units (a token's share of unexplained variance), never a per-token percent
  error (0023).
- f*(τ) = 0 is a statement about each handoff's MEAN deviation, not a guarantee that no token exceeds τ (0045).
- Quantiles come only from `e7_stats` (lower nearest-rank, no interpolation); a second convention silently moves
  a p90.
- Entries 0006–0023 are the authority: read them whole before touching E7/E8/E9 code.

## Paper-facing claims
- A scientific figure or claim enters paper text only through the admitted evidence path: a ledger entry that
  states it, or a document a ledger entry explicitly admits for citation.
- Co-author pilot figures admitted for paper citation by entry 0056 carry the provenance language that entry
  specifies. Paper-citation admission does not by itself make them ledger figures; ledger admission still follows
  the registered entry / draft path.
- The registered reading of f* is in entries 0023 and 0027, and 0054 records how a contrary reading would have to
  enter. When a review record, draft or manuscript disagrees with a registered reading or an operator ruling,
  report the conflict and leave it to the operator. Do not resolve it in text.
- "Lean" may be claimed in the paper only after `lake build` has passed on the committed tree (`proofs/`).

## GPU runs
`docs/gpu-experiment-protocol.md` (R1–R12) governs every GPU experiment, and each run has a dated runbook. Never skip:
- Registered before requested: no rule, τ, band or cap change once a score file exists (R1).
- Budget the attention backend, not the parameters: f32 + GQA takes the math kernel (R2).
- Every input the driver reads is in git, the manifest, or listed by sha in the runbook, gitignored mappers too (R3).
- Launch detached, rotate the log before any relaunch, never `pkill -f` a self-matching pattern (R4).
- Pull → verify against `report.json` `kept_dumps` → delete, per handoff; nothing exists only on the box (R5/R6).
- Release by the R7 checklist in order, starting with step 0 (the account is shared until proven otherwise):
  mirror re-verified, box swept, HF cache removed, server stopped and the effect probed.
- Back the verified home mirror up to an HF dataset, every file checked by `lfs.sha256` (R8). The backup is
  transport only: summarizers read the local mirror.
- Hub tokens: scoped, expiring, environment-only, revoked once pasted anywhere (R9).

## Where to read current state
Not restated here; it changes too fast. Read, in order:
1. `ledger/ledger.md`: the hypothesis table, then the entries its cells cite.
2. `docs/handoff/HANDOFF.md`: the newest brief is the pick-up target, but re-verify it against the repo rather
   than treating it as evidence.
3. `docs/drafts/README.md`: staged entries, file order, the next free number (the only allocator).
4. The experiment's runbook (`docs/*-runbook.md`) and `docs/gpu-experiment-protocol.md`.

## Before changing anything
- Run `git status`: parallel sessions leave uncommitted work in this tree. Commit by explicit paths.
- Re-read `docs/drafts/README.md` before staging an entry; parallel sessions have collided on numbers.
- Ledger entries, handoff briefs and learnings entries are immutable; a correction is a new one.
- Leave to the operator, or do only on the operator's explicit instruction: appending an entry or running an
  `append_00NN.py` script, taking or reinterpreting a ruling, requesting or releasing a GPU box, pushing to or
  changing the visibility of a Hub dataset, re-pinning the upstream, editing a registered config.

## Common checks — the definition of done
`$PY` is the repo venv: `.venv/Scripts/python.exe` (Windows) or `.venv/bin/python` (Linux/macOS). If it is missing,
say so; never substitute another environment for a scientific run.
```
$PY -m pytest -q                       # synthetic, offline
$PY -m linear_ceiling.seal verify
$PY -m linear_ceiling.lint_scope
$PY -m linear_ceiling.ledger_check
```
A green suite proves the tools work, not a scientific claim.

## Repo map
- `src/linear_ceiling/`: instruments, gates and fail-closed summarizers. `tests/` mirrors it (synthetic, offline).
- `config/`: registered experiment configs and manifests. `ledger/ledger.md`: the record.
- `docs/handoff/` briefs · `docs/drafts/` append scripts + allocator · `docs/reviews/` review records ·
  `docs/learnings/` re-verifiable learnings · `docs/paper/` outlines (the manuscript is not in this repo).
- `docs/gpu-experiment-protocol.md` + dated runbooks · `docs/agent/` commands and architecture.
- `tools/`: GPU box drivers, HF backup push/verify, pilot code. `proofs/`: the Lean 4 formalization.
- `UPSTREAM.md`: the pin chain and the provenance table for everything borrowed.

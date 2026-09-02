# Handoff — Track B: manifest, ledger lint gaps, overlap nulls, cache-aware ratio (build complete; appends pending 0023)

**Date:** 2026-09-01 (late)
**Describes:** the working tree of the git worktree `.claude/worktrees/track-b-recon` (branch
`worktree-track-b-recon`) on top of `f48b536`, uncommitted; the operator commits from the per-item
patch sequence below. Pick-up measures drift from `f48b536` plus these patches.
**Seed:** "Track B: the six major review issues, in order" (2026-09-01). Track A owns `e9*`,
`summarize_e9`, `config/e9.toml`, the GPU runbook, the upstream `score_positions.py` change and its
re-pin, and **entry 0023**; none of those files was touched here.

## Current state

**built — #6 corpus manifest.** `config/e7-manifest.json`: one record per file the corpus walk
touches (188), sha256 + bytes, and for the 180 SWE-bench objects the S3 key/ETag/size from the
anonymous listing (retrieved 2026-09-01T23:41:46Z). `e7.assert_ready` requires it committed as-is;
`e7.build_report` and `summarize_e7` refuse on any disk/report/manifest disagreement; `ledger_check`
requires every entry >= 0024 that cites `summarize_e7` to carry `e7-manifest-sha256:` naming the
committed manifest. The manifest sha is the canonical-JSON hash (CRLF-safe).
re-verify: `.venv/Scripts/python.exe -m linear_ceiling.e7_manifest check` → `manifest ok: 188 files match disk; sha256 371fb4bf3cb0…`
re-verify: `.venv/Scripts/python.exe -m pytest -q tests/test_e7_manifest.py` → 12 passed

**found — the SWE-bench selection rule, recovered.** Every submission's local set is exactly the
first N objects of its S3 listing (positions 0..N-1, all seven submissions). Listing order is UTF-8
key order, so the subset is the **alphabetically first N instances** of each submission (astropy-
dominated) — a rule, not a random draw. No bearing on Lane A (all 60 composio files present); the
pooled SWE-bench taxonomy rows now carry the label `SELECTED SUBSET` in the summary.
re-verify: `.venv/Scripts/python.exe -m linear_ceiling.summarize_e7 | grep -c "rule: first-N in listing order"` → 7 (needs local `traces/`)

**built — #6b provenance hash portability.** `config_sha256` was the raw-bytes digest, so a CRLF
checkout (this worktree) recorded `9c488cc3…` where the ledger cites `6915666d…`. `hashing.sha256_text_file`
(newline-normalized) is now used for E7's config sha; equal to the raw digest for LF files, so
every recorded value stays valid. E8/E9 still use the raw digest (Track A's files / #5 stopped).

**built — #1 ledger lint gaps.** `ledger_check` now (3) refuses any edit to an entry block committed at
a base revision (`--against <rev>`, default HEAD; CI passes the push/PR base, fetch-depth 0; an
unreadable base FAILS), so the trailing entry is as immutable as the chained ones; (4) requires every
verdict cell to equal the value set by a numbered entry — a frozen map through 0022
(`VERDICT_PROVENANCE`, one comment per entry naming its wording) plus `verdict: H-XX = <VERDICT>`
lines from 0024 on (reopening = `= unresolved`). Both adversarial edits from the review are pinned as
tests; the current ledger passes; README invariant 2 states exactly what is enforced and the residuals
(squash-merge net change; history rewrite).
re-verify: `.venv/Scripts/python.exe -m linear_ceiling.ledger_check --against f48b536` → `ledger ok (blocks unchanged vs f48b536)`
re-verify: `.venv/Scripts/python.exe -m linear_ceiling.ledger_check --against deadbeef` → exit 1, `cannot read ledger/ledger.md at 'deadbeef'`
**Track A must know:** the H-E9 verdict entry (whatever its number) must carry `verdict: H-E9 = <VERDICT>`
or `ledger_check` refuses the cell change.

**built — #2 overlap null controls.** `summarize_e7 --overlap-null` (seed in `config/e7.toml
[e7.overlap_null]`, so the config sha moved to `d16cf4659aab`): same-family null (seeded derangement
over composio ids, partner switch by ordinal) and cross-family null (seeded draw from the 64
role/content SWE-bench trajectories' full text), same measure via `e7_headroom.switch_slices` (shared
with the observed measure so the nulls cannot drift), same quantile convention. On the real corpus:
observed 0.988 (p10 0.972, p90 0.994); same-family 0.498 (0.311, 0.574); cross-family 0.386 (0.205,
0.499); upper bound as fraction of paid 88.9% / 44.9% / 34.7%. NOT COMPUTABLE where a null cannot be
formed (never zero).
re-verify: `.venv/Scripts/python.exe -m linear_ceiling.summarize_e7 --overlap-null` → the three-row table above (needs local `traces/`)

**built — #3 cache-aware readings of the H-E7a denominator.** `summarize_e7 --cache-aware-ratio`
reports the ratio under registered requests (each assistant turn re-bills the trajectory prefix —
the 0015/0018 pricing) and request-level requests (0017's `paid` applied to every request), each cold
and warm (byte-identical prefix vs the preceding request at read_mult). Real corpus, numerator
496,798 unchanged: registered cold 244,739,122 → **0.20%** (= 0018 by construction); registered
warm 27,354,947 → 1.82%; **request-level cold 4,967,377 → 10.0012% — AT the 10% cutoff**;
request-level warm 5,775,842 → 8.60% (only 7.6% of request-level prefill is a shared byte-identical
prefix, and write_mult 1.25 > 1 makes warm exceed cold). Independently recomputed by a second walk of
the corpus: denominator 4,967,377 exact, and all 68 switch rows' receiver prefill equal the
request-level prompt tokens (557,863 both ways, 0 mismatches).
re-verify: `.venv/Scripts/python.exe -m linear_ceiling.summarize_e7 --cache-aware-ratio` → the four-column table (needs local `traces/`)

**built — #4 wording.** README intro + H-E7a findings row and CLAUDE.md say the finding is about
what public *benchmark* traces evidence (Lane A measurable on 60 of 2,904 trajectories, one designed
critic stage), not production workloads; 0015's consequence sentence kept and attributed. Ledger
header regenerated from the table state and documents the `verdict:` / `e7-manifest-sha256:`
conventions. No `docs/drafts/` 4-pager exists to mark; handoff briefs are immutable, so no markers
were placed there.

**built, not run — the 0024 append script** `docs/drafts/append_0024.py` (ordering-guarded: refuses
until 0023 is in the ledger and the E7 gate passes; every figure from `results/e7/recon.json` and the
verified report; `--preview` prints the text; `--number` renumbers). Its verdict paragraph **does not
change H-E7a's cell**: the registered reading is what 0014/0015/0018 decided under; choosing a
reading is a registration act for a successor to 0006/0014.

**STOPPED — #5 E8 rescoring.** The pinned upstream `score_mapper.py` derives the training mask as the
complement of the held-out set and refuses an empty one, so `--holdout-frac 1.0` is rejected; and it
writes only layer means + per-layer R², never per-sequence moments (Track A's uncommitted `--per-token`
path writes per-token squares with no sequence index). Both are upstream changes → a coordinated
re-pin after Track A's lands, per the seed. Nothing in `config/e8.toml`, `e8.py` or `summarize_e8.py`
was changed; entries 0025/0026 as drafted in the seed cannot be registered as written.

**not done — appends.** No ledger entry was appended (0023 is not on `main`). Suite 331, gates green.
re-verify: `.venv/Scripts/python.exe -m pytest -q` → 331 passed
re-verify: `.venv/Scripts/python.exe -m linear_ceiling.seal verify && .venv/Scripts/python.exe -m linear_ceiling.lint_scope && .venv/Scripts/python.exe -m linear_ceiling.ledger_check`

## Locked decisions

- **Manifest hash = canonical JSON; config hash = newline-normalized text** — both CRLF-safe; recorded
  values unchanged for LF files.
- **Selection rule is recovered from the two sets, never assumed**; `rule: null` = hand-selected.
- **Trailing-entry immutability is a base-revision block diff, not a hash** — a hash cannot cover the
  entry that carries it. Unreadable base fails closed.
- **Verdict provenance = frozen map + `verdict:` lines**; no regex over four phrasings.
- **The nulls share `switch_slices` with the observed measure** — one slicing, no drift.
- **The request-level reading is REPORTED, not decided** — 0024 changes no cell.
- **Git history is the operator's** — the rigor git-guard refused `git commit`; the override was not
  taken. Per-item patches instead (below).

## Reuse map

- `e7_manifest.list_s3` / `selection` — paginated anonymous listing + rule recovery, reusable for any
  new S3 corpus.
- `ledger_check.check_against(now, base)` + `ledger_at(rev)` — the block diff, pure functions.
- `e7_null.derangement`, `e7_cache.request_prompts` — seeded derangement; request grouping by
  `Msg.request` with the response = the request's last assistant message.
- `docs/drafts/append_0024.py` — the ordering-guarded append pattern with `--preview` and `--number`.

## Invariants (new)

- Disk, report and manifest agree in both directions and in bytes, or E7 reads/summarizes nothing.
- An entry block committed at the base revision is byte-identical afterwards (CI).
- A non-`unresolved` cell has a named setter; from 0024 the setter is a `verdict:` line.
- Every E7 figure from 0024 names its manifest sha.

## Open / next

1. **Apply and commit the per-item patches** (operator; commands in the session report), then run the
   GATED driver once: `python -m linear_ceiling.e7` → its report must equal the recon-only one
   byte-for-byte (`config d16cf4659aab`, `manifest 371fb4bf3cb0`), then `summarize_e7` with both flags.
2. **0023 lands (Track A) → `docs/drafts/append_0024.py`** (renumber with `--number` if 0024 was taken:
   Track A's notes call its H-E9 verdict entry 0024 — collision to resolve first).
3. **Ruling needed — the request-level reading of "input-token spend"** puts H-E7a's upper-bound ratio
   at 10.0012%. 0024 records it without changing the cell; a successor to 0006/0014 must fix the
   reading before any restatement. (The exact-tokenizer sensitivity of 0022 was computed under the
   registered reading only; the request-level one is unmeasured — a 4.5% denominator move would cross.)
4. **#5 needs an upstream change** (allow `holdout_frac = 1.0` with no training mask, and per-sequence
   SSE/SST) — coordinate with Track A's re-pin; then 0025 (amended text) → rerun → 0026.
5. **Small:** `upstream_gate.check_upstream` crashes with `NotADirectoryError` from a worktree because
   `../kv-transfer-replication` resolves relative to the worktree root — should refuse with a message.
   E8/E9 config shas still use the raw-bytes digest.

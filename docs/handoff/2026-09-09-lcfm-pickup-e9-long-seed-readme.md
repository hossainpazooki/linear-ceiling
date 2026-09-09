# Handoff — LCFM pick-up: gap map and paper assessed, E9-long seeded, README reworked, the 0034 chain checked before commit

2026-09-09 (session `linear-ceiling-lcfm`, `018R4BNzaMfGpTZaCSocf8Sc`; home session, no box). Newest commit this
brief describes: linear-ceiling `4eafe40` = origin/main, tree clean except untracked `.claude/`. Upstream
`kv-transfer-replication` at `4633718` = origin, one untracked unignored dir `results/mapper/qwen3-0.6b-to-1.7b/n420/`
off every invoked path. Ran in parallel with the box session (`878feb6f`, brief
`2026-09-09-n420-dump-fit-0033-0034-landed.md`); this brief covers only what this session did and verified.

## Current state

- **verified** — pick-up of the 2026-09-07 brief: every re-verify line reproduced; the two blocks (n = 420 target
  dump absent; `summarize_e9` refusing at upstream HEAD) reproduced exactly. Block (a) was then cleared by the box
  session (0033/0034 on the record). **Block (b) is still open.**
  re-verify: `.venv/Scripts/python.exe -m linear_ceiling.summarize_e9` → `E9 SUMMARY REFUSED: upstream paths ... changed between the pin d5786df91f55 and HEAD`.
- **verified** — the 0034 chain, checked before the operator's commit: every figure in entry 0034 recomputes from
  `results/e8c/summary.md` and `results/e9c/summary.json` to the digit (E8 three k rows, per-sequence median, E9 f*
  at three τ, bootstrap, ladder, bridge R² K and V); the mapper sha `b602eaf2e844` is in both reports; the n = 420
  target dump 30/30 and the fit outputs 9/9 re-hashed from raw bytes; token/IP sweep over all changed files clean.
  re-verify: `cd ~/dev/kv-transfer-replication/data/kv/qwen3-0.6b-to-1.7b-n420/target && sha256sum -c --quiet ../n420_target.sha256 && echo 30/30`; `grep -c "| \[+0.1357, +0.1562\] | UNRESOLVED / UNRESOLVED |" ledger/ledger.md` → 1.
- **verified** — gates at `4eafe40`: `pytest -q` 401 passed / 1 skipped; `ledger_check` → `ledger ok`; `lint_scope`
  → `scope ok`; `seal verify` OK; `git diff --check` clean. `e8 --check --config config/e8c.toml` and `e9_rescore check
  --config config/e9c.toml` were run only on the uncommitted tree (refused, as designed) and **not re-run after the
  commit** — the next session runs them first.
  re-verify: `.venv/Scripts/python.exe -m pytest -q | tail -1`; `.venv/Scripts/python.exe -m linear_ceiling.e8 --check --config config/e8c.toml` → expected `ready`.
- **built** — `docs/2026-09-08-seed-e9-long-half.md`: the long-half E9 experiment (cap 81,920, +35 of 39 excluded
  handoffs), five operator decisions D1–D5, controls incl. a configuration-bridge control, R1 checklist, a
  request-ready abstract for the 3g.40gb slice. Updated after the sitting: 0033/0034 ordering satisfied, both
  mappers in the cross arm, R7 step 0, verifier, the measured 1g.20gb ladder (box session's row).
  re-verify: `grep -c "Updated 2026-09-09\|Why a 3g.40gb slice" docs/2026-09-08-seed-e9-long-half.md` → 2; `grep -c "3g.40gb" docs/2026-09-08-seed-e9-long-half.md` ≥ 8.
- **built** — README reworked in six commits (`bfe3375`..`b4b56aa`): Contents; *Where the program stands*; *What HELD
  means here*; after the Status table, *How the cells hold each other up* (E7 corpus, E8 contrast) and the
  descriptive-entry table 0030–0034 with the 0034 V band-word movement; *Backups (Hugging Face)* with both datasets,
  layouts, restore and verify; docs map gains the n420 runbook, the verifier and the seed.
  re-verify: `grep "^## " README.md` → 8 headings in the order Aims, Contents, Where the program stands, What HELD means here, Status, Setup, Backups (Hugging Face), Docs map.
- **built** — eight learnings entries dated 2026-09-09 (cap-ladder knee; YaRN is an upstream code change; E9 driver
  hard-codes required entries; formula-only GPU budget misses the activation term; compaction gap is occurrence not
  recording on tau2; a descriptive entry moved a band word; the freeze date is a label; a parallel session's report
  is stale on arrival), each with a re-captured basis at `4eafe40`; index rows appended.
  re-verify: `node ~/dev/rigor/scripts/check-learnings.mjs docs/learnings 2>&1 | grep -c "2026-09-09"` → 0 failures on today's entries (7 pre-existing reds remain).
- **assessed, not built** — the LCFM 4-pager. Operator direction 2026-09-09: *for the paper only E9 is relevant*;
  this session's reading is a re-cut, not a drop (E7 supplies the handoffs, E8 explains the cross arm; README
  section *How the cells hold each other up*). No outline edit was made. Items identified and NOT done: abstract's
  compaction sentence overclaims (learnings entry); E8 sentence needs "at this calibration" with 0034 beside it;
  §5.1 freeze row still says BLOCKED though 0034's figures came through both summarizers; the length-is-a-selection-
  variable sentence; the hidden prefix moved into the preface; §4 as the deliverable; the lit sweep (still unrecorded:
  `grep -c -i "lit sweep\|lit-sweep\|literature sweep" ledger/ledger.md` → 1).
- **planned / unregistered** — E9-long (the seed; needs D1–D5 rulings, an upstream YaRN commit, a 3g.40gb grant);
  the recorded-corpus experiment (gap-map open item, MLSys cycle); the gap-map revisited doc has no "status at 0034"
  addendum (its table is still correct).

## Locked decisions — premises checked

- **Paper re-cut around E9** (operator, 2026-09-09). Reason: E9 is the only positive cell and the only mechanism
  result; E7 becomes the corpus section, E8 the contrast. Premise holds only if §3.5 can be frozen → ruling (b).
- **Descriptive entries never move a cell** (ledger rule; 0030–0034 all say so). Reason: a cell is decided once under
  its registered protocol. Premise held at the pre-commit check: no `verdict:` line after 0029.
- **The freeze is the provenance rule of 0006, not the date.** Reason: 0006's text names only "recompute clean via a
  fail-closed summarizer". A figure freezing on 09-09/10 satisfies it. Learnings entry of that name.
- **E9-long needs a 3g.40gb slice or a full card** (measured: 1.7B OOM at T = 40,960 on 1g.20gb). Not relitigated;
  the seed's abstract carries the justification; the T = 80,111 probe replaces the extrapolated 29 GiB before any request.
- **YaRN is an upstream code change + re-pin, not a config edit** (`kvt/rope.py` is plain-θ). Its commit may now be
  the next upstream change (0034 landed); afterwards the 0033-chain gates need a detached checkout at `223f469`.
- **Ruling (a) = re-dump** was taken (box session); **ruling (b)** — detached checkout at `d5786df` for one
  `summarize_e9` run, or a re-pin entry — is still the operator's.
- **The n420 login handle in the 09-09 learnings entry stays** unless the operator redacts; a sibling handle is already
  in a committed 09-04 probe.

## Reuse map

- `docs/2026-09-08-seed-e9-long-half.md` — §1 is a verified fact table with sources; §2 the rulings; the blockquote is
  the grant-request text.
- README sections *What HELD means here* and *How the cells hold each other up* — the paper's E9-centric framing,
  already written with entry citations; lift into the outline rather than re-deriving.
- `docs/probes/2026-09-08-e9-long-memory-ladder-1g20gb.{py,out}` — the R2 ladder; rerun at T = 80,111 on the granted profile.
- `tools/hf_verify_backup.py` — R8 two-direction check; `tools/jupyterhub/` — the box driver and pull loop.
- `results/e9/align/*.json` (local) — the 68 alignment records; the cap ladder recomputes from them in one line
  (learnings entry re-verify).
- The pre-commit check recipe (this session): gate set → figures vs summaries → sha manifests → doc diffs → token/IP
  sweep over `git status --short` paths → commit block grouped by concern, never `git add -A` (`.claude/` untracked).

## Invariants (unchanged, plus two from today)

`results/`, `data/`, `traces/` never enter history; `results/e9/`, `results/e8c/`, `results/e9c/` never rewritten;
entries 0025–0034 immutable; no number enters the ledger, a brief, the README or a paper that a summarizer did not
produce; upstream read-only from linear-ceiling; git history is the operator's; double-blind rules. **Today:** never
launch a summarizer or a model load from this session while a sibling session's summarizer is paging the 24 GB pair
(shell reads only); and the ledger's CRLF warning from `git diff --check` is benign only because `ledger_check`
prints `ledger ok` on the same tree — re-run it after every ledger-touching commit.

## Open / next

1. **Operator: ruling (b).** If detached checkout:
   `cd ~/dev/kv-transfer-replication && git checkout d5786df && cd ~/dev/linear-ceiling && .venv/Scripts/python.exe -m linear_ceiling.summarize_e9 && cd ~/dev/kv-transfer-replication && git checkout main`.
   Then the outline's §3.5 row → FROZEN with the run date. Minutes; the only thing standing between the re-cut paper
   and a frozen result. Deadline 2026-09-10 23:59 AoE.
2. **Outline re-cut around E9** (this session can do it on files no other session touches): §3.5 as the result,
   E7 as corpus (§2), E8 as contrast with "at this calibration" and 0034 beside it, §5.1 row → FROZEN, abstract's
   compaction sentence scoped, length-as-selection sentence, E9-long as the first-named limitation.
3. Post-commit gates not yet run at `4eafe40`: `e8 --check --config config/e8c.toml`, `e9_rescore check --config config/e9c.toml`.
4. The lit sweep (three attributions) or drop the column; `check-learnings` red on 7 pre-existing entries.
5. E9-long: rulings D1–D5; the upstream YaRN commit; the T = 80,111 probe; the 3g.40gb request.
6. Operator: tell the co-author about the 00:40Z incident (box session's brief, item 1).

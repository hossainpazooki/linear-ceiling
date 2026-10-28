# Anonymity denylist — tracked files on main carrying an identifying term (generated 2026-10-13 at daeef57)

Supersedes `docs/2026-10-01-anonymity-denylist.md` (generated at e3a9dfb, before the camera-ready, the eight-author
CITATION.cff, the README rewrite, the OpenReview link, and the removal of `docs/handoff/` and `docs/learnings/` from the tree).
**Status 2026-10-27 (entry 0066):** the conference submission this list was refreshed for was not made; the workshop
camera-ready is non-anonymous and needs no mirror. The list is kept for the next double-blind venue, and the venue
term `mlsys` is in the pattern below so that a mirror is venue-free as well as author-free.

Why it was needed again: MLSys review is double-blind (the 2026 call, the format proxy for 2027: "authors must avoid
identifying themselves either explicitly or implicitly"; non-compliant submissions "will be rejected without review"),
so a code link in the MLSys submission must point at a re-cut of `origin/lcfm_anon` made from the submission commit with
this list applied. If the submission carries no code link, this list and the mirror are unnecessary.

Rule (learning 2026-09-21): `origin/lcfm_anon` is the double-blind copy; it censors these terms across the tree and drops
infrastructure-only records. Before any re-mirror, every file below is either censored or dropped; a new term is added
here before it is added to the tree. The pattern is case-insensitive; `yan` is word-bounded.

Pattern: `hossainpazooki|pazooki|hossain|ishmam|farhan|ritvikagg|ritvik|aggarwal|emersony99|emerson|nadathur|vikram|muhzain05|zain|asad|alake|lingyuan|yan|samuel|muhammad|algoverse|emmmy|neuriv|de anza|university of (alberta|toronto|utah)|kegvswnfaq|mlsys`

Added since 2026-10-01: `hossain` (surname alone, README and pyproject), `zain` and `asad` separately (CITATION splits the
name), `yan`, `samuel`, `muhammad` (the three author names the old pattern missed), the four GitHub handles that appear in
review records and issue references (`neuriv`, `muhzain05`, `ritvikagg`, `emersony99`), the three affiliations, and the
OpenReview forum id `kEGVswNFaq` (the badge, `pyproject.toml`, `CITATION.cff` and the README citation resolve to the named
workshop paper).

## Judgment items the pattern cannot decide

- **Dataset ids** `hossainpazooki/linear-ceiling-*` and `emmmy/linear-ceiling-*` (README, `docs/paper-to-record.md`, runbooks,
  reviews, T04): the mirror censors the namespace (`<anon>/linear-ceiling-*`) and the submission says the datasets are
  public and named on acceptance. The README's runnable Hub record check must be dropped or rewritten on the mirror.
- **`kv-transfer-replication`** is the operator's public upstream repository (`UPSTREAM.md`, six configs, the gates). Its
  name is not in the pattern because censoring the path breaks every gate; the mirror keeps the path and censors the
  GitHub owner in `UPSTREAM.md`'s links only, as the 2026-09-14 cut did.
- **The repository name** `linear-ceiling` is not identifying on its own and stays.
- **`LICENSE`** is the canonical Apache-2.0 text with no copyright line and stays. `pyproject.toml` drops its `authors`
  and `[project.urls]` tables on the mirror.
- **`docs/reviews/2026-09-20-astra_review.md`** names a reviewer tool and the branch; censor by pattern like any other file.
- **`tools/cache_injection_pilots/docs/refutations.html`** is a co-author's review record; censor by pattern, never edit otherwise.
- **The ledger** carries 11 pattern hits (dataset ids, PR links, one surname at 0005's design citation). The mirror re-derives
  the chain after censoring, as before; a censored ledger proves internal consistency only and is never a source for a figure.

## Files hit, with the action on the mirror

| file | hits | action |
|---|---|---|
| `docs/probes/2026-09-04-hf-upload-large-folder-4workers.err` | 50 | DROP: upload log naming the account (infrastructure record) |
| `README.md` | 40 | censor |
| `docs/2026-10-01-anonymity-denylist.md` | 36 | DROP: the previous list; this file supersedes it and is itself dropped on the mirror |
| `CITATION.cff` | 27 | DROP: author list and affiliations; the mirror carries no citation file |
| `ledger/ledger.md` | 14 | censor |
| `docs/reviews/2026-09-28-llama-cell-r8-backup-and-recomputation.md` | 11 | censor |
| `tools/cache_injection_pilots/docs/refutations.html` | 11 | censor |
| `docs/paper-to-record.md` | 8 | censor |
| `docs/reviews/2026-10-01-cache-refutation-0025-0029.md` | 8 | censor |
| `docs/runbooks/2026-10-07-llama-long-cell-runpod-runbook.md` | 7 | censor |
| `pyproject.toml` | 6 | censor |
| `docs/runbooks/2026-09-02-e9-gpu-runbook.md` | 5 | censor |
| `docs/gpu-experiment-protocol.md` | 5 | censor |
| `docs/reviews/2026-09-14-e9-cold-rescore-second-machine.md` | 5 | censor |
| `UPSTREAM.md` | 4 | censor |
| `docs/runbooks/2026-09-08-n420-target-dump-runbook.md` | 4 | censor |
| `docs/runbooks/2026-09-10-e9l-gpu-runbook.md` | 4 | censor |
| `docs/runbooks/2026-10-04-e-trunc-gpu-runbook.md` | 4 | censor |
| `docs/runbooks/2026-10-06-cache-behavior-runpod-runbook.md` | 4 | censor |
| `docs/drafts/README.md` | 4 | censor |
| `docs/design/2026-09-02-e-rl-design.md` | 3 | censor |
| `docs/design/2026-09-13-seed-e9-scaled-short-cell.md` | 3 | censor |
| `docs/runbooks/2026-09-30-consolidation-runbook.md` | 3 | censor |
| `docs/reviews/2026-09-30-review-response-map.md` | 3 | censor |
| `docs/reviews/2026-09-11-clean-clone-reproduction.md` | 3 | censor |
| `tools/cache_injection_pilots/docs/replicate.html` | 3 | censor |
| `tools/cache_injection_pilots/experiment-manifest.json` | 3 | censor |
| `tools/cache_injection_pilots/fetch_records.py` | 3 | censor |
| `tools/ec2/setup.sh` | 3 | censor |
| `config/e8f.toml` | 2 | censor |
| `config/e9f.toml` | 2 | censor |
| `config/e9fl.toml` | 2 | censor |
| `docs/design/2026-09-08-seed-e9-long-half.md` | 2 | censor |
| `docs/runbooks/2026-09-13-e9s-gpu-runbook.md` | 2 | censor |
| `docs/design/2026-09-18-llama-upstream-patch-spec.md` | 2 | censor |
| `docs/runbooks/2026-09-19-sitting-b-procedure.md` | 2 | censor |
| `docs/runbooks/2026-10-07-consolidation-runpod-runbook.md` | 2 | censor |
| `docs/reviews/2026-10-01-feedback-and-claims.md` | 2 | censor |
| `tools/cache_injection_pilots/README.md` | 2 | censor |
| `tools/cache_injection_pilots/results/README.md` | 2 | censor |
| `docs/design/2026-09-01-lcfm-gpu-plan.md` | 1 | censor |
| `docs/runbooks/2026-09-18-llama-gpu-runbook.md` | 1 | censor |
| `docs/reviews/2026-09-20-astra_review.md` | 1 | censor |
| `docs/runbooks/2026-10-01-cache-behavior-runbook.md` | 1 | censor |
| `docs/README.md` | 1 | censor |
| `docs/agent/experiment-commands.md` | 1 | censor |
| `docs/drafts/e-trunc-design.md` | 1 | censor |
| `docs/drafts/tables/T04-r12-0051-recompute.md` | 1 | censor |
| `docs/provenance/2026-09-30-a100/source.json` | 1 | censor |
| `docs/provenance/2026-10-01-cache-behavior-inputs/README.md` | 1 | censor |
| `docs/reviews/2026-09-08-e9-independent-reverification.md` | 1 | censor |
| `src/linear_ceiling/__init__.py` | 1 | censor |
| `tools/cache_injection_pilots/migration-manifest.json` | 1 | censor |
| `tools/jupyterhub/README.md` | 1 | censor |
| `tools/seam_pilot/fetch_inputs.py` | 1 | censor |
| `tools/seam_pilot/source.json` | 1 | censor |

56 tracked files hit; 322 hits (each occurrence of a term counted once; the handle `hossainpazooki` counts as one).

## Which terms hit (files)

`hossainpazooki` 179 in 43 files · `algoverse` 21 in 13 files · `emmmy` 13 in 5 files · `neuriv` 11 in 10 files · `pazooki` 10 in 5 files · `hossain` 10 in 6 files · `ritvik` 9 in 6 files · `farhan` 7 in 5 files · `aggarwal` 6 in 4 files · `kegvswnfaq` 6 in 4 files · `emersony99` 6 in 6 files · `emerson` 5 in 3 files · `nadathur` 4 in 3 files · `vikram` 4 in 3 files · `lingyuan` 4 in 3 files · `alake` 4 in 3 files · `asad` 4 in 3 files · `zain` 4 in 3 files · `university of ...` 4 in 1 files · `ishmam` 4 in 3 files · `yan` 2 in 2 files · `samuel` 2 in 2 files · `muhammad` 2 in 2 files · `de anza` 1 in 1 files

## Re-cut procedure (operator, from the submission commit)

1. Tag the submission commit on main. 2. Branch `lcfm_anon` anew from it (the old branch stays as the LCFM record; never
merge either way). 3. Drop the DROP files (the `docs/handoff/HANDOFF.md` stub stays). 4. Censor every
remaining hit by the pattern (`[anon]` for names and handles, `<anon>` for the account in dataset ids and links, remove the
OpenReview badge and the citation section). 5. Re-run `grep -rilE '<pattern>'` on the branch tree: zero files. 6. Re-derive
the ledger chain and run `ledger_check`, `lint_scope`, the suite. 7. Push the branch only; the submission links the branch
at its commit, never `main`. 8. Add any new term here before it enters the tree.

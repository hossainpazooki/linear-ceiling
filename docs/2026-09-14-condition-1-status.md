# Condition 1: source check and stop report

Date: 2026-09-14. Reviewed HEAD: `a5053b2f1d453235c87ce07e9f30f95524a2a590`.
Status: supporting status note, not a ledger entry, refutation, signature, admission ruling, or new scientific result.

## Stop condition

The operator's seed requires: "Fill every 'verify' row with a quote and line number. If any row fails, stop and report."

Row 6 cannot be verified from the supplied source. The operator supplied the Claude **Papers** project context and the source of `lcfm-extended-sprint-board-v3.jsx`. The project context separately lists `lcfm-submission-day-board.jsx`, but the source of that artifact has not been supplied or located locally. The supplied extended board does not contain "dropped as a gate". It must not be substituted for the submission-day board while claiming to have checked the latter.

The Path A signature identities also remain unconfirmed. The seed proposes the co-author and operator; the supplied extended board instead assigns the review record to **Samuel and Emerson**, and says the pairings are proposed. That is a proposed assignment, not an operator confirmation of whose two signatures this template requires.

No Path A template, signature lines, Path A entry script, Path B append script, or entry-number allocation was prepared after this source check failed. No path was selected. The ledger, existing review record, upstream checkout, paper source, and results were not edited. No scientific summarizer, driver, or probe was run.

## D1: source checks

All repository line references below are to the reviewed HEAD. The supplied board is an external conversation artifact, not a file at that HEAD.

### Row 1: condition and consequence — verified

`ledger/ledger.md:1947-1951`, entry 0032:

> **Condition carried forward, not a ledger fact.** The co-author refutation of entries 0025–0029 (two leads:
> the τ-ladder sensitivity; the exactly-zero prefix-invariance control) is owed at the time of writing. If it has
> not been recorded by the numbers-freeze gate, the 4-pager's E9 section is cut to one sentence marked as
> ongoing work and the figures are withheld from the submission; this entry does not decide that outcome and a
> later entry records it either way.

The applicable freeze is also stated: `ledger/ledger.md:1927-1928` says "numbers-freeze gate EOD 2026-09-08 per entry 0006". A later workshop deadline does not itself amend this date.

### Row 2: latest handoff — verified

`docs/handoff/2026-09-14-e9s-sitting-run-read-and-entered-backup-staged.md:51`:

> Paper condition 1 (co-author refutation of 0025–0029), unchanged.

### Row 3: outline and the actual probe-independence brief — verified

`docs/paper/2026-09-11-lcfm-outline-v3.md:25-28`:

> **E9 (0029) stays in only if the co-author refutation of 0025–0029 is recorded.** Status: **NOT discharged.** The
> co-author's PR (merged 2026-09-10) records a computational re-verification of two sampled handoffs; the 09-10
> brief on it states this does not by itself discharge condition 1, and whether it counts is the operator's ruling.
> Until ruled, §5.1 is written and marked cond. 1 as in v2.

The referenced brief was read directly. `docs/handoff/2026-09-10-keeping-the-e9-independent-rescore-probe-independent.md:112-115`:

> **Paper condition 1 is not discharged by this merge.** The record supports computational integrity for two sampled
> handoffs, and says itself that it does not resolve the threshold choices, the sign-off chronology, the oracle floor
> versus an achieved method, or generalization. Whether it counts toward the owed refutation of 0025–0029 is the
> operator's ruling.

### Row 4: handoff index — verified

`docs/handoff/HANDOFF.md:10`, the probe-independence row, ends:

> condition 1 not discharged by this merge.

The index is a pointer; the actual statement is verified in the underlying brief above.

### Row 5: what the independent re-verification records — checked; no signed author named

Read `docs/reviews/2026-09-08-e9-independent-reverification.md` in full, lines 1-66. Its date is 2026-09-08 (line 3). It has no named author or signature line. Introducing commit `d009f36` was identified with `git log --follow`; commit authorship is not a signed attestation in the review document. The extended board's later assignment to Samuel and Emerson does not establish that they both authored or signed this earlier review.

The two sampled handoff IDs are quoted at lines 33-34:

- `20241025_composio_swekit__django__django-11066_traj_sw36`
- `20241016_composio_swekit__astropy__astropy-14182_traj_sw68`

These identifiers are internal provenance, not paper text. The sample is two retained handoffs (review lines 30-34), from the 25 included handoffs in entry 0029 (`ledger/ledger.md:1779`).

What was recomputed, review lines 36-40:

> For each handoff, the frozen upstream `scripts/score_positions.py` was run from
> the archived raw dumps, mapper, and alignment. The archived and regenerated
> headline fields matched exactly, as did the keys and contents of every retained
> per-token array. The review used exact equality rather than the registered
> cross-platform tolerance.

What this establishes, review lines 61-66:

> This re-verification supports computational integrity for the sampled archived
> records. It does not resolve the registered threshold choices, the chronology
> of later sign-off, the oracle-floor-versus-achieved-method distinction, or
> generalization beyond the recorded harness, model pair, and corpus. Those are
> scientific judgment and governance questions, not failures of the comparison
> tool.

Neither a threshold-ladder attack nor an attack on the exactly-zero prefix-invariance control is documented. The opening says interpretation was assessed separately (lines 8-10), but the note supplies no attack procedure or outcome for either of 0032's leads. This is a finding about what the document records, not a claim that no other review work occurred.

For any eventual Path B entry, preserve this boundary. Calling this check a refutation would be the operator's admission ruling, not a new description of what the check measured.

### Row 6: submission-day board — could not verify; stop

Location established only at the project/artifact level: Claude project **Papers**, artifact `lcfm-submission-day-board.jsx`, listed separately in the operator's supplied project context. No local file, URL, or source lines for that artifact have been supplied. Searches of repository documentation and local board/artifact filenames did not locate it. The repository's path history search did not identify a committed copy.

The supplied source is instead `lcfm-extended-sprint-board-v3.jsx`. Relevant exact excerpts, located by object or section in that supplied source rather than invented repository line numbers:

- `PAIRS`, `id: "se"`: `pair: "Samuel · Emerson"`.
- The same object's `closes` field: "A dated record under docs/reviews with both names; §6's owed-at-time-of-writing sentence resolved either way."
- `RULES`: "Nothing run after 0036 enters the paper. The verification pair's findings go to docs/reviews, then to an entry after the upload."
- The section **What may appear in print** says: "Unchanged from the submission-day board, whose frozen table is still the source: §4.1 from 0029, §4.2 from 0036".
- Footer: "pairs are proposed, not settled" and "the ledger is the authority where this page and the repo disagree".

The extended board schedules use of 0029 while deferring a verification entry until after upload. It does not itself release 0029 under 0032, nor does it prove the claimed wording of the separate submission-day board. The latter source is required to finish row 6.

### Row 7: a brief cannot loosen the ledger — verified, with a date correction

`docs/handoff/2026-09-10-e9l-independent-verification-outline-filled-and-the-r8-retry-corrected.md:63-64`:

> **0035 supersedes 0032's space clause and nothing else.** Reason: the operator's re-cut ruling lived only in
> briefs, and a brief cannot override an immutable entry. Premise holds; the co-author condition is untouched.

The explicit sentence assigning a loosening to the operator is in the **09-09** handoff, not the 09-10 statement above. `docs/handoff/2026-09-09-e9-long-build-and-paper-recut.md:49-50`:

> **0035 carries the paper re-scope and supersedes 0032's space clause; every other 0032 clause kept, including the
> co-author condition unchanged.** Loosening that condition is the operator's call by a later entry, not mine.

Together these sources establish the seed's substantive claim, with its source date corrected.

### Row 8: scaled short provenance — verified

`ledger/ledger.md:2244-2246`, entry 0037:

> which reproduces 0029's coverage and keep draw exactly (checked by this script
> against `results/e9/report.json`: the same 25 included ids with the same `n_sender`/`n_receiver`/`n_matched` and
> text hashes, the same 43 excluded, the same eight kept).

Entry 0038, `ledger/ledger.md:2316-2317`, confirms:

> Complete: 25 scored of 25 registered, in 0037's order; of 68 observed handoffs 25
> included and 43 excluded, 0029's sets exactly.

### Row 9: calibration-size E9 provenance — verified

`ledger/ledger.md:2024`, entry 0034, names "0029's kept dumps and alignments by fingerprint."

`ledger/ledger.md:2038-2039`:

> **E9 cross arm on the 8 kept handoffs.** Same-arm control PASSED on every handoff (max relative square vs 0028's
> re-score: same_K 0.00e+00, same_V 0.00e+00; the tensors and alignments are 0029's).

This verifies the dependency. It does not substitute for the operator's confirmation of whether a release covers 0034's E9 part.

## D1: does the condition extend to 0036?

**0035 does not extend 0032's withholding consequence to E9-long.** This conclusion is a reading of the explicit distinction in the entry, not a new waiver.

Entry 0035, `ledger/ledger.md:2156-2161`:

> from 0032, unchanged: E9 and E9-long figures enter the 4-pager only from a passing `summarize_e9` run (E9's at the
> detached `d5786df` checkout, 2026-09-09; E9-long's under `config/e9l.toml`); the same-model result never appears
> without the cross-model outcome in the same table or sentence; coverage travels with every number, and E9-long's
> reads "n of 35 newly included, the long half, never pooled with 0029's 25"; the co-author refutation of 0025–0029 is
> still owed and 0032's consequence for E9's figures stands as written — a later entry records it either way. E9-long's
> figures enter by their own numbered entry.

The consequence names E9's figures while the same passage names E9-long separately and admits its figures through its own entry. The outline independently preserves this distinction: `docs/paper/2026-09-11-lcfm-outline-v3.md:29` says "E9-long (0036) enters only from a passing `summarize_e9 --config config/e9l.toml`" and marks that condition satisfied.

The long cell uses the same statistic, ladder, and control ideas, so the scientific criticisms remain relevant. Shared instrument dependencies do not by themselves add a publication gate absent from the admission text.

## Scope to preserve when work resumes

| Record | Current drafting treatment | Authority or outstanding decision |
|---|---|---|
| 0029 | Withhold figures; one sentence marked ongoing work | Explicit consequence in 0032, retained by 0035 |
| 0038 | Withhold under the operator's current task instruction; no workaround through the same short handoffs | Dependency verified in 0037/0038; eventual admission ruling must state its release scope |
| 0034, E9 part | Do not include in an admitted variant without the operator's explicit release scope | Dependency verified; the seed labels withholding proposed and asks the operator to confirm |
| 0036 | Remains separately admissible under 0035's stated conditions | Own numbered entry and passing summarizer; no automatic extension of condition 1 |
| 0020, 0031, 0034 E8 part | Outside this condition's short-handoff dependency | No release decision for these is made here |

A new Path A review would be recorded after the original numbers-freeze date. Its subsequent admission entry must address that chronology explicitly; a newly dated review cannot itself establish compliance by the earlier freeze. Path B likewise must say what the operator accepts and which admission terms they supersede, while preserving the older entries and the review's stated boundaries.

## D5: board correction text for the operator — not posted

Condition 1 remains open under ledger 0032, carried by 0035: this board does not release 0029's figures; the operator must record the admission outcome in a later numbered entry (see `docs/2026-09-14-condition-1-status.md`).

## Remaining work and inputs

1. Supply the source or an accessible URL for `lcfm-submission-day-board.jsx` so row 6 can be checked with actual source lines, or explicitly amend the seed's stop requirement for that unavailable source.
2. Confirm whose two signatures Path A requires. The supplied board proposes Samuel and Emerson; the seed's co-author-plus-operator assumption is not confirmed.
3. After the source gate is resolved, confirm the release scope of a prospective operator ruling, especially 0034's E9 part. Neither path has been chosen here.
4. Then prepare D2, D3 and D4. Do not allocate an entry number until the Path B script is actually staged in `docs/drafts/README.md`; do not generate a Path A append script before the completed review document exists.

No append script exists for this task, so there is no preview command to run and no script to execute. The final commit block must name only files that actually exist at handoff; the seed's full proposed block is not ready to run.

## Validation

Pending the final read-only checks for this stop report. No scientific outputs were regenerated.

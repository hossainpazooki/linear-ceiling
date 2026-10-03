# Admitting a co-author's GPU run to the ledger: upload by the runner, refutation by the operator

**Date:** 2026-10-03 · **Status:** PROPOSED procedure, not yet a protocol rule. It composes rules that already exist
(`docs/gpu-experiment-protocol.md` R1, R3, R8, R11, R12; the drafts README's allocator; the Path A review format) into
one path for a run that someone other than the operator executed. Once ruled, it becomes R13 of the protocol and this
doc is its rationale. Worked case: the September 30 same-model extension (Qwen3-4B, SmolLM3-3B, Qwen3-1.7B bridge) in
PRs #8 and #9.

## 0. Why a separate path

Every entry on this ledger so far was run by the operator or on a box the operator released. A co-author's run breaks
two assumptions the protocol makes silently: the person who appends the entry did not see the forwards, and the raw
records live on a machine the repository cannot read. R12 already says what that costs: "a co-author's refutation of
the run's entries is recomputation from the git repo plus the backup, and if that is not possible from a clean
checkout, something is missing from R3 or R8." Here the roles invert. The co-author is the claimant; the operator is
the refuter. Nothing enters the ledger on the claimant's word, including the claim that a GPU ran at all.

Three roles, one direction of trust:

| role | does | may not do |
|---|---|---|
| **runner** (co-author) | freezes inputs, runs, mirrors, pushes the backup, opens the PRs | append an entry, write a figure into a doc, name a ledger number |
| **operator** | registers, downloads the backup to a clean mirror, recomputes, writes the refutation record, appends | trust a figure that did not come out of the fail-closed reader on the operator's machine |
| **second reader** (another co-author) | signs the refutation record by PR approval | — |

## 1. Before the run (R1): registration still comes first

The runner opens a PR with the frozen inputs and nothing else: the config under `config/`, the input manifest
(every input byte hashed), the runbook (box, chunking, controls, bridge bounds, stopping rule, what is retained),
the lock files, the driver and its tests. The operator reads it, allocates the next number in `docs/drafts/README.md`,
and appends the registration entry. **The entry lands before the first forward.** The runner then runs against the
committed config sha and manifest sha, which the driver asserts at start (the consolidation driver already does).

If the run already happened, as in the worked case, R1 is not met upstream and cannot be repaired. The entry then says
so in its first paragraph: where the registration did occur (a fork, a commit sha, its UTC timestamp), what evidence
dates the forwards relative to it, and that this is a post-hoc descriptive import. Precedents for an entry recording a
lapse: 0021 (dating erratum), 0041 (an ordering never registered), 0045 (a sentence corrected). An import may never
carry a `verdict:` line or move a cell.

## 2. What the runner delivers

Everything below is checked by the operator, not read:

1. **The evidence bundle**, laid out as `results/<exp>/` so `hf download --repo-type dataset --local-dir results/<exp>`
   reconstructs it with no translation (R8): per-model `report.json` with `complete: true`, every compact record the
   report names with its sha256, the retained raw witnesses, the inputs the manifest names, logs, and a `SHA256SUMS`
   over the whole bundle.
2. **In each `report.json`**: `config_sha256`, `manifest_sha256`, `code_commit`, `code_sha256` of the driver files
   that ran, `torch` / `transformers` / `numpy` / `cuda` versions, the `gpu` string, `dtype`, and per handoff `seconds`
   and `peak_allocated_GiB`. These are what make the hardware claim checkable at all.
3. **The run code.** If the driver in the PR differs from the code that ran (packaging edits after the run), the
   runbook states the run-time `code_sha256` values and what changed. A refutation compares the PR's files to those
   hashes; a silent divergence is a finding.
4. **The backup push (R8)**, by the runner, from the verified home mirror, never from the box. Public. Records first,
   large files by one resumable `upload-large-folder`, the `complete: true` report last. Name:
   `<account>/linear-ceiling-<exp>-<YYYY-MM-DD>`, under the runner's account if that is where the mirror is (the Llama
   precedent, ruled 2026-10-01). Dataset names stay out of double-blind material. Before the first push: sweep the
   staging tree for credential shapes with a planted positive control; push from a copy, never a hardlinked stage.
5. **A verification line the operator can run**: `tools/hf_verify_backup.py <repo_id> <local_root>` exit 0 both
   directions, with the Hub revision sha it was verified against written into the runbook.
6. **The claimed figures**, in the PR body or the runbook, each with the key of the summary file it comes from. A
   figure with no key is not a claim, it is prose.

## 3. What the operator does (R12, inverted)

On a clean clone of the PR head, on a machine that did not run the experiment:

1. **Pins.** Config sha and manifest sha in each report equal the committed files; the manifest's `config_sha256`
   equals the config; every record and witness hashes to its report entry; `SHA256SUMS` matches the download; the
   Hub revision equals the one the runbook names. Any mismatch stops the admission.
2. **Code.** The PR's driver files hash to the report's `code_sha256`, or the runbook's divergence note explains each
   difference and none of them touches arithmetic or capture.
3. **Chronology.** Registration commit timestamp, first and last forward (from `report.json` per-handoff timing, or
   the logs), backup push time. If the forwards precede the registration, the entry is an import (§1), whatever the
   runner's ledger says.
4. **Recompute.** Run the runner's fail-closed summarizer in-process over the downloaded mirror. It must recompute
   every figure from the records, re-score every witness from raw tensors, and refuse on any disagreement. Compare
   each recomputed figure to the claimed one at printed precision. A reader that does not refuse on a planted
   mismatch is not a reader (test it with one byte changed before trusting its pass).
5. **Instrument.** The arithmetic must be the registered one (`e9_pertoken.centered_delta`, `token_mean`, `f_star`,
   `e7_stats.quantile`); a second quantile or mean convention is a finding. A bridge against the original archive is
   required when the capture path differs from the original driver, with its bounds fixed in the config.
6. **Record.** `docs/reviews/<date>-<exp>-admission-refutation.md` in the Path A format: reviewed revision, the Hub
   revision, per claim an attack / evidence / finding / limits block, what was not checked, signature and date. It
   states explicitly whether the hardware claim is supported by the report fields or only asserted.
7. **Second signature.** A co-author who did not run the experiment approves the review PR.

## 4. The entry

Appended by an `append_<NNNN>.py` that runs the summarizer in-process over the operator's verified mirror, with the
pin checks of §3.1 as assertions. The entry states: who ran it, on what (the `gpu` string from the report), when
(UTC, from the report), the registration status (R1 met, or the import paragraph of §1), the Hub dataset id and the
revision verified, the refutation record's path and its two signatures, the runner's credit, and every figure with its
summary key. Descriptive imports carry no `verdict:` line. The runner's config files move under `config/` in the same
commit as the registration entry, never before.

## 5. The paper

A figure from a co-author's run enters a paper only from that entry (the outline's gate, unchanged). The caption names
the entry and, for an import, the words "registered post hoc; R1 exception recorded in entry NNNN". Tooling that emits
paper tables (`paper_assets.py` in PR #9) takes the entry number as a required argument and refuses without one.

## 6. What refuses the admission

Any one of: no public backup; a report without `complete: true`, `code_sha256` or the runtime fields; a pin mismatch;
a recomputed figure that differs from the claim at printed precision; a reader that passes a planted mismatch; a
chronology the records cannot support; a `verdict:` line on an import; a figure in a doc or PR body with no summary
key. Refusal is a finding in the review record, not a rejection of the work: the runner can repair R8 and R3 defects
and resubmit; R1 cannot be repaired and is recorded instead.

## 7. Worked case: the September 30 extension (PRs #8 and #9), as of 2026-10-03

| step | state | owes |
|---|---|---|
| §1 registration | **not met upstream**; fork entry at `3cb4bb3` (2026-10-01 02:41Z), results commit 05:28Z | import paragraph in the entry (operator) |
| §2.1 bundle | exists on the runner's Desktop only | — |
| §2.2 report fields | present per the driver source; **not seen** | the push |
| §2.3 run code | PR driver differs from the pre-run commit; run-time hashes not stated | runbook note with `code_sha256` (runner) |
| §2.4 R8 push | **not done** | runner |
| §2.5 verify line | — | runner, after the push |
| §2.6 claimed figures with keys | tables in `docs/2026-10-01-a100-analysis.md` and the fork entry; keys in `summary.json` | — |
| §3 recompute + record | not started; blocked on §2.4 | operator |
| §4 entry | number 0048 unallocated; config currently proposed under `config/` in PR #8 | operator, after §3 |
| §5 paper | `paper_assets.py` ungated | runner |

Verified by the operator's session on 2026-10-02 without the bundle: config and manifest byte-identical to the fork's
pre-run commit; the fork-ledger excerpt and whole-file hashes in `docs/provenance/2026-09-30-a100/source.json`
reproduce; the driver's arithmetic imports the registered functions; the PR tests pass on an extracted tree.

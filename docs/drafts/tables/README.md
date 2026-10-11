# Paper tables and paragraphs (drafts)

One file per table, or per figure-bearing paragraph, that the paper will print, written BEFORE it is pasted. The file
is the paste source and the skeptic's target; the ledger stays the provenance. A file with no table or paragraph body
is a RULE: what every file of its kind must carry. The draft plan under `docs/paper/` is the index of what the paper
needs; these files are its paste source.

Format (approved by the operator 2026-10-10):

- Filename `T<nn>-<slug>.md`, numbered in staging order; `T` keeps these apart from ledger entries, which they cite and
  never restate.
- Header fields, one per line: `status:` (`RULE` | `DRAFT` | `APPROVED <date>` | `PRINTED <manuscript sha>`), `sources:`
  (BOTH forms for every figure: the ledger entry:line at a named ledger revision, AND the summary-file key with the
  file's sha256 prefix — entry lines rot at the next corrective, keys do not), `conventions:` (the quantile, rounding
  and unit each number is under), `re-verify:` (shell lines that must hold, with the expected output after `#`, as in
  `docs/learnings/`; run before every commit that touches the file).
- Body: the annotated paper format used for the abstract and introduction — the paragraph as a block quote, then
  "Changes, and why" (or "Sources, and why each sentence is there") with entry:line per figure, then the skeptic record,
  then the approval record. A table sits in the same body at the paper's precision (four decimals), every cell with
  its source. Approval is per paragraph.
- Immutability: a file edits freely while `DRAFT`. Once `APPROVED` it never changes; a correction, a filled
  cross-reference or a reviewer-forced rewrite is a NEW file that names the one it supersedes in its header, and the
  index below marks the old one superseded. `PRINTED` is a superseding file too, pinning the manuscript tree.
- No figure here is typed from memory: the skeptic pass reads each cell from its summary file at claim time and the
  approval note records what it read.

| file | status | what |
|------|--------|------|
| [T01](T01-pooled-per-token-quantiles.md) | RULE | printing a pooled per-token p10/p90/p99 under the nearest-rank sentence |
| [T02](T02-e-trunc-paragraph.md) | APPROVED 2026-10-10 | the E-TRUNC paragraph (§4); §X cross-reference open, filled by a superseding file |
| [T03](T03-second-pair-section.md) | DRAFT | §4.x second pair Llama-3.2-3B → Llama-3.1-8B: table, P1–P4, App. A scoping sentences; P2 tail-sentence placement open |

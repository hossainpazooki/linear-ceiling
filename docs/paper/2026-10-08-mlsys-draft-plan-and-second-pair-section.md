# MLSys 2027 draft — the delta from the submitted camera-ready, and the index of the drafted sections

**Date:** 2026-10-08 (sections moved to `docs/drafts/tables/` 2026-10-10) · **Status:** plan, operator-side. Nothing is
manuscript text until the operator approves it paragraph by paragraph (the 2026-10-04 shape: paragraph, then
"Changes, and why" with entry:line per figure). The drafted paragraphs and tables live as `T<nn>` files under
`docs/drafts/tables/`, each with its sources in both forms (entry:line and summary-file key), its conventions and a
re-verify line; this document is the index of what the paper needs. Line numbers below are those of `ledger/ledger.md`
at `0741fdd` (0051 appended).

**Target format** (MLSys 2027's CFP page still says "details … not announced"; MLSys 2026's rules are the proxy): two
columns, **up to 10 pages not including references**, the MLSys 2025 style files, double-blind for the research track
(no names, affiliations, repo names, dataset handles or artifact links in the text — the anonymity denylist
`a6a746d` applies), artifact evaluation voluntary. The 2026 deadline was Oct 30 20:00 UTC; 2027's dates page says
**Oct 30 2026 12:00 PDT** (= 19:00 UTC).

## 1. The delta, by section (what the camera-ready `6c706bef…` has, what the MLSys draft needs)

| where | camera-ready | MLSys draft | source |
|---|---|---|---|
| Abstract, §1, Conclusion | "three receiver models from two families"; "across the tested models" | **four receivers from three families and two source→receiver pairs**, each pair at its own calibrated tolerance; the second pair's long cell at a native receiver | 0044:2947, 0051:3874 |
| §2 / Limitations (App. A) | "cross-model transfer uses a single model pair and a single calibration size on the long cohort" | "two model pairs; the second calibration size on the long cohort is still unrun" (review §6.2); scoping sentences drafted in T03 | 0034 (n = 420 refit), 0044:2971, 0051:3891 |
| App. A, lower-bound sentence | "not a general lower bound … because practical recomputation can propagate errors" | conclusion stands; the **reason** becomes App. D's denominator (0058); "oracle removal fraction" wording throughout | 0058 (whole entry); review §6.1 |
| App. D | "not an achievable recomputation or runtime cost" | stands, now citing the registered reading | 0058 |
| Table 5 caption | "4 exceed 81,920, and 4 have empty receiver prompts" | "4 more exceed 81,920, and 4 others — also over 81,920 — have empty receiver prompts and are excluded for that reason" | review §6.3 (raw records: all four empty-R handoffs have \|S\| 89,296–284,742) |
| Tables 3, 7, App. C, App. F provenance | pilot figures without the 0056 provenance sentence | cite the **registered operator runs** 0048 (same-model extension) and 0049 (cache behaviour) instead; the 0056 clause becomes unnecessary; App. F's three 4th-decimal differences take 0049's values | 0048, 0049; review §2 |
| §3 "still pending" sentences (two) | Condition 1 "still open" | delete; 0054 discharged it | 0054 |
| App. B, Table 4 | Qwen E8 blocks only | add the second pair's k = 1 block (registered 10-sequence arm (b) and the all-sequence amendment); P4 of T03 | 0040:2539, 0053:3540, 3559 |
| **new §4.x "A second source→receiver pair"** | absent | **T03** (`docs/drafts/tables/T03-second-pair-section.md`): one table, P1–P4, the App. A scoping sentences; DRAFT, awaiting per-paragraph approval | 0039, 0042, 0044, 0050, 0051, 0053 |
| §4, E-TRUNC | — | **T02** (`docs/drafts/tables/T02-e-trunc-paragraph.md`): one paragraph (length vs. handoff identity) carrying 0055's two limitations; APPROVED 2026-10-10; the §X cross-reference is filled by a superseding file | 0055, 0057 |
| Lean | no claim | no claim (`lake build` has not run on an operator machine) | CLAUDE.md rule |

Page budget: the camera-ready's main text is ~4 pages in the NeurIPS one-column style; the MLSys two-column 10-page
limit leaves room for the second-pair section (~0.75 page with its table), the moved App. C controls (~0.5 page) and
the E-TRUNC paragraph. Appendices D–F stay appendices.

## 2. The drafted sections

Moved to `docs/drafts/tables/` on 2026-10-10, unchanged in wording:

- **T03 — §4.x second pair** (`T03-second-pair-section.md`): working title, placement, P1–P4 with "Changes, and why",
  the one table (Llama-only, by design), the App. A scoping sentences, and the 2026-10-08 skeptic pass. Status DRAFT.
  Open: whether P2's tail sentence prints in the main text or goes to App. C.
- **T02 — the E-TRUNC paragraph (§4)** (`T02-e-trunc-paragraph.md`): the paragraph approved 2026-10-10 with its
  sources, the 2026-10-10 skeptic pass, and the open §X cross-reference. Immutable; §X is filled by a superseding file.

## 3. What is NOT in this plan

No Lean claim; no E-TRUNC figure beyond the ones T02 reads from 0057; no cache-behaviour or extension figure beyond what 0048
and 0049 state; no sentence about "practical savings" beyond the camera-ready's; no pooled Qwen/Llama number anywhere.
The LaTeX source of the camera-ready is not in this repository (co-authors' Overleaf), so the `T<nn>` files are the paste
source and the ledger lines are their provenance; whoever holds the source applies the delta table.

**Pooled per-token quantiles.** This plan prints none. The rule for printing one (both conventions stated in words,
read from the summary file, skeptic recomputes both) is `docs/drafts/tables/T01-pooled-per-token-quantiles.md`.

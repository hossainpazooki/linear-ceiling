# Carryover — one-screen status for the Wednesday meeting (2026-09-30)

**Where we are.** LCFM @ NeurIPS 2026 submission 126: **Accept** (decision 09-29; two reviews, both 6/10). Workshop is
non-archival; camera-ready date not announced (asked: no — operator to email the organizers). Next venue: **MLSys
2027, deadline Oct 30 2026 12:00 PDT** (30 days). Repo `main` = `118d08e`, gates green on Linux; ledger at 0044.

**What the reviewers want (both reviews reduce to the first line).**

| | weakness | fix | kind |
|---|---|---|---|
| W1 | no behavioral validation of τ_K | **E-BEH**: teacher-force the recorded continuation from fresh vs reused caches; KL + top-1 | experiment (MLSys) |
| W2 | length not isolated | **E-TRUNC**: head-truncate the same 35 senders to 65K / 49K / 32K; common matched subset | experiment (MLSys) |
| W3 | mean passes, tail may not | **E-TAIL**: tail counts, top-10/20 % removed, bin means, attention-weighted δ | Part A = CPU today; Part B = MLSys |
| W4 | "35K-80K" is sender length; receivers ~11.5K; 73 % of tokens inside 32K | abstract clause + two rows | text (+ one entry for the new rows) |
| W5 | Corollary 3 fed medians, needs per-token bounds | restate on bin means (exact), "consistent with" | text + the bin-mean figure (entry) |
| W6 | Prop. 4 "predicts" YaRN carries the tolerance | bridge control is the evidence; drop "predicts" | text |
| W7 | one pair, one family, 50-sequence map | cite n = 420 refit (0034) as reference-instrument caveat; Llama cell once R8 holds | text + (MLSys) |
| W8 | HOLDS vs an expected-worse map | name null pairing, cross arm, τ = 0.03 | text |
| nits | main-conference footer; unrun appendix | workshop class; drop E-RL appendix | text |

**Dependencies, by experiment.**

- E-BEH: cache injection on the receiver side (splice on upstream `kvt/cache.py`, pinned by entry first); a
  continuation extractor from the traces; a card ≥ 40 GB (L40S fits); ≈ 3 h GPU. The load-bearing one.
- E-TRUNC: a `sender_head_truncate` config key + paired summarizer; L40S; ≈ 3-5 h GPU. No upstream change.
- E-TAIL: Part A needs no GPU (35 per-token records are on the home mirror); Part B one R prefill per handoff on any
  20 GB card, < 1 h.
- All three: registered before requested (own entry, thresholds fixed, R1-R12); numbers allocated only by
  `docs/drafts/README.md` (next free 0047).

**Text-only, startable now (camera-ready):** W4 abstract clause, W6, W7, W8 sentences, footer, appendix drop. **Blocked
on the submitted tree** (not on this machine): Cor. 3 / Prop. 4 wording, appendix lettering, Lean diff, the diff itself.

**Rulings needed (operator):** E-BEH bands · E-TRUNC margin + native cell · E-TAIL registered vs descriptive, and whether
its table rides the owed corrective entry into camera-ready · W5 entry (one or two) · Lean restatement ·
de-anonymization at camera-ready · owners below.

**Task slots.**

| slot | owner |
|---|---|
| Camera-ready text patch at the tree (W4, W6, W7, W8, N1, N2) | ??? |
| Corrective entry: tail counts + per-handoff max (+ bin means, |R| row on ruling) — summarizer `--tail` first | ??? |
| E-BEH: injection splice spec + continuation extractor | ??? |
| E-TRUNC: config key + paired summarizer | ??? |
| E-TAIL Part B: chunked attention hook | ??? |
| R8 push of `results/e8f`, `results/e9f` to the two empty Hub datasets | Emerson (per 09-30 note) |
| Co-author refutation of 0025-0029 (Condition 1, Path A) | Ritvik (owed) |
| Camera-ready date: email `longcontextfm@googlegroups.com` | ??? |

Designs: `docs/drafts/e-beh-design.md`, `e-trunc-design.md`, `e-tail-design.md`. Map with ledger anchors:
`docs/2026-09-30-review-response-map.md`.

# Hostile reading of the 02:11 build (2026-09-14)

**Status:** review record, not a ledger entry. **Build:** `farhan_rrhs (1).pdf`, compiled 02:11 EDT 2026-09-14, 9 pages. Every figure checked against ledger entries 0012–0038 and, where the ledger is silent, the public e9l/e9s summary files. **Question:** does the paper's E9 content survive a hostile reader of (i) the coverage clause and (ii) the floor language?

## Attacks that land

1. **"The abstract's 0.93 comes from the run you say is withheld."** Lands. The abstract places both cells under the YaRN receiver; under it the short cell's cross-model f\*(τ_K) is 0.9500 (0038). 0.93 is the native run's 0.9286 (0029). Fix: "selects 0.95 and 0.96 at τK", and print 0.9500 beside the short cell's same-model 0.0000 in §4.1.
2. **"You print the native run's figures while calling it excluded."** Lands. §3.2's |M|/|R| 0.9344 and null 2.009/1.962 exist only in 0029; §4.1's 0.0195 and 0.1433 are 0029's results restated as 0038's baseline. 0032 (kept by 0035) withholds the figures, not only the verdict, and no entry lifts that. Fix: §3.2 prints the long cohort's own controls (0.9606; 2.015/1.975, 0036). §4.1's native legs need the lead author's ruling: drop them, or keep them and record the exception in an entry.
3. **"Where do bridge R² 0.8932 / 0.8603 come from?"** Lands. No entry carries them; they are the median of three per-handoff values in a summary file. Fix: the ledger's own bridge figures — zero native-versus-scaled f\*(τ_K) and f\*(τ_V), per-handoff median δ_K 0.071–0.089 (0036).
4. **"The bridge says nothing about the positions past 32,768 that the verdict reads."** Lands on wording. The three bridge handoffs are 13,955–17,935 tokens and the registered reading concerns τ_K only; "the tolerance carries across these controls" overstates it. Fix: "by the registered reading, τK carries to the scaled receiver on these handoffs, all under 32,768 tokens."
5. **"The scaled receiver isn't the model."** Lands unless said. 0035: static YaRN changes the KV of short contexts too, so this receiver is a different function from the native one. Fix: say so in the first sentence of the bridge paragraph.
6. **"The matched comparison was designed after you saw both cells."** Lands unless disclosed. 0037 (13 Sep) follows 0029 (4 Sep) and 0036 (10 Sep) and cites their gap. It was registered before its own prefill. Fix: "a post hoc descriptive comparison, registered before its own prefill".
7. **"Table 1 says 4 handoffs exceed 81,920; your data say 8."** Lands. The 4 empty-receiver handoffs have |S| 89,296–284,742 (public coverage file, recomputed today), so 8 of 68 exceed 81,920. 0035 states the split as exclusion reasons: 25 / 35 / 4 above / 4 empty receiver.
8. **"Limitations explains a native-versus-YaRN comparison the paper no longer makes, and forgets the short handoffs."** Lands. Fix: "25 short and 35 long handoffs from one coding-agent system, not a random sample" (two submissions of one system, alphabetically first tasks: 0013, 0024) and "the short and long cohorts are different handoffs, so their differences cannot be attributed to length; both use a YaRN-scaled receiver."
9. **"You predict the result of a study you haven't run."** Lands. Appendix F: "We hypothesize that small weight updates change caches less than cross-model transfer does." The abstract's "far end / near end" implies the same ordering. Four mentions omit "designed" or "unrun". Fix: delete the hypothesis; every mention reads "designed, unregistered and unrun".
10. **"A zero fraction means no token is off."** Half-lands, in the Conclusion only. f\* is 0023's mean-repair statistic; §4.1, §5 and Appendix D say individual tokens exceed τ_K, but the Conclusion reads as every token staying within tolerance. In the short cell a median 4–5% of matched tokens exceed τ_K while f\* is 0 (0038); on four retained short handoffs re-scored today, 215 of 3,362 to 636 of 4,485. Fix: "matched-token mean deviation can stay within…".
11. **"Your controls are exactly zero, so they could never have failed."** Partly lands. Identity scores a dump against itself; prefix invariance tests causal masking. Sensitivity is shown by the null (≈ 2.0) and the bridge's nonzero deviations, not by these controls. Fix: name the halt tolerances (0 and 1e-4) and never cite the controls as proof of sensitivity.

## Attacks that fail

- **Mean-repair statistic.** Defined correctly in §3.2 and Appendix D; the paper never copies 0029/0036's exceedance wording.
- **"0.29 vs 0.53 is a length effect."** The abstract says the contrast does not isolate length, and 0038's configuration share (0.43 far from seam, 0.39 at τ = 0.03) supports reporting both configuration and handoffs.
- **"None reproduces its prefix byte for byte ignores the hidden prefix."** Still true (0018: 0/68), and lengths are labelled lower bounds.
- **Registration dates, stopping rule, 35 of 35 scored.** Match 0035 and 0036.

## Needs a ruling, not a sentence

- **Table 1** prints entry 0025 figures from the window whose co-author verification is still owed (0032, 0035; nothing through 0038 records it). The |S|/|R| rows recompute exactly from the public coverage file (checked today on a second machine); the overlap row does not recompute from public data.
- **Figure 3 and Appendix B's normalization diagnostic** come only from summarizer output, on no entry.
- **The band edges** carry no stated source: 0023 anchors HOLDS 0.15 to CacheBlend (whose 15% is a per-layer default recompute ratio, arXiv 2405.16444 §5) and calls DEGRADES 0.50 the operator's judgment. Say so in Appendix D.
- **The re-verification sentence** in Limitations cites review records (8 and 14 September), not ledger entries.
- **The upload file name** contains a team member's name.

Companion records: `docs/reviews/2026-09-14-e9-cold-rescore-second-machine.md`; the paste-ready edits are in the author's local `emerson-draft/2026-09-14-fixes/`.

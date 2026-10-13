# T02 — The E-TRUNC paragraph (§4): length vs. handoff identity

status: APPROVED 2026-10-10 (operator, paragraph approved in the draft plan §2c the same day; moved here unchanged;
  immutable from this commit — the §X cross-reference is filled by a superseding file)
sources: ledger lines at `71c4cef` (0057 appended) — 0055:3406, 3410–3414, 3423, 3515–3516; 0057:3990–3992,
  3997–4000, 4000, 4004–4008, 4017–4018; 0038:2360–2361. Files — `results/e9t/compare.json` (sha256 `0572662307f3…`):
  `n_void`, `n_used`, `n_common_total`, `min_common_matched`, `reading.{far_from_seam_median_on_M_cap,
  full_far_from_seam_median_on_M_cap, short_scaled_level, long_level, margin_abs, reads_as}`,
  `by_level.<level>.fstar_median_over_handoffs["0.3186"]`, `by_level.L32768.paired_mean_delta_K_minus_full.{median,
  bootstrap.lower_2.5, bootstrap.upper_97.5}`; `results/e9s/compare.json` (`a0699a826f1f…`): `configuration_share.seam_far`,
  `long_cell.seam_far_median`, `seam_profile_left_pooled` 16+ bin `median_native` / `median_scaled`
conventions: four decimals, as the ledger prints them; pooled medians are `np.median` and over-handoff medians
  `statistics.median` (identical values); the paired interval is a seeded percentile bootstrap (seed 52, 2,000 reps)
  read with `e7_stats.quantile`, reported, not read; the ±0.005 margin is 0055's pre-registered reading rule
re-verify: .venv/Scripts/python.exe -c "import json;t=json.load(open('results/e9t/compare.json'));s=json.load(open('results/e9s/compare.json'));r=t['reading'];p=t['by_level']['L32768']['paired_mean_delta_K_minus_full'];print(t['n_void'],t['n_used'],t['n_common_total'],round(r['far_from_seam_median_on_M_cap'],4),round(r['full_far_from_seam_median_on_M_cap'],4),round(p['median'],4),round(p['bootstrap']['lower_2.5'],4),round(p['bootstrap']['upper_97.5'],4),r['reads_as'],round(s['configuration_share']['seam_far'],4),[t['by_level'][l]['fstar_median_over_handoffs']['0.3186'] for l in t['by_level']])"   # 14 21 154620 0.0868 0.1112 -0.0257 -0.0434 0.0024 unattributed 0.4285 [0.0, 0.0, 0.0, 0.0]

Placement: §4, after the second-pair section (T03); one paragraph, no table, descriptive, no cell moves. Every figure
was read from the two JSON files at drafting, not from entry prose.

> **Does length alone move the far-from-seam deviation?** The short and long cohorts are different handoffs, so their
> far-from-seam same-K medians (native short 0.0195, scaled short 0.0381, long 0.0629) confound context length with
> handoff identity. The move from the native to the scaled receiver, measured on identical tokens, accounts for 0.4285
> of the native-short to long gap; the remainder, from 0.0381 to 0.0629, was unattributed. E-TRUNC varies length within
> a handoff. Under causal attention a matched token's reused K/V depend only on the sender prefix before it, so we
> truncate the sender's head, S′ = S[−L:], at L = 65,536, 49,152 and 32,768 beside the full sender, on the 35 long
> handoffs under the same YaRN receiver, and compare on the tokens matched under every level. Fourteen handoffs fall
> below the pre-registered floor of 2,000 common tokens and are void; 21 enter, with 154,620 common tokens. Median
> f*(τ_K) is 0 at every level. At the native-window level L = 32,768 the far-from-seam pooled median on the common
> tokens is 0.0868, against 0.1112 for the full sender on the same tokens; the paired per-handoff difference has median
> −0.0257 with a bootstrap 95 % interval [−0.0434, 0.0024] that includes zero, so no per-handoff direction is claimed.
> Under the pre-registered ±0.005 margin against the two cohort levels the result reads as unattributed: shortening the
> causal prefix to the native window lowers the pooled median but does not bring it to the short cohort's level, and
> the value sits above both references. The common subset lies at late sender positions, whereas the two cohort medians
> pool their full matched sets. Two limitations are registered. The comparison speaks for the handoffs whose receiver
> re-renders enough late sender context to survive head truncation, not for the long cohort as a whole; and every level
> runs under the YaRN receiver, so nothing here compares a native with a scaled receiver on the same tokens, where the
> bridge control (§X) remains the only evidence.

Sources, and why each sentence is there:

- Cohort medians and the confound — 0055:3410–3411 ("the residual is unattributed because the short and long cohorts
  are different handoffs"). 0.0195 / 0.0381 / 0.0629 and the share's definition (scaled − native) / (long − native) —
  0038:2360–2361; recomputed from `results/e9s/compare.json` (16+ bin `median_native`, `median_scaled`,
  `long_cell.seam_far_median`, `configuration_share.seam_far`). Motivates the run: says what "unattributed" is the
  residual of.
- Causal-prefix argument and head truncation — 0055:3412–3414.
- Levels, 35 handoffs, same YaRN receiver, the common subset — 0055:3406.
- Floor 2,000, 14 void, 21 enter, 154,620 common tokens — 0057:3990–3992; `n_void`, `n_used`, `n_common_total`,
  `min_common_matched`; the void set recomputed from the per-handoff block.
- Median f*(τ_K) 0 at every level — 0057:3997–4000; `by_level.*.fstar_median_over_handoffs["0.3186"]`. "Median"
  because the file holds the median over handoffs; the per-level summaries are not on the drafting machine.
- 0.0868 vs 0.1112, paired median and bootstrap interval — 0057:4000, 4008; `reading`,
  `by_level.L32768.paired_mean_delta_K_minus_full`.
- Reading word, above both references, not to the short level — 0057:4004–4008, resting on 0055's ruling (1) wording
  at 3423.
- Late-positions caveat — 0057:4006–4007; the entry states it beside the reading, so the paper does too.
- Limitation 1 — 0057:3992 (0055:3515). Limitation 2 and the bridge control as the only native-vs-scaled evidence on
  the same tokens — 0057:4017–4018 (0055:3516).

Skeptic pass (2026-10-10, read-only `skeptic-verifier`): every number recomputed from the two JSON files at four
decimals, CONFIRMED; claims checked line by line against 0055/0057, CONFIRMED; the paraphrase scorer reports no scope
overlap (max 0.08 against 0.45). REFUTED and corrected: the first draft paired the 0.4285 share with the scaled-short
to long gap; the share is the native-to-scaled move's part of the native-short to long gap, and the scaled-to-long gap
is the residual. Also corrected: "f*" to "median f*".

Open at approval: the section number for the bridge-control cross-reference (§X), set once the App. C controls have
their place in the main text. This file is immutable; the file that fills §X supersedes it and says so in its header.

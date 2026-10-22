# T05 — The E-BEH subsection (§4): does reading the assembled cache move the receiver's predictions?

status: P1 APPROVED 2026-10-15 (operator; skeptic pass the same day, one citation added before approval; P1 immutable
  from this commit). P2 (the repair arms) waits for entry 0061's run and its figures entry; P3 (scope and the practitioner
  band) waits for the band entry or the ruling that none exists. Operator ruling 2026-10-15: a half-page subsection, last in the
  results section, after T02.
sources: ledger lines at `fe15202` — 0047:3214–3215 (τ_K not validated against anything the receiver does), 0047:3217–3218 (teacher-forced on the recorded continuation; prediction sensitivity
  on fixed text), 0047:3223 (fp32, SDPA, the long cell's YaRN schedule), 0047:3227–3230 (the 35 handoffs of 0036, archived
  alignment pairs as M, continuation capped at 256 tokens), 0047:3237–3239 (RANDOM norm-matched; CYCLIC permuted with keys
  relocated), 0047:3250–3251 (readout: KL(p_FRESH ‖ p_ARM) and top-1 per token; per handoff mean KL, p90 KL, top-1 rate; over
  the 35 the median with p10 / p90 by `e7_stats`), 0049:3761–3763 (the three arms' medians), 0049:3768, 0049:3771 ("No
  downstream task-quality number is claimed"). File — `results/cache-behavior/summary.json` (sha256 `5228de0dd8c4…`, the
  file 0049 pins): `arms.{reuse,random,scrambled}.{mean_kl,top1_agreement}.median`; `interpretation`.
conventions: four decimals, as the ledger prints them; `scrambled` is the summary file's key for the arm the ledger
  names CYCLIC (0049; paper-to-record alias); medians over handoffs are `e7_stats` nearest-rank; handoffs weighted equally.
re-verify: .venv/Scripts/python.exe -c "import json;a=json.load(open('results/cache-behavior/summary.json'))['arms'];print({k:(round(a[k]['mean_kl']['median'],4),round(a[k]['top1_agreement']['median'],4)) for k in ('reuse','random','scrambled')})"   # {'reuse': (0.1424, 0.902), 'random': (11.2981, 0.0471), 'scrambled': (0.2826, 0.8549)}

Placement: §4, after the E-TRUNC paragraph (T02); half a page; no table in P1. Every figure was read from the summary
file at drafting, not from entry prose.

## P1 — the behavioural check (APPROVED 2026-10-15)

> **Does reading the assembled cache move the receiver's predictions?** A token's deviation in R²'s units says how far
> its reused key sits from the fresh one, not what the receiver does with it. E-BEH asks the behavioural question on the
> 35 long handoffs: the receiver prefills its own prompt with the matched tokens' K/V taken from the sender's cache, keys
> relocated to their receiver positions, and we compare its next-token distribution with a fresh prefill of the same
> text, teacher-forced on the recorded continuation (at most 256 tokens). Per handoff we take the mean KL(p_fresh ‖ p_arm)
> over the continuation and the top-1 agreement rate; over handoffs, the median. Reusing the whole assembled cache gives
> a median mean KL of 0.1424 nats and top-1 agreement of 0.9020; a norm-matched random perturbation of the same states
> gives 11.2981 nats and 0.0471; permuting the matched states across the matched set, keys relocated, gives 0.2826 nats
> and 0.8549. These are prediction-sensitivity figures on fixed text: no downstream task-quality number is claimed, and
> no acceptance band is registered.

Changes, and why:
- Opening question and the R²-units sentence: the subsection has to say why a behavioural check exists beside f*;
  0047:3214–3215 ("τ_K is a weak linear map's error and is not validated against anything the receiver does") carries
  the first half, 0047:3217–3218 ("prediction sensitivity on fixed text, not coding-task quality") the second.
- "35 long handoffs … keys relocated … teacher-forced on the recorded continuation (at most 256 tokens)": 0047:3227–3230
  (inputs, the 256-token cap) and the relocation step the driver's `core.relocate` performs (0047's instrument).
- The readout sentence: 0047:3250–3251, restated without p90 KL and p10 / p90 (P1 carries medians only; the spread can go
  in a table if the subsection gets one).
- The three figures: 0049:3761–3763, read again from `summary.json` `5228de0dd8c4…` at drafting (re-verify line).
- "norm-matched random perturbation" and "permuting the matched states across the matched set, keys relocated":
  0047:3237–3239's two controls, in the ledger's own words; "cyclic" avoided because the summary file calls the arm
  `scrambled` and the paper should not introduce a third name.
- Last sentence: 0049:3771 verbatim in substance; "no acceptance band is registered" is 0047's "No band is registered"
  and leaves the slot the practitioner band entry would fill.

Not said, on purpose: any quality or serving-cost reading of the KL (0049 forbids it); the attention-slice figures
(0047 records them "not as the object of this entry"); the repair arms (P2, after 0061 runs).

## P2 — the repair arms (NOT DRAFTED: waits for entry 0061's run and its figures entry)

## P3 — scope, and the practitioner band (NOT DRAFTED: waits for the band entry, or the ruling that none exists)

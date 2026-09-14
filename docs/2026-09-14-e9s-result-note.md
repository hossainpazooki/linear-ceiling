# E9 scaled short cell — result note for a co-author read

**Date:** 2026-09-14 · **Ask:** an out-of-loop read of entry 0038 and the compare output before the 11:59Z deadline.

## What was run

0029's 25 short handoffs, re-measured under the same YaRN-2.5 receiver that 0036 used, so the two paper cells now share a
receiver configuration. Registered as **0037** before any prefill; figures in **0038** (`ledger/ledger.md`, on `main`).
Descriptive: no hypothesis row, no verdict moves.

- Rented L40S, 02:26–02:56Z, **25 of 25 scored**, no partial close.
- On-box memory probe matched 09-10: 1.7B 16.70 GiB, 0.6B 10.89 GiB at 32K.
- Home mirror verified file by file (770/770).
- Backup verified in both directions: public dataset
  [`anon/linear-ceiling-e9s-2026-09-13`](https://huggingface.co/datasets/anon/linear-ceiling-e9s-2026-09-13).

**One process slip, stated in 0038.** The summarizer first refused: this cell had no τ calibration of its own. The runbook
omitted the step and the pre-run gate does not check for it. It was run after the GPU run; it reads nothing from the run
and reproduced τ_K, τ_V and τ_agent_K exactly. Both readers then passed.

## The result

On identical tokens, the scaled receiver raises the per-handoff mean δ_K by a median **0.0165** (bootstrap
[0.0152, 0.0171]); same-model f*(τ_K) stays **0.0000**.

Configuration share = (scaled − native) / (long − native):

| reading | native (0029) | scaled (0038) | long (0036) | share |
|---|---|---|---|---|
| far-from-seam (16+) median δ_K | 0.0195 | 0.0381 | 0.0629 | **0.43** |
| f* median at τ = 0.03 | 0.1433 | 0.2930 | 0.5255 | **0.39** |
| f* median at τ = 0.1 | 0.0000 | 0.0000 | 0.0119 | 0 by construction (both short medians are 0) |

## What it means for the paper

0037's reading, fixed before any prefill: a share near 1 means the receiver configuration accounts for the cross-cell
difference; near 0, the handoffs do; **in between, the paper reports both**. So §4.2 gets one sentence per length
descriptive: about two-fifths is the receiver configuration, the rest the handoffs, length among them. It is not a claim
about length alone, because the long cell is different handoffs.

## What to read

- Entry **0038** in `ledger/ledger.md` (and 0037 for the registered reading).
- `results/e9s/compare.md` — local to the repo by rule; also in the dataset above under the same path.
- The sitting log: `docs/2026-09-13-e9s-gpu-runbook.md` §6.

**If you can't get to it in time, or something doesn't hold up:** the submission goes out on 0029 + 0036 with the
configuration difference stated as a limitation, and this result waits for the camera-ready.

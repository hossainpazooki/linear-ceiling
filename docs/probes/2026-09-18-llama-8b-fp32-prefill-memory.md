# Probe: Llama-3.1-8B fp32 prefill memory, 16K–32K — 2026-09-18

**This is a PROBE, not a result.** It informs card choice for sitting B and nothing else. It moves no
registered parameter, decides no hypothesis, and no number here may enter a ledger entry as a finding.
It ran on an already-paid card after sitting A's artifacts were pulled home and verified, and it wrote
nothing into `results/`, `data/`, `mappers/` or the sitting-A pull set — the script only prints JSON to
stdout.

## The question

Does the E9 short cell (`config/e9f.toml`, cap 32,768) fit a 48 GB card at ~$0.49–0.79/h, or does it
need an 80 GB card at ~$1.19–1.59/h? The runbook's answer was an **extrapolation** — 45.2 GiB estimated
against an L40S's measured 44.39 GiB usable — and nothing in this program had ever measured an 8B fp32
forward. The difference is worth $1.1–2.5 on sitting B alone.

## Conditions

| | |
|---|---|
| card | NVIDIA A40, 44.43 GiB total, 44.17 GiB free at start |
| driver stack | torch 2.11.0+cu128, the pinned sitting-A venv |
| attention | `sdpa_repeat_kv` (the registered backend; confirmed in the probe output) |
| dtype | float32 |
| rope | `null` — the **native, unscaled** path, since `config/e9f.toml` carries no `[e9.rope]` |
| config read | `config/e9f.toml` **as committed and registered**, unmodified |
| threads | `OMP/OPENBLAS/MKL_NUM_THREADS=8` |
| tool | `tools/ec2/probe_e9l.py`, `EXP=e9f`, ladder `16384,24576,32768` |

The probe reads the registered config through raw `tomllib` and takes only `pair`, `rope` and
`handoffs.context_cap` from it. It never calls `load_e9_config`, so the config's UNRESOLVED τ markers
are irrelevant to it — **no config was edited and no scratch copy was made.**

## What it measured

| model | T | peak GiB | wall s | ok |
|---|---:|---:|---:|---|
| meta-llama/Llama-3.1-8B (receiver, 29.92 GiB weights) | 16,384 | 37.56 | 18.0 | yes |
| | 24,576 | 41.38 | 30.3 | yes |
| | **32,768** | **43.2 at failure** | — | **CUDA OUT OF MEMORY** |
| meta-llama/Llama-3.2-3B (source, 11.98 GiB weights) | 16,384 | 17.74 | 8.6 | yes |
| | 24,576 | 20.63 | 15.3 | yes |
| | 32,768 | 23.51 | 23.3 | yes |

Recorded alongside: the receiver declares `rope_type llama3`, `factor 8.0`; the source `factor 32.0` —
different per side, as expected, and the reason every RoPE-identity assertion downstream is role-scoped.

## Reading

**The E9 short cell does not fit a 48 GB card.** The receiver OOMs at the cell's own registered cap of
32,768 with 43.2 GiB peak on a 44.43 GiB card — and this is the *floor*, because the probe measures a
single model doing one forward. The E9 driver is strictly heavier: it holds the receiver and performs
three stride-1 dumps per handoff, plus the identity, null and prefix-invariance controls. Sitting B
therefore needs an **80 GB card**, and the runbook's extrapolated 45.2 GiB was right in direction.

The source model is not the constraint at any rung.

This does not close the question of what the E9 driver's true peak is — only that 48 GB is already
insufficient for the easier single-model case, which is enough to decide the card.

## Cost

~3 minutes on a card already rented and already loaded, ≈$0.03. It prevented renting a 48 GB card for
sitting B and discovering the OOM after paying for it.

## Raw record

`~/.cache/linear-ceiling/sitting-a-pull/probe_e9f.jsonl` (10 JSON lines, pulled home before the pod was
terminated). Not committed: it is scratch evidence, and `results/` never enters git history.

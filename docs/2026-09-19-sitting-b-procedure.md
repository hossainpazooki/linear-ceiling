# Sitting B — the literal procedure

**One page, in order, copy-pasteable.** The reasoning lives in `docs/2026-09-18-llama-gpu-runbook.md`
§8 and in `docs/gpu-experiment-protocol.md`; this is the thing you read with a pod billing.

Cell: **E9F**, the verdict-bearing cell of the Llama campaign — `llama3.2-3b-to-llama3.1-8b`,
28 included handoffs, cap 32,768 Llama-3 tokens, native receiver (no bridge). Registered by ledger
entry **0042**, which also registers the stopping rule (`by = "n_sender_asc"`, `allow_partial = true`).

---

## 0. Before anything bills

| | check | how |
|---|---|---|
| a | **the pre-prefill amendment is on the ledger** | it registers the atomic checkpoint write and the stop protocol below; a run started before it is a run whose stopping rule was fixed after the instrument changed |
| b | **upstream commit P exists at the pin** | `06f8d55592570deae70c3feb9f84a75c4044fb03` — currently on `emersony99/kv-transfer-replication`, pending `hossainpazooki/kv-transfer-replication#1`. That PR must merge **without squash or rebase** or the sha dies and `e9 --check` refuses |
| c | `e9 --check --config config/e9f.toml` prints ready from a **fresh clone** | the registering entry is committed and pushed |
| d | `summarize_e9 --calibrate-tau --config config/e9f.toml --e8-report results/e8f/report.json` **has run** | the gate never looks at `tau.json`; skipping this is how 2026-09-14's card was released before the summarizer refused |
| e | weights staged | `box-cache/hub/` holds both models, `*.json` + `*.safetensors` + `tokenizer*` only, tarred to `hf-cache.tar.gz` |
| f | **the three-scenario rehearsal passes** | `pytest -q tests/test_sitting_b_rehearsal.py` |

## 1. The inputs, by sha

| input | sha256 | size |
|---|---|---|
| `k1.json` | `6cbfad42b6b08d3a39c770dd6313d7d7cfc6035555c03aed1dc4c549828c27fb` | 870 B |
| `k1.safetensors` | `fe77166a8ff4f7d55230486806679f6a91acd24c4efb305fdf9a93556a2869fc` | 268,707,688 B |
| `results/e9f/align/coverage.json` (home) | `c0764a05f4869747806b6c2a5442935c411c894d1fe99b3a66655f5dc0c086ec` | — |

Source: `~/e9-repro/kv-transfer-replication/mappers/llama3.2-3b-to-llama3.1-8b/`. Irreplaceable
without renting another card.

## 2. Rent

```bash
.venv/bin/python tools/runpod/rp.py price --gpu "NVIDIA A100 80GB PCIe"     # or H100 PCIe
.venv/bin/python tools/runpod/rp.py up --gpu "<id from price>" --price <$/h> \
    --hours 5.5 --sitting-max 6.55 --disk 250 \
    --verify-file ~/.cache/linear-ceiling/e9f-verified.json --dry-run
# read the dry run, then repeat with --yes
```

**80 GB card, not 48.** Measured, not guessed: `docs/probes/2026-09-18-llama-8b-fp32-prefill-memory.md`
— Llama-3.1-8B fp32 OOMs at T = 32,768 on a 44.43 GiB card, peak 43.2 GiB.

**Never pass `--terminate-after`.** It is a provider-side hard kill that cannot be extended without
editing the pod, which at `volumeInGb 0` wipes `/workspace` mid-run. A sitting B that overruns would
be destroyed rather than closed under the registered partial rule.

## 3. Arm the net — IMMEDIATELY, before the driver

```bash
nohup bash tools/runpod/watchdog_supervised.sh > /dev/null 2>&1 &
tail -f ~/.cache/linear-ceiling/watchdog-supervisor.log
```

It restarts `rp.py watchdog` on any non-zero exit, forever, and stands down only when two consecutive
polls see nothing billing. On 2026-09-18 a single watchdog died on an SSL EOF and a pod billed
unwatched for five minutes.

## 4. Stage and launch

```bash
.venv/bin/python tools/runpod/rp.py wait-ssh
.venv/bin/python tools/runpod/rp.py put <k1.json> <k1.safetensors> traces.tar.gz \
    results/e9f/calibration/tau.json hf-cache.tar.gz tools/runpod/sitting_b.sh
.venv/bin/python tools/runpod/rp.py ssh 'EXP=e9f \
  PAIR=llama3.2-3b-to-llama3.1-8b \
  UP_REPO=<remote> UP_SHA=06f8d55592570deae70c3feb9f84a75c4044fb03 \
  LC_REPO=<remote> LC_SHA=<the pushed commit> \
  MAPPER_JSON_SHA=6cbfad42b6b08d3a39c770dd6313d7d7cfc6035555c03aed1dc4c549828c27fb \
  MAPPER_ST_SHA=fe77166a8ff4f7d55230486806679f6a91acd24c4efb305fdf9a93556a2869fc \
  COVERAGE_SHA256=c0764a05f4869747806b6c2a5442935c411c894d1fe99b3a66655f5dc0c086ec \
  bash /workspace/sitting_b.sh'
```

The launcher runs the R2 probe before any weights and **refuses below 70 GiB of usable VRAM**. Stop if
it refuses; that refusal is the measurement replacing §3.4's extrapolation.

## 5. Pull, from the moment the driver starts

```bash
nohup .venv/bin/python tools/runpod/pull_verify_b.py --delete-verified \
    > ~/.cache/linear-ceiling/pull-e9f.log 2>&1 &
```

Every handoff: verify against `report.json`'s fingerprints → delete that tree on the box → snapshot
the checkpoint to `results/e9f/checkpoints/report.<n>.json` if every artifact it names verifies here.
Add `--terminate-on-receipt` to close the billing window the instant the receipt exists.

Exit codes: **0** verified and receipted · **3** `--once` and not done · **4** `--final-partial`
refused · **5** the box wrote `SITTING_B_FAILED` (terminal — go to §7).

## 6. The disk and time budgets

Per-handoff dump bytes are `n_sender × 245,760 + n_receiver × 131,072`, computed from
`coverage.json`, not estimated:

| | GiB |
|---|---|
| largest single handoff's dumps | **8.57** |
| keep subset (8 handoffs), the pull target | **50.12** |
| all 28, never resident — non-kept dumps are deleted per handoff | 168.93 |

The table above is what the PULLER moves. The box additionally **writes** up to 12.4 GB of dumps per
handoff at the cap (`same_src` 4.30 + `same_tgt` 4.30 + `cross_src` 3.76, runbook §3.5) and deletes
each non-kept set after scoring.

**Box disk, 250 GB container:** weights 22.5 + two venvs ≈ 8 + repos/traces ≈ 2 + the working
handoff ≤ 12.4 + kept trees awaiting pull ≤ 50.1 ⇒ **≈ 95 GiB peak**, and that last term only reaches
50 if the puller never deletes. **Home disk:** the floor is *outstanding kept bytes + 10 GiB*,
re-derived every round — never a constant, which froze the puller against its own downloads once.

**Time.** ~85 model loads (28 handoffs × 3 dumps, plus the controls on the first). The load cost is
the **one assumed term** in this model and everything else follows from it; `--hours 5.5` with
`--sitting-max 6.55` is set against the assumption that it holds.

> **Go/no-go at handoff 5.** By then the measured per-handoff wall clock is real. Project
> `t_remaining = (28 − n) × median(t_handoff)`. If that lands past the TTL, **drain now** (§7) rather
> than at the ceiling: a drained partial is a registered outcome, a hard kill is a salvage.

## 7. How it ends — the three ways, and only these

### Complete
The puller prints `COMPLETE:` and writes the receipt. Terminate (`--terminate-on-receipt`, or
`rp.py terminate`), then §10/§11 of the runbook, then `summarize_e9 --config config/e9f.toml`.

### Drain → registered partial *(the intended budget stop)*
1. Stop the driver **by signal**, between handoffs. The last checkpoint stays intact.
2. Let the puller finish the tensors already written.
3. `pull_verify_b.py --final-partial` — pulls nothing. It refuses unless the driver is provably
   stopped, proves the last fully verified checkpoint, and writes the receipt with `partial{n_scored}`.
4. `.venv/bin/python -m linear_ceiling.e9 --close-partial --config config/e9f.toml`.

### Hard kill → last verified snapshot → close at home
The ceiling fired mid-handoff; `report.json` names a tensor that never arrived and the box is gone.
Steps 3 and 4 are **identical** — `--final-partial` falls back to the highest
`checkpoints/report.<n>.json` that verifies whole, installs it as `report.json` (keeping the
superseded file as evidence), and the close stamps that prefix.

**The closing basis is always the last checkpoint whose every named artifact is sha-verified at
home.** It is a genuine driver checkpoint and a prefix of the registered order — never an edited
report. If nothing verifies whole, there is no close: H-E9F stays `unresolved`, and that is the
finding, not a problem to work around.

## 8. Prove it is gone

```bash
.venv/bin/python tools/runpod/rp.py ps        # must list nothing
.venv/bin/python tools/runpod/rp.py spend
```

R7 step 6: prove absence from the API, never assume it. `sudo shutdown` on a RunPod container does
**not** stop billing, and "stopped" is not "terminated".

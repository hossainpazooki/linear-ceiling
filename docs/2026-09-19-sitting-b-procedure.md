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
| e | weights staged | **done 2026-09-19.** `~/Desktop/linear-ceiling/box-cache/hub/` — Llama-3.2-3B 5.99 GiB (2 shards) + Llama-3.1-8B 14.97 GiB (4 shards), `*.json` + `*.safetensors` + `tokenizer*` only, **0 token files**, and it passes `sitting_b.sh`'s own `cache_complete` for both. Tar to `hf-cache.tar.gz` for the no-token path |
| f | **the three-scenario rehearsal passes** | `pytest -q tests/test_sitting_b_rehearsal.py` |

## 1. The inputs, by sha

| input | sha256 | size |
|---|---|---|
| `k1.json` | `6cbfad42b6b08d3a39c770dd6313d7d7cfc6035555c03aed1dc4c549828c27fb` | 870 B |
| `k1.safetensors` | `fe77166a8ff4f7d55230486806679f6a91acd24c4efb305fdf9a93556a2869fc` | 268,707,688 B |
| `results/e9f/align/coverage.json` (home) | `c0764a05f4869747806b6c2a5442935c411c894d1fe99b3a66655f5dc0c086ec` | — |

Source: `~/e9-repro/kv-transfer-replication/mappers/llama3.2-3b-to-llama3.1-8b/`. Irreplaceable
without renting another card.

## 1a. The home disk, and why the order matters

Staging the weights took `/Users` to **57 GiB free**, which is under the puller's 65 GiB pre-create
gate. That gate is not wrong and must not be lowered — the kept dumps really do need 50.12 GiB. What
is wrong is asking "is there room now" when the question is "will there be room when the first kept
dump lands". The 21 GiB of staged weights is dead the moment the box has verified them.

So the sequence is fixed, and the puller is told about it rather than lied to:

1. Upload `hf-cache.tar.gz` (§4).
2. The box's sha check passes on **every shard** — `sitting_b.sh` extracts, validates the archive
   (hub/ only, no token files, no escaping links) and then re-runs `cache_complete`.
3. **Delete `~/Desktop/linear-ceiling/box-cache` at home and log the freed bytes.** Both models are
   re-downloadable from the Hub with the ambient login, which is the operator's stated condition for
   clearing anything off this disk.
4. Only then can the first kept dump land. It is at run position 4 (3.9 GiB), roughly 35 billed
   minutes in, so step 3 has time — but it is not automatic.

Start the puller with the promise named, so the gate is honest and auditable:

```bash
tools/runpod/pull_verify_b.py --delete-verified     --reclaimable ~/Desktop/linear-ceiling/box-cache
```

`--reclaimable` counts **only** in the pre-create check. The running floor stays
*outstanding + 10 GiB of real free space*, so if step 3 never happens the puller **pauses and says
so** instead of filling the disk. Nothing on the box is deleted while it is paused.

> Also reclaimable, ~6.0 GiB: `~/.cache/huggingface/hub/models--meta-llama--Llama-3.2-3B`, a
> duplicate of what was staged. Not needed to pass the gate (57 + 21 = 78 ≥ 65), so it is left alone;
> it is the next thing to clear if the margin tightens.

## 2. Rent

```bash
# re-query BOTH clouds immediately before creating; stock and price move
.venv/bin/python tools/runpod/rp.py price --gpu "NVIDIA A100 80GB PCIe"
.venv/bin/python tools/runpod/rp.py up --gpu "<id from price>" --price <$/h> \
    --hours 6.0 --sitting-max 7.14 --max-price 1.25 --disk 250 \
    --verify-file ~/.cache/linear-ceiling/e9f-verified.json --dry-run
# read the dry run, then repeat with --yes
```

**The ceiling is `--hours 6.0 / --sitting-max 7.14`, and the reason is the drain, not the bill.**
Entry 0043 puts the drain at 70% of the sitting ceiling, and a measurement may only move it earlier.
So the ceiling is what *positions* the drain:

| | at `--sitting-max 6.55` | at **7.14** |
|---|---|---|
| drain fires at | 3.85 h | **4.2 h** |
| P90 compute end | ~3.75 h | ~3.75 h |
| margin | ~6 min — a healthy slow run is drained into a partial | **~27 min**, and 1.8 h left for the pull tail and the backstop |

Timeline behind those figures (no-token path): create → setup ~10 min → weight upload ~32 min →
driver starts ≈ 0.75 h → compute 1.9–3.0 h → compute ends 2.65–3.75 h → pull tail 0.4–0.7 h → verify,
terminate. **A healthy run costs the same either way (~$3.6–5.4);** only a bad run pays for the extra
headroom. Campaign worst case: $1.44 already spent + $7.14 = **$8.58 against the $10 cap**.

Fallback if the A100 80 GB is unavailable: A100 SXM community, then A100 PCIe secure. A fallback that
needs `--max-price` above 1.25 is **not** a silent retry — it is a decision to take back to the
operator.

**80 GB card, not 48.** Measured, not guessed: `docs/probes/2026-09-18-llama-8b-fp32-prefill-memory.md`
— Llama-3.1-8B fp32 OOMs at T = 32,768 on a 44.43 GiB card, peak 43.2 GiB.

**Never pass `--terminate-after`.** It is a provider-side hard kill that cannot be extended without
editing the pod, which at `volumeInGb 0` wipes `/workspace` mid-run. A sitting B that overruns would
be destroyed rather than closed under the registered partial rule.

**Pushed sha at the last rehearsal:** `659c5d6`. `config/e9f.toml` sha256 `2e7cade40489`, coverage
`6a8dc1242300`, gate `0019/0023/0025/0027/0042/0043`. Re-run §0f after any change to the config — the
gate checks it is committed unmodified and the coverage is bound to its sha.

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

**The weight upload, and the deletion that frees the home disk (§1a).** `sitting_b.sh` validates the
archive (hub/ only, no token file, no escaping link) and then re-runs `cache_complete` on both models.
Confirm every shard on the box before deleting anything at home:

```bash
.venv/bin/python tools/runpod/rp.py ssh \
  'find /workspace/hf/hub -name "*.safetensors" -exec sha256sum {} + | sort'
# compare against home, then -- only if all six lines match:
( cd ~/Desktop/linear-ceiling && du -sh box-cache && rm -rf box-cache ) \
  | tee -a ~/.cache/linear-ceiling/freed-bytes.log
```

Six shards: 3B has 2, 8B has 4 (§1). Both models are re-downloadable from the Hub with the ambient
login, which is what makes this deletion reversible. Log the freed bytes — the puller's pre-create
gate was passed on the promise of them.

## 5. Pull, from the moment the driver starts

```bash
nohup .venv/bin/python tools/runpod/pull_verify_b.py --delete-verified \
    --reclaimable ~/Desktop/linear-ceiling/box-cache \
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

**The drain.** The watchdog stops the DRIVER before the ceiling terminates the pod, so the last
checkpoint survives and the puller can finish. It drains at 70% of the sitting ceiling by default, or
earlier if the puller's measurement (outstanding GiB ÷ measured GiB/h, written to
`~/.cache/linear-ceiling/drain-hint.json` each round) says the remaining pull needs more than the
leftover budget. A measurement can only move the drain **earlier**, never later — `outstanding_gib`
cannot see the handoff in flight. `--no-drain` turns it off and costs you that handoff.

> **Go/no-go at handoff 5.** By then the measured per-handoff wall clock is real, and the assumed
> load cost is no longer load-bearing. Read the five timestamps out of `report.json`, then:
>
> ```
> t_remaining = (28 − n) × median(t_handoff)          # n = 5
> t_end       = now + t_remaining + pull_tail         # pull_tail from the drain hint
> ```
>
> **GO** if `t_end` is before the drain at 4.2 h. **DRAIN NOW** if it is not — deliberately, at §7's
> step 1, rather than waiting for the ceiling to do it worse. A drained partial is a registered
> outcome under entry 0042; a hard kill is a salvage. The handoffs run shortest-sender-first, so
> handoff 5 is on the *fast* end and `median(t_handoff)` over the first five **underestimates** the
> rest — treat a marginal projection as a fail.

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

## 7a. Aborts — what to do, literally, when each thing fails

| failure | do this |
|---|---|
| **SSH never comes up** (`wait-ssh` times out, default 12 min) | `rp.py` terminates on its own timeout — confirm with `rp.py status`, then `rp.py spend`. An account with no `PUBLIC_KEY` yields a permanently unreachable pod; check that before re-creating. Nothing was staged, so there is nothing to salvage. |
| **CUDA smoke test fails / < 70 GiB VRAM** | The launcher refuses **before any weights** and exits non-zero; nothing downloaded, no dump written. `rp.py terminate --force` (there is no receipt to interlock on, and nothing to lose). Record the card actually delivered — a refusal here is §3.4's extrapolation being replaced by measurement, and it belongs in the closing brief. |
| **Weight archive or shard sha mismatch** | The launcher refuses at the archive validation or at `cache_complete`. Do **not** re-upload blindly: re-hash `box-cache` at home first and compare against §1's figures, because a mismatch means either the upload truncated or the home copy is wrong, and those need different fixes. **Do not delete `box-cache`** until a check passes. |
| **`SITTING_B_FAILED`** | The puller exits **5** with the status quoted. The run cannot complete, but what is mirrored may still be a closeable prefix: §7's drain-partial path from step 3. Paste the box log verbatim into the closing brief — never summarise a failure. |
| **The drain signal does not land** | The watchdog says so and retries each poll. The ceiling still terminates at `--sitting-max`, and the close then falls back to the last verified snapshot — scenario 3, which the rehearsal covers. |
| **Home network drops mid-run** | The watchdog alerts and **keeps polling** (a home outage is not a runaway pod), with a 45-minute backstop terminate. The puller resumes on its own; nothing on the box is deleted while it cannot verify. |

In every case: **`rp.py status` must end in `(none — nothing is billing)`** before you stop paying attention.

## 8. Prove it is gone

```bash
.venv/bin/python tools/runpod/rp.py status    # must end in "(none — nothing is billing)"
.venv/bin/python tools/runpod/rp.py spend
```

R7 step 6: prove absence from the API, never assume it. `sudo shutdown` on a RunPod container does
**not** stop billing, and "stopped" is not "terminated".

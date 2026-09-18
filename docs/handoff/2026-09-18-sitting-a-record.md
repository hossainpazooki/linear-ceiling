# Sitting A — the complete record, 2026-09-18

The E8 calibration and the k = 1/4/8 mapper fit for `llama3.2-3b-to-llama3.1-8b`, from the pod being
taken over to the pod being proven gone. Written to be read by someone who was not here.

**Status: sitting A is COMPLETE. Artifacts are home and verified. The pod is terminated and proven
gone. No ledger entry has been appended for its figures — that is entry 0040 and it is not written.**

> **Status at pause, 2026-09-18 ~18:50Z.** Nothing is billing (pods [], $0/h, balance $9.81).
> The home re-score **PASSED**: `summarize_e8 --config config/e8f.toml` exited 0 on the pinned stack,
> recomputing every R² by re-running the upstream scorer on the fingerprinted dumps, and it agrees
> with the box to the digit — so §8's figures are **confirmed, no longer preliminary**. At the
> verdict-bearing k = 1: generic K 0.7139 / V 0.4711, agent K 0.7311 / V 0.4599, drop
> K **−0.0172** / V +0.0111, band **K HOLDS / V HOLDS**. (The drop is NEGATIVE: this pair's mapper
> fits agent text *better* than the generic text it was fitted on. The summarizer states plainly that
> the H-E8 verdict is not made here and enters only by a numbered entry.)
> **One must-fix before entry 0040 is previewed, let alone appended:** `docs/drafts/append_0040.py`'s
> τ-ordering passage calls the ordering "registered" and cites "entry 0039's pre-registered
> contingency". **Both are false** — see §8; 0039 registers contingencies for the τ ladder, the
> prefix-invariance tolerance and the τ_K ceiling, and for nothing else. An appended entry is
> immutable, so that sentence must be rewritten to state only what the ledger says before any preview
> is shown. The rewrite was drafted but **not yet applied**; the draft on disk still contains the
> false text. Nothing is on the ledger, so nothing false has been recorded.

---

## 1. What exists now, and where

| artifact | home location | note |
|---|---|---|
| the mapper, k = 1/4/8 | `~/e9-repro/kv-transfer-replication/mappers/llama3.2-3b-to-llama3.1-8b/` | **irreplaceable without another card** |
| generic dumps (source, target) | `~/e9-repro/kv-transfer-replication/data/kv/<pair>/` | what the probe and fit were computed from |
| `r2.json` (archived held-out R²) | `~/e9-repro/kv-transfer-replication/results/mapper/<pair>/` | τ is 1 − these |
| probe outputs (6 × `.npy` + `summary.json`) | `~/e9-repro/kv-transfer-replication/results/probe/<pair>/` | `fit_mapper` reads these |
| generic token draw (n = 50, seed 0) | `~/e9-repro/kv-transfer-replication/data/tokens/` | the dumps are meaningless without it |
| E8 report | `results/e8f/report.json` | the sitting's result |
| agent dumps | `results/e8f/kv/agent/{source,target}` | `summarize_e8` re-fingerprints these |
| agent token file + manifest | `data/e8f/` | same |
| the verified staging copy | `~/.cache/linear-ceiling/sitting-a-pull/pull/` | 150 files, 9.2 GB, incl. `MANIFEST.sha256` |
| both sitting logs | `~/.cache/.../pull/logs/` | `sitting_a.log` and `sitting_a.attempt7.log` |

`results/` and `data/` are gitignored in this repo; `data/`, `mappers/` and most of `results/` are
gitignored upstream. **No artifact enters git history.** The upstream's tracked code is untouched:
`git -C ~/e9-repro/kv-transfer-replication diff` is empty and the E8 gate reads *ready*.

## 2. Verification — how we know the artifacts are sound

Three independent layers, all passed:

1. **On the box, before anything moved.** `sitting_a.sh` wrote `MANIFEST.sha256` over the packaged
   tree, then `sha256sum -c` was run there: **149 of 150 OK**. The single failure is
   `MANIFEST.sha256` hashing *itself* — see §6, it is a packaging bug of ours and is benign.
2. **At home, after the pull.** `tools/runpod/pull_verify_a.py` checked an explicit expected-path list
   (each entry carrying the reason it cannot be skipped) and then re-hashed every manifest entry:
   **149 files verified, every expected path present.** It wrote the verification receipt that
   `rp.py terminate` refuses without.
3. **Continuously, during the run.** A read-only incremental puller recorded a box-side and a
   home-side sha256 for every file as it arrived: **12/12 agreeing at the last check, 0 mismatches**,
   plus an independent manual spot-check of the largest artifact (`k4.safetensors`, 1.07 GB) which
   matched on both sides.

The pod was terminated only after layer 2 passed, and its absence was then confirmed by a direct
GraphQL query rather than by trusting our own tool: `pods: 0`.

## 3. What happened, in order

| time (UTC) | event |
|---|---|
| 15:47 | pod created (A40, secure, $0.49/h + disk ⇒ $0.518/h effective) |
| 16:13 | attempt 7 of `sitting_a.sh` starts: gates pass, `manifest ok: 188 files` |
| 16:14–16:15 | both generic dumps written, `check_max_abs 5.96e-08` on **both** sides |
| 16:15–17:50 | `probe.py` — 95 minutes (see §5, why it was slow) |
| **17:50:51** | **SITTING_A_FAILED fit k=1/4/8** — `fit_mapper.py: error: the following arguments are required: --pair` |
| 17:53:51 | resumed from the fit via `resume_a_fit.sh`, BLAS threads capped at 8 |
| 17:54–18:04 | fit complete: k1, k4, k8 + `r2.json` — **11 minutes**, against a projected ~55 |
| 18:04–18:12 | E8 driver, arms (a) and (b) |
| ~18:12 | **home watchdog died** for ~5 min on a transient SSL error (see §6) |
| 18:13:29 | **SITTING_A_OK**, 150 files / 9.2 GB packaged |
| 18:30 | full pull home; `pull_verify_a.py` passes; receipt written |
| 18:31–18:33 | sitting-B memory probe (§4) |
| **18:34:15** | **pod terminated, PROVEN GONE.** sitting $1.4337, balance $9.8160 |

**Cost: $1.43** against the $3.25 approved for this sitting; campaign cap $10 intact.

## 4. The sitting-B memory probe

Run on the already-paid card *after* sitting A was home and verified, for ≈$0.03. Full record:
`docs/probes/2026-09-18-llama-8b-fp32-prefill-memory.md`.

**Result: the E9 short cell does not fit a 48 GB card.** `Llama-3.1-8B`, fp32, `sdpa_repeat_kv`,
native unscaled RoPE, on a 44.43 GiB A40:

| T | peak GiB | outcome |
|---:|---:|---|
| 16,384 | 37.56 | ok |
| 24,576 | 41.38 | ok |
| **32,768** | **43.2** | **CUDA OUT OF MEMORY** |

32,768 is `config/e9f.toml`'s own registered cap, and this is the *easiest* case — one model, one
forward. The E9 driver holds the receiver and performs three stride-1 dumps per handoff plus the
identity, null and prefix-invariance controls. **Sitting B needs an 80 GB card.** The 3B source is
never the constraint (23.51 GiB at 32,768).

It read `config/e9f.toml` **as committed**: `probe_e9l.py` takes only `pair`, `rope` and
`context_cap` through raw `tomllib` and never calls `load_e9_config`, so the config's UNRESOLVED τ
markers did not apply. **No config was edited and no scratch copy was made.** The probe writes only
to stdout, so it could not touch sitting A's artifacts.

## 5. Why the probe took 95 minutes and the fit took 11

The pod reported `nproc` 96 but the cgroup quota was **7.65 CPUs**, and the process ran 111 threads
with ~50k throttle events. Capping `OMP/OPENBLAS/MKL/NUMEXPR_NUM_THREADS=8` on the resume removed the
thrashing: the fit produced k1 in ~1 minute and k4 in ~2, against a projected ~55 minutes for the
whole fit.

**This changed no registered parameter** — not the rule, τ, band, cap, seeds, k, λ or hold-out. It
changes reduction *threading*, which can move float32 results at the last ULP; that is the class
entry 0028 registered a cross-platform tolerance for, and it is unavoidable between box and home in
any case. It is recorded in the sitting log header and in the resume script's docstring so the
sitting record carries it rather than discovering it later.

## 6. Every defect found, and its disposition

| # | defect | severity | disposition |
|---|---|---|---|
| 1 | `sitting_a.sh` called `fit_mapper.py` without `--pair` | **killed the sitting** after a 95-min probe | fixed in `4e990e5`, in the script and in the two runbook lines; an audit of every upstream-script invocation found no other |
| 2 | `except Exception` cannot catch `SystemExit`, so the watchdog died on a transient SSL error and a pod billed unwatched for ~5 min | **lost the only safety net** | fixed at all three sites; `tests/test_runpod_watchdog.py` **verified to fail against the buggy version**. NOT yet committed — see §7 |
| 3 | `MANIFEST.sha256` is written into the tree it hashes, so it carries a stale self-entry | benign | **not fixed.** Every real artifact verifies and `pull_verify_a.py` skips it by name. `sitting_b.sh` should write the manifest to a temp path and move it in |
| 4 | the incremental puller used `declare -A`; macOS ships bash 3.2 | killed the puller at the first mapper path | fixed (file-based size cache) |
| 5 | the puller did not watch `results/mapper/<pair>/r2.json` | would have missed the file τ derives from | fixed; the file was pulled by hand the moment it was noticed |
| 6 | `probe_e9l.py` hardcodes `Path.home()`; the box has `HOME=/root` with repos in `/workspace` | would have failed to find the config | worked around at invocation with `HOME=/workspace`; **not** by editing the script or symlinking |
| 7 | the on-pod dead man never armed (`runpodctl get pod` failed with pod-scoped credentials) | the home side was the ONLY net | recorded; sitting B must not assume two layers exist |

## 7. What is deliberately NOT committed

`tools/runpod/rp.py` and `tests/test_runpod_watchdog.py` are held in the working tree together:

- `rp.py`'s diff is ~72 insertions, and **most of it is another operator's unreviewed work** (a
  verification-receipt interlock with nonces). Committing it would sweep unreviewed changes into the
  record on the tool that guards a billing pod.
- the test loads `rp.py` from disk, so committing it *without* the fix would break a fresh clone.

They go in together after that review. The same applies to everything else left uncommitted:
`src/linear_ceiling/e9.py`, `tests/test_e9.py`, `tests/test_e9_long.py`, `docs/drafts/append_0041.py`,
`docs/drafts/append_0043.py`, `tools/runpod/sitting_b.sh`, `tools/runpod/pull_verify_b.py`,
`tests/test_runpod_pull_verify_b.py`. `e9.py` is the registered instrument's driver and gets a proper
review, not a glance.

Incidentally the receipt interlock **worked on us**: the first `terminate` was refused because the
receipt had been written to the wrong path. Rather than force past it, `pull_verify_a.py` was re-run
pointed at the path the state records, so the receipt was produced *by the verifier* rather than
hand-written. That is exactly what the interlock is for.

## 8. The open scientific question — τ ordering

**Preliminary, box-side only.** The home re-score had not completed when this was written, and these
numbers appear in no ledger entry, config or commit message.

The box report gives, at k = 1: generic K 0.7139 / V 0.4711, agent K 0.7311 / V 0.4599. So
τ_K ≈ 0.286 (comfortably under the registered 0.45 ceiling, and *better* than Qwen's 0.3186) but
τ_agent_K ≈ 0.269 — **this pair's mapper fits agent text slightly better than generic text, the
opposite of Qwen.**

`config.py` refuses that: it requires `tau_K < tau_agent_K < 1`. The question asked was whether that
ordering is *registered* or *assumed*. It was traced, and the answer is:

> **It is not registered.** Entry 0025 registers τ_agent_K's *derivation* (1 − agent-text K R²,
> recomputed and refused on disagreement), that it "is a K tolerance and is applied to nothing else",
> and that "**the band reads τ_K only**". It nowhere states an ordering. The validator in
> `config.py:290` pre-dates this campaign, and its own error text says "it is the LOOSER agent-text
> tolerance from entry 0020 arm (b)" — i.e. it describes what 0020 *measured for Qwen*.

Enforcement sites, in the order they fire on the path to 0040 and 0041:

| site | behaviour |
|---|---|
| `docs/drafts/append_0040.py:93` | **reports** the non-ordering in the entry text; does not refuse. States "Nothing is edited into a config to make it load." |
| `src/linear_ceiling/config.py:290` | **refuses on load** — blocks both Llama E9 configs |
| `tools/emit_tau.py:61` | refuses |
| `docs/drafts/append_0041.py` | blocked downstream, since it loads the config |
| `summarize_e9` | no ordering check |

So **0040 can be written and will state the anomaly honestly; 0041 is blocked.** One gap: 0040's
prose points to "entry 0039's pre-registered contingency", but 0039 as appended registers
contingencies only for the τ ladder, the prefix-invariance tolerance and the τ_K ceiling — **not for
this ordering.**

**Operator ruling (2026-09-18): register that it was never a requirement.** A numbered entry is to
state the above and relax the check to report-only. Rationale: a quantity that entry 0025 says decides
nothing should not be able to block a cell, and a mapper that transfers to agent text as well as to
generic text is a *finding* about this pair, not a fault. **Not yet implemented** — it needs the
numbered entry, and no entry may be appended while the independent review is running.

## 9. The stack

The home upstream venv was torch 2.14.0 / transformers 5.16.1 / numpy 2.5.3; the box ran torch
2.11.0+cu128 and the runbook pins transformers 5.15.1 / numpy 2.5.2 — a wider divergence than the
numpy point release alone. Since `summarize_e8` re-runs the upstream scorer at home and compares, and
entry 0028's tolerance was measured on the pinned stack, the home venv was rebuilt to
**torch 2.11.0 / transformers 5.15.1 / numpy 2.5.2** (the CPU build; home has no CUDA, which is
itself why 0028's cross-platform tolerance exists) before the re-score.

## 10. What comes next, and who decides

Nothing below has been started; all of it is the operator's to sequence.

1. **The home re-score** (`summarize_e8 --config config/e8f.toml`) must pass before any figure is
   believed. Until then §8's numbers are preliminary.
2. **Entry 0040** — the E8 figures. `append_0040.py --preview` renders it for reading; the append
   needs an explicit go-ahead. It carries an append-only correction of a prose error in 0039 (which
   says "all five tau-derived keys" carry markers; only three do, since the ladder and the prefix
   tolerance were registered absolute).
3. **The τ-ordering entry** (§8) — required before 0041 can exist.
4. **Entry 0041** — the E9 short-cell registration. Still open: whether it registers a run order and
   a stopping rule. It currently has neither, so a budget kill mid-run would yield no verdict at all,
   only a spent card. E9-long registered both in entry 0035.
5. **Sitting B** — needs an 80 GB card (§4), and a balance guard: do not start it without enough to
   finish. Balance is $9.82.
6. **R8 backup** of this sitting's verified home mirror.
7. **The review** of the uncommitted work in §7.

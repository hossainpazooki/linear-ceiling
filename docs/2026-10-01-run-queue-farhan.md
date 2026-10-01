# The ask: MLSys experiments that need a GPU, for a co-author running his own compute

**Date:** 2026-10-01 · **HEAD at write:** `0a51275` (= `origin/main`, 0/0) · **Last entry on the ledger: 0044** ·
gates green (`ledger_check`, `lint_scope`, `seal verify`).

**Update, 2026-10-01:** the original queue below describes a broader MLSys proposal. The focused
cache-injection follow-up is Task C's fresh/reuse comparison with correctness controls, with Task B
optional on the same GPU. This update corrects those designs; it does not register them, adopt
quality thresholds, schedule the other campaigns, or authorize renting a box. The revised E-BEH
and E-TAIL drafts retain the pending registration and distinguish prediction sensitivity from
coding-task quality.

**Completed fork follow-up:** the separate `exp/cache-behavior` change measured all 35
long handoffs on an H100, including fixed-text predictions and the last 32 receiver
queries' fresh attention. Its runbook records the descriptive scope. This does not
register the queue below or supply its unrun truncation and repair-budget results.

**Dates.** Internal review **week of Oct 12** · draft to a PI by **Oct 15** · **MLSys 2027 deadline Oct 30 2026,
12:00 PDT**. The NeurIPS/LCFM workshop paper is already accepted (non-archival), so nothing here is needed for that;
this is the MLSys push plus the camera-ready text.

**What I am asking for, in one sentence.** Four reviewer weaknesses need experiments; three of them need a GPU and
one is already done. **E-TRUNC is the one I want run** — it is the highest-value row, needs no upstream change, and
fits a 48 GB card in about three hours. Everything else below is either context so you don't redo finished work, or
a clearly-marked second and third choice.

**Two hard limits on what you can do without me.** (1) **Ledger appends are the operator's** — you draft an entry,
never append one, and entry *numbers* are allocated only by `docs/drafts/README.md`. (2) **An experiment is
registered before it is run**: the entry, with its thresholds, lands *before* any prefill (R1). So every GPU row
below is blocked on a ruling from me, and §10 is the list of rulings, each with my recommended default, answerable
in one reply.

---

## 0. The ask as a table

| # | task | needs from me first | code that must land first | min card | time | deliverable |
|---|---|---|---|---|---|---|
| **A** | **E-TRUNC** — isolate length by head-truncating the same senders (W2) | rulings 1, 2, 3 + registration | `sender_head_truncate` config key; paired reader | **48 GB** | ≈3 h | tail/paired figures + a drafted entry |
| **B** | Optional E-TAIL **Part B** — fresh-attention-weighted error (W3) | descriptive scope, query selection, checks + registration | chunked reductions **+ their own probe** | reuse C's **80 GB** allocation; smaller card only after probe | measure in probe | per-query w and matched mass + drafted entry |
| **C** | E-BEH — prediction sensitivity to practical reuse (W1) | ruling 6 + registration of core arms and controls | cache injection; pinned continuation extractor | **80 GB recommended**; 40 GB marginal | measure in probe | per-token KL/top-1, controls + drafted entry |
| **D** | *Optional:* a third pair, Llama-3.2-1B → 3B | ruling 9 (just the go/no-go) | nothing — one CPU preflight | **none** | seconds | preflight output, pass or fail |
| **E** | Llama **LONG** cell, 0046/0047 (W7) | ruling 10 + the numbering ruling 11 | nothing; drafts are staged | **80 GB** | ≈2 h | run the staged drafts' cell |

Nothing in this document allocates a number, registers anything, or edits a design.

---

## 1. Already done — do not redo any of this

- **E-TAIL Part A is finished** (committed `0a51275`, `src/linear_ceiling/e9_tail.py` + tests). It ran on all three
  Qwen cells and reproduced every figure the outline carried as PENDING — 16 of 16 comparisons. Outputs are
  `results/{e9,e9l,e9s}/tail.json` (gitignored). Verified from those files directly, not from a report:

  | cell | tokens over τ_K | pooled mean δ_K | per-handoff mean δ_K, median | \|R\| median (p10, p90) |
  |---|---|---|---|---|
  | e9 (0029), 25 handoffs | 9,047 / 155,257 = **5.83 %** | 0.0810 | 0.0682 | 6,551 (4,148, 9,165) |
  | e9s (0038), 25 | 10,336 / 155,257 = **6.66 %** | 0.0986 | 0.0895 | same handoffs as e9 |
  | e9l (0036), 35 | 30,701 / 387,508 = **7.92 %** | 0.1165 | 0.1106 | 11,462 (7,085, 19,853) |

- **The short Llama cohort has already run:** entry **0044, H-E9F HELD, 28 scored of 28**, on an A100-SXM4-80GB.
- **R8 holds for the Llama family:** both mirrors are public under the pair owner's account and verified against
  every sha pin 0040–0044. The e9f mirror is complete on this machine (1,054 files = the Hub's 1,054).
- **The upstream pin is merged and reachable.** PR #1 merged 2026-10-01T03:44:25Z without squash or rebase, so
  commit **P = `06f8d55`** is an ancestor of upstream `main`; the local clone is on `main` at `0d27c68` and
  **contains P** (`merge-base --is-ancestor` → 0). The "commit P is not merged" blocker in `docs/drafts/README.md`
  is retired.
- **Text-only reviewer fixes** (W6, W7, W8 sentences and W4's abstract clause) are grounded on the ledger and are
  being handled on the paper side — not yours.

### One new fact from Part A that changes how the paper reads, and how A must be registered

**Pooled seam-bin means run far above the medians the ledger reports.** On the long cell, same-K, verified from
`results/e9l/tail.json`:

| seam bin | n tokens | **mean** | median |
|---|---:|---:|---:|
| 0 | 4,050 | **0.4285** | 0.2603 |
| 16+ (far from seam) | 359,203 | **0.1105** | 0.0629 |

That is reviewer teFN's Corollary 3 objection made concrete: a restatement on means prints numbers ~1.7× the
medians the paper printed. **It also matters for task A**, because E-TRUNC's registered reading is written against
the far-from-seam figures, and those figures depend on which statistic you pick. I recomputed 0038's configuration
share both ways from the tail files:

- on **medians**: native 0.019497 → scaled 0.038085 → long 0.062873, share **0.4285** — reproducing entry 0038 exactly;
- on **means**: native 0.070807 → scaled 0.088973 → long 0.110493, share **0.4577**.

Good news: the share is robust to the statistic (0.43 vs 0.46). But the *levels* nearly double, so a margin stated
as a bare number is ambiguous — ±0.005 is 13 % of the median 0.0381 and only 5.6 % of the mean 0.0890. **Ruling 1
therefore names its statistic.**

---

## 2. Task A — E-TRUNC (the main ask)

**Question.** The short↔long gap is confounded: different handoffs *and* different configuration. Entry 0038 split
off the configuration part (share 0.4285); the residual is unattributed because the cohorts are different handoffs.
E-TRUNC varies length **within** a handoff and attributes the residual.

**Why head truncation.** Under causal attention a matched token's K/V depends only on `S[:p_S(t)]`, so *tail*
truncation changes nothing. The treatment is **head** truncation: `S'_L = S[−L:]`, which shortens every matched
token's causal prefix and lowers its sender position.

**Cells.** FULL (= E9L re-run under this entry's pin, the control) · L65 · L49 · L32, all with R unchanged and the
YaRN receiver; plus optionally **L32-native** (ruling 3), the only cell where native vs YaRN is comparable on the
same tokens.

**What the entry must seal, before any prefill:**
- the four levels and that **R is unchanged within a row** (the YaRN cells share one receiver prefill per handoff);
- the **common matched subset** rule: compare δ only on `M_∩`, the tokens matched under *every* level, and report
  `|M_∩| / |M_FULL|` per handoff **before** any verdict is read, with a shrinkage gate (ruling 2) below which a
  handoff is **void** for the comparison — this is the design's own weak point, so it is gated, not hoped;
- the statistics: mean δ_K, p(τ_K), f*(τ_K), f*(0.03), the 16+ seam bin **naming mean or median** (ruling 1), and
  the sender-position profile re-binned on `p_S'`; bootstrap seed/reps as 0025's unless re-registered;
- the pre-registered reading: near the scaled-short far-from-seam figure ⇒ **length**; near FULL's ⇒ **the
  handoffs**; between ⇒ **unattributed, say so**;
- the run order (longest |S| first, so the only handoffs L65 changes are scored first), checkpoint per
  (handoff, level), and the partial-close shape;
- that it is **descriptive** and moves no hypothesis cell.

**Code first.** `config.py` must accept `sender_head_truncate = L` — it does not exist today. Then per-level configs
and a new fail-closed reader for the intersection and the paired comparison, with its inputs sha-pinned. **No
upstream change, no injection.**

**Card and time.** FULL peaks **31.56 GiB** at |S| = 80,111, so **48 GB**. A 20 GB card runs only L32 and
L32-native. ≈3 h realistic, 4–5 h upper bound.

**One correction to the design doc, found by recomputing.** `e-trunc-design.md` §8 says L49 differs for "the 18 over
49,152". It is **19** — one handoff sits at |S| = **49,196**, and 18 is the count above the `s_len` bin edge
**49,999**. Hours unaffected; fix it before the entry is written, since the entry states it as a fact about its own
cells.

---

## 3. Task B — E-TAIL Part B (optional mechanism analysis)

**Quantity.** `w_i(l,h) = Σ_{j∈M, j≤i} a_ij(l,h) · δ_K(j,l,g(h))` with `a` the **fresh** receiver's attention
weights and `g(h)` mapping query head h to its GQA KV head. Report w, matched attention mass m, and w/m when m>0
(undefined otherwise). Also report attention mass on the Part A tail set defined by token-average δ_K>τ_K,
always beside µ and δ_max. A small w can reflect little attention to M; mass makes that distinction visible.

**What the entry must seal:** the fresh-attention choice, exact query positions/sampling, GQA mapping, causal
mask, numerical checks, and backend. Preserve SDPA where possible and reconstruct selected-query attention in
chunks; if eager replaces it, bridge states/logits within declared tolerances. Fresh attention is one endpoint,
whereas Proposition 4 uses attention along an interpolation path and additional norm/variance assumptions.
These summaries do not establish that bound, validate τ_K under YaRN, or prove unchanged generation quality.

**Code first.** Reduce selected-query attention against δ without materializing full all-position matrices;
at |R|=19,853 with 16 query heads one FP32 matrix is about 25 GB per layer. Check GQA mapping and chunked
reductions against a small explicit causal-attention reference, then probe the actual largest case.
The existing prefill probe does not establish this new path's memory requirement.

**Card and time.** The earlier 20 GB / sub-hour figures were unmeasured estimates for this path. Prefer C's
existing A100/H100 80 GB allocation if available; choose a smaller card only after a memory/time probe.
Retain per-query reductions and masses, not only cohort means. Do not rerun prefills for the completed CPU Part A.

---

## 4. Task C — E-BEH (focused fresh-versus-reuse follow-up)

**Question.** How much does reading an assembled cache with reused same-model KV change next-token
predictions on the recorded continuation, relative to fresh prefill?

**Core:** FRESH and REUSE-ALL, with fresh-repeat, no-reuse/full-fresh, exact-prefix, and rotary-relocation
checks. A random perturbation can test error direction beyond matched magnitude; it is not needed to interpret
fresh-vs-reuse KL. Oracle-ranked recomputation at 10%/20% or the tau-ladder counts is optional, still requires
fresh-reference information for selection, and must not be named CacheBlend.

**What the entry must seal:** exact archived M, arms, controls/tolerances, backend/precision/version pins,
continuation extraction and cap, missing/short-continuation coverage, and scoring alignment. Build the entire
receiver cache, preserving all M; feed C[0] as conditioning and score C[1:]. The first continuation token is
unscored. The text came from a proprietary model, so this measures **prediction sensitivity on fixed text**,
not Qwen coding-task quality. Ruling 6 proposes descriptive reporting without a fabricated quality gate.

**Code first.** Port the block-wise cache construction and pinned continuation extraction into this repository;
the upstream `kv-transfer-replication` clone remains read-only. Source/destination must use the same fixed YaRN
schedule and amplitude for a pure `(p_R-p_S)` rotation with scaled `inv_freq`; do not apply the amplitude twice.
Reject unsupported configuration differences. The separate implementation/runbook pins the executable path.
Fresh repeats can be exact, but chunk/backend/version bridges use declared finite-precision tolerances and
report errors. A failed control stops expansion; it does not justify weakening the tolerance after the run.

**Card and time.** Prefer **one A100 80 GB or H100 80 GB**. The measured 31.56 GiB S prefill does not bound
simultaneous source/fresh/assembled caches. A **40 GB slice is marginal**; 48 GB or 40 GB requires a successful
largest-case probe of the actual port. Synchronize CUDA around timings. Measure the core workload before
estimating duration; the old three-hour estimate was not an upper bound. Reuse verified baselines and preserve
new per-example records. Deleted pilot outputs cannot be recovered by labeling a fresh run a reproduction.

---

## 5. Task D — *optional*: a third pair, Llama-3.2-1B → 3B

This is the one item I'd call genuinely optional, and it is cheap enough to settle this week for nothing.

Your "1B→3B" doesn't match the repo, and the correction cuts both ways. **The registered second family is
3.2-3B → 3.1-8B**, and its short cohort has already run — 0044, H-E9F HELD 28/28, on an A100 80GB. So "worth running
a short Llama cell first on smaller hardware" is answered twice: it ran, and it couldn't have run smaller — a
measured probe puts Llama-3.1-8B fp32 at **OOM at T = 32,768 on a 44.43 GiB A40**, and 32,768 is that cell's own
registered cap. **No Llama cell on this pair fits 48 GB**; it's the 8B *receiver*, not the 3B source
(23.51 GiB at 32,768).

But if you really meant a **new** 1B→3B pair, it has a genuine advantage: the receiver would be the 3B, which
measured 23.51 GiB at 32,768, so it **would** fit 48 GB. The likely blocker is `check_matched_kv`, which requires
per-head dim equality and is called unconditionally on every dump — the 3B side is 128 and the 1B side is plausibly
64. **I could not verify that today:** `meta-llama/Llama-3.2-1B` is gated (401 on its raw `config.json`) and there's
no local snapshot, so **don't take my 64 as fact**. `tools/preflight_pair.py` settles it in a second, CPU-only and
free — that's ruling 9's default.

If it passes, it is still a **new pair**: its own E8 fit, its own τ, and a pair/family registration entry before any
E9 cell — a new campaign, not an add-on. Worth it only if a cheap card matters more than the four weeks left.

---

## 6. Task E — the Llama LONG cell (W7), if a 80 GB card is already in hand

The drafts are **staged and unrun**: `append_0046.py` (registration) and `append_0047.py` (figures; renumbered 2026-10-01), with
`config/e9fl.toml` committed. **Their numbers are provisional and may move — see ruling 11.**

- Cap **81,920**, floor **32,768** in Llama-3 tokens. The floor equals the short cell's cap, so the two Llama cells
  **partition** their handoffs, and 0046 asserts that the ids it excludes under the floor are *exactly* the short
  cell's included set, with the residual above the cap named and counted. Audited, not asserted.
- **Neither side is scaled** (both natively 131,072): no `[e9.rope]`, no `[e9.bridge]`, no `--rope-scaling`. 0035's
  configuration-bridge reading is declared **inapplicable**; two dump-derived controls replace it — a native-window
  assertion and a **role-scoped** RoPE identity (the sides carry different llama3 factors, 32.0 and 8.0, so an
  unscoped assertion would refuse every correct run).
- It **cannot move, support or refute H-E9L** and is **never pooled** with 0036's 35. 0047 reads
  `results/e9l/summary.json` only to state 0036's figures *beside* these, with non-comparability spelled out.
- **Card: 80 GB.** Not a 48 GB job, per §5.
- **What R8 must hold before the entry:** every kept dump and record of `results/e9fl/` pushed; the push **two-way
  verified** (every local file on the Hub *and* every Hub file local; LFS by `lfs.sha256`, non-LFS downloaded and
  hashed) with **exit 0**; and the existing e8f/e9f mirrors still verified, so 0040–0044 stay recomputable. Prefer
  the pair owner's account, which already holds both verified datasets.

My recommendation is **not** to schedule this before Oct 30 (ruling 10): W7's camera-ready sentence is already
grounded on 0034 today.

---

## 7. How to run any of it

**Host-agnostic.** `tools/ec2/box.sh` is AWS-only; nothing else is. Box-side: `setup.sh`, `probe_e9l.py`, `run.sh`,
`release_sweep.sh`. Home-side: `pull.py`, `verify_mirror.py`. If you are on a **rented container**, read
`tools/runpod/rp.py`'s header first — four rules change and each is a way to lose money or evidence:
`sudo shutdown -h` **does not stop billing**; **stop is not terminate**; **container disk is ephemeral**, which makes
R5 (pull → verify → delete) load-bearing rather than tidy; and there is no instance metadata, so R7's read-back
comes from the API.

**Environment for the existing E9 drivers.** Two clones, two venvs: upstream `kv-transfer-replication` **detached at the cell's pin** (for every
Llama cell, `06f8d55`) with torch cu128, and `linear-ceiling` CPU-only. `setup.sh` builds both idempotently, places
the mapper by sha, checks the traces tarball against its manifest, runs `e9 --check` and `--align-only`, and arms a
24 h self-halt.

The new E-BEH/attention port has its own pinned environment and runbook. Do not mix Transformers 4.57 pilot
caches with a 5.x scoring path without an explicit numerical bridge, or assume the commands below already
implement Tasks B/C. No new environment is required merely to re-read completed CPU summaries.

```bash
# HOME, BEFORE the box exists. The gate does NOT check this and the summarizer refuses later without it.
.venv/bin/python -m linear_ceiling.summarize_e9 --calibrate-tau --config config/<exp>.toml

# BOX, R2 probe — before the run, never after. Give it the RUN's longest prefill, not the config's
# context_cap (which is a BOUND, not the run's number): take MAX_S from results/<exp>/align/coverage.json.
EXP=<exp> MAX_S=<max n_sender/n_receiver> ~/kv-transfer-replication/.venv/bin/python ~/probe_e9l.py > ~/probe.log 2>&1
EXP=<exp> LADDER=32768,49152,65536,80111 ~/kv-transfer-replication/.venv/bin/python ~/probe_e9l.py   # task A: all levels, one ladder

# BOX, R4 — detached, log rotated, python -u, exit code to ~/<exp>.rc
EXP=<exp> bash ~/run.sh            # or: bash ~/run.sh --resume

# HOME, R5/R6 — mirror, verify against report.json, delete on the box per handoff
BOX=<user>@<ip> .venv/bin/python tools/ec2/pull.py <exp>
.venv/bin/python tools/ec2/verify_mirror.py <exp>

# BOX, R7 steps 0-5, then terminate and read the state back
EXP=<exp> LAUNCH_UTC="<box launch, UTC>" bash ~/release_sweep.sh > ~/release.log 2>&1
```

**The reader that must produce every figure** — nothing else may be the source (R11), and no number is typed into an
entry script:

| task | reader | one-command verify |
|---|---|---|
| A — E-TRUNC | a **new** paired reader (intersection + paired levels), fail-closed, inputs sha-pinned | `e9 --check --config config/<level>.toml`, then the reader → exit 0 |
| B — E-TAIL B | `e9_tail`'s surface extended, or a sibling; the eager-vs-SDPA identity check is part of it | reader exit 0 **and** identity within the entry's stated tolerance |
| C — E-BEH | a new reader over per-position KL/argmax, input hashes, and control records | reader exit 0; declared controls within fixed tolerances; exact scored subset named |
| E — Llama LONG | `summarize_e9 --config config/e9fl.toml`, in-process inside `append_0047.py` | `.venv/bin/python -m linear_ceiling.summarize_e9 --config config/e9fl.toml` |
| any R8 mirror | — | `.venv/bin/python tools/hf_verify_backup.py <repo_id> <local_root>` → **exit 0 only when every file matches both directions** (`HF_TOKEN` in the env only) |
| the repo | — | `ledger_check && lint_scope && seal verify` |

### Traps that have actually cost us time

1. **`release_sweep.sh:7`'s `OURS_FILES` is a fixed allowlist** of the e9l/e9s filenames. Any new file your sitting
   puts in `~` — a new probe, a per-level driver, extra configs — is reported `NOT OURS` and the sweep returns
   `foreign=1` **on a clean box**. Extend it in the same change that adds the file.
2. **Never hardlink a results tree into a staging dir and then run a reader.** We did, and it bit today: the
   summarizer rewrote `results/{e9l,e9s}/summary.json` *through* the hardlink (same inode in both paths), so both R8
   staging trees now differ from their published datasets and `hf_verify_backup.py` would fail on that one file. No
   figure moved — I diffed the Hub bytes against the live files field by field: **zero values changed**, one key
   added (`dump_rope`). Copy into a stage, don't link; or delete the stage once the push is verified.
3. **One clone, one cell at a time.** The config loader resolves the upstream path with no override and the gate runs
   inside it, so a git worktree does not give you a second concurrent cell. Detach, run, return to `main`.
4. **Box scripts must be LF.** A Windows clone with `core.autocrlf` hands you CRLF copies that fail on the box.
5. **Percentiles:** quantiles come from `e7_stats` — **lower nearest-rank, no interpolation**. A `numpy` recompute of
   a registered p10/p90 disagrees and looks like drift when nothing drifted (|R| p90 is 19,853 nearest-rank vs
   18,998 interpolated). Use `e7_stats`, or cite the summarizer's field.
6. **The Windows suite is red** on 28 + 26 cases (`os.fsync` on a read-only handle at `e9.py:415`, plus tests that
   exec bash); Linux CI is green. Run the suite on Linux/WSL and treat Windows reds as known.

---

## 8. Return path

1. **Code and docs: a PR against `main`.** One concern per commit, explicit paths, gates passing in the PR
   (`ledger_check`, `lint_scope`, `seal verify`, suite on Linux). Do **not** touch `docs/paper/tex/` (another
   session's) or `docs/drafts/README.md` — it is the number allocator; propose changes in the PR body.
2. **Results: Hub dataset + two-way verify.** Push `results/<exp>/` plus the mapper files the entry pins, run
   `tools/hf_verify_backup.py`, and **paste its exit-0 line into the PR**. R8 is transport, not evidence: the
   verified home mirror is the evidence and the entry quotes the reader, never the dataset. Public is fine (operator
   ruling 2026-09-11). Token **in the environment only** — never in a file, a log or a commit — and revoked when the
   push is done.
3. **Entries: drafted, never appended.** Stage `docs/drafts/append_00NN.py` in the PR. The script runs the reader
   in-process, refuses out of order, and runs `ledger_check` after appending. Treat your number as **provisional**
   and write every cross-reference as a **literal**, not an offset from your own `NUM` — inserting an entry inside a
   block is exactly what offsets get wrong.
4. **No dataset or account names in paper material.** Hub dataset names and the account name are an open
   de-anonymization question; `lcfm_anon` is the double-blind copy. Cite entries and figures.

---

## 9. Priority, and what the Oct 12 draft says for anything unrun

**Order:** task **A** (E-TRUNC) → task **B** → task **D** if you want it (it costs seconds) → task **C** and task
**E** as post-deadline. A is the only GPU row plausibly *entered* by Oct 30.

That was the original broader scheduling proposal. For the focused cache-injection follow-up described in
the dated update above, prepare **C's core comparison first**, with B optional on the same allocation.
This does not schedule A, D, E, or the optional repair campaign.

**What the draft says for an unrun row** — the rule, not a case-by-case call: **name it as designed and unrun, cite
the design document, and state what it would decide.** Never pending-but-expected, and never let a reader infer a
result. For example: "E-TRUNC (designed, unregistered, unrun) isolates length within a handoff by head-truncating
the same senders; it would attribute the residual short↔long gap to length or to the handoffs." A designed-unrun row
is **not** `[BASELINE]`. If a row is dropped for time, say so in a clause rather than omitting it silently.

**"No downstream task-quality number is claimed" remains true after teacher-forced E-BEH.** A completed
E-BEH entry can add prediction-divergence results; coding-task quality requires a separate task outcome.

---

## 10. Rulings — answer these and task A can start

Recommended default in **bold**. None is implemented.

1. **E-TRUNC margin, and its statistic.** → **Default: ±0.005 absolute on the far-from-seam (16+) same-K
   *median*, as entry 0038 reports it** (0.0381 scaled-short, 0.0629 long); "unattributed" between the band and
   FULL's level. Reason: 0037 registered "near / in between" with no threshold, which is why 0038's share came out
   unclassifiable — and per §1 the mean and median levels differ by ~1.7×, so the statistic must be named.
2. **E-TRUNC shrinkage gate** — minimum `|M_∩| / |M_FULL|` below which a handoff is void. →
   **Default: 0.80, reported per handoff before any verdict is read.**
3. **E-TRUNC L32-native** — include it, and is R re-prefilled natively? → **Default: include it, keep R under YaRN,
   and state so** — it is the only same-token native-vs-YaRN comparison, and holding R fixed changes one thing.
4. **E-TAIL Part A's carrier entry** — now that Part A is run, does its table ride the owed corrective f* entry? →
   **Default: yes, one entry — the corrective one, widened** to carry the tail counts, the per-handoff maximum, the
   seam-bin **means**, and the |R| row. They are all re-reads of the same verified records.
5. **E-TAIL Part B** — **Default: descriptive**, reported beside µ, δ_max, and matched attention mass.
   Fresh weights do not establish Proposition 4's pathwise assumptions or a quality threshold.
6. **E-BEH scope and readout** — **Default: descriptive FRESH/REUSE-ALL with correctness controls**.
   The earlier 0.95/0.90 band proposal is withdrawn; those numbers have no established task-quality meaning.
   Fix the continuation cap/coverage rule, numerical controls, and stopping rule before registration. No new
   hypothesis row or verdict vocabulary is proposed by this update.
7. **W5 entry count** — one entry for the bin means or two? → **Default: one**, folded into ruling 4's entry.
8. **The Qwen3 short cell (the 25 of 0029)** — may it appear in MLSys tables? → **Default: no pooled row; a separate
   table only, labelled a separate cell**, until Condition 1's admission outcome is recorded in a numbered entry.
9. **Task D, the 1B→3B pair** — pursue? → **Default: run `tools/preflight_pair.py` this week (free, CPU, no card)
   and decide on its output.** Don't plan a campaign before it passes matched-KV; if it fails, the question closes
   for nothing.
10. **Llama LONG cell** — request an 80 GB card before Oct 30? → **Default: no.** W7's camera-ready sentence is
    grounded on 0034 today; spend the weeks on task A and the tail table.
11. **Numbering collision — this one blocks two files.** A corrective-entry draft is proposed to take **0045**,
    which would push the staged Llama drafts to **0046 and 0047**. That is not two renames: it moves every
    `NUM`/`PREV` literal in both scripts **and** `config/e9fl.toml`'s `[e9.gate] required_entries`, which currently
    lists `"0045"` — and that commit must land **before** any `e9 --check`, which verifies the config is committed
    unmodified. → **Default: let the corrective entry take 0045 and renumber the Llama drafts in one commit**, per
    the drafts README's own contingency, since the corrective entry can run today and the Llama long cell cannot.
    **Ruled 2026-10-01: default taken.** 0045 is the corrective entry; the Llama drafts are now `append_0046.py` /
    `append_0047.py`, and `config/e9fl.toml`'s gate ends at 0046 (one commit, before any `e9 --check`).

**Not mine to decide, and not in this document:** the de-anonymization ruling, the Lean restatement, the
camera-ready date, and the task-slot owners still marked `???` in `docs/2026-09-30-team-status-wednesday.md`.

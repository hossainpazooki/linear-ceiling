# Run queue for the MLSys experiments — for a co-author with his own GPU compute

**Date:** 2026-10-01 · **HEAD at write:** `0265290` (= `origin/main`, 0 ahead / 0 behind) · **Last entry: 0044** ·
**Next free number: 0047** (`docs/drafts/README.md` is the only allocator) · gates green
(`ledger_check`, `lint_scope`, `seal verify`).

**Who this is for.** A co-author who will run outstanding experiments on his own hardware and push findings back.
It is **not** the operator's copy: every ledger append, every number allocation and every threshold stays with the
operator, and this document allocates nothing and registers nothing. It is a re-cut of
`docs/2026-10-01-mlsys-box-plan.md` (written for a rented AWS L40S) for a host that may not be AWS at all.

**Dates.** Internal review week of **Oct 12** · draft to a PI by **Oct 15** · MLSys 2027 deadline
**Oct 30 2026 12:00 PDT**. The NeurIPS/LCFM workshop version is **accepted** (non-archival, camera-ready date not
announced), so nothing below is needed for that acceptance — this queue is for MLSys plus the camera-ready text.

Everything here cites its source rather than re-deriving it: `docs/2026-10-01-mlsys-box-plan.md` (cards, prices,
probes, release), `docs/2026-09-30-team-status-wednesday.md` (the W1–W8 map and owners),
`docs/2026-09-30-review-response-map.md` (per-weakness ledger anchors, T1/T2 split),
`docs/drafts/e-{beh,trunc,tail}-design.md` (the three designs) and `docs/drafts/README.md` with the staged
`append_0045.py` / `append_0046.py`.

---

## 0. Two blockers cleared today, after the box plan was written

Both were open in every document above. Neither has been acted on, and each needs one action from the operator
before anyone relies on it.

1. **The upstream pin is merged and survived.** `hossainpazooki/kv-transfer-replication` PR #1 ("register the
   matched-KV Llama pair") was **merged 2026-10-01T03:44:25Z**, and the no-squash/no-rebase request was honored:
   `compare/06f8d55...main` returns **ahead 7, behind 0**, so commit **P = `06f8d55`** is an ancestor of upstream
   `main` and remains valid as the pin in `config/e9f.toml`, `config/e9fl.toml` and `config/e8f.toml`.
   This retires "0045/0046 cannot run: commit P is not merged" (`docs/drafts/README.md`) and unblocks the R12
   recompute of 0040/0044. **Action:** the local clone `../kv-transfer-replication` still sits at `9ca6258` and does
   not contain P; someone must fetch and detach it at `06f8d55`. I did not — that clone is read-only to me.
2. **The e9f mirror is complete on this machine.** `C:\m\e9f` holds **1,054 files, 52 GiB**, matching the Hub
   dataset's **1,054** files exactly. The e8f mirror was already `BACKUP VERIFIED`. So "0040–0044 is not
   recomputable from a clean checkout" (`review-response-map.md:46`) is now false in substance.
   **Caveat, stated rather than glossed:** 1,054 = 1,054 is a *file-count* match. The hash verification needs a read
   token and has not been run for e9f — see the one-command verify in §4.

Note for the status doc: its task slot "R8 push of `results/e8f`, `results/e9f` to the two empty Hub datasets" is
**superseded** — the push landed under the pair owner's own account, and the two empty datasets under the operator's
account are to be deleted.

---

## 1. Runnable now, with no ruling pending

Your belief was "text-only items and E-TAIL Part A on CPU". **Confirmed with two corrections**, one narrowing and
one widening.

**Genuinely runnable now, nothing pending:**

| item | why it is free of rulings | where the words come from |
|---|---|---|
| **W8** sentence (what HOLDS could have failed against: null pairing, cross arm, τ = 0.03) | every figure is already on the ledger | `0029:1772,1783,1797`; `0036:2191,2201,2216,2218` |
| **W7** sentence (the cross arm is a reference instrument, not a ceiling on cross-model reuse) | grounded on the n = 420 refit already registered | `0034:2043` |
| **W6** rewording (drop "predicts"; the bridge control is the evidence) | the bridge's own f* and δ are registered | `0036:2191-2192` |
| **W4** *abstract clause* (the 35K–80K band is **sender** length; receivers are ~11.5 K; 73 % of tokens sit inside 32 K) | the 73.3 % is arithmetic on a registered count and may print as such | `0036:2206` |
| **N2** drop the E-RL appendix | the design itself says "not registered"; the decision is editorial | `docs/2026-09-02-e-rl-design.md` |
| **R12 recompute** of 0040/0044 from the mirror | a *recompute*, not a new finding — it produces no new number | §0 above; §4 |
| **A 1B→3B pair preflight** (CPU, free, no card) | a go/no-go check is not a registration | §3 |

**Correction 1 — narrowing. The W4/W5 *rows* are not text; they are blocked on an entry.** The abstract *clause*
is free, but W4's |R| row, W4's native-window mean/median δ, W5's pooled bin means and any W3 tail table are **new
figures**, and no figure reaches the paper except through a numbered entry produced by a fail-closed reader
(R11). `review-response-map.md:62-64` lists them as "blocked on an entry" for exactly this reason. Separately,
Cor. 3 / Remark 1 / Prop. 4 / Remark 2 wording, the appendix lettering, the Lean diff and the template footer are
**blocked on the submitted tree, which is not on this machine** (`:65-66`). Also: the map refers to a
`make_figures.py` emitting macros — **that file does not exist in this repo**, so the macro path lives wherever the
manuscript tree does, not here.

**Correction 2 — widening, and the one thing to coordinate before you touch it.** E-TAIL **Part A** needs no GPU and
no ruling *to compute*: the 35 per-token records are on the home mirror (`results/e9l/tokens/*.tokens.npz`). But its
fail-closed reader **is being written right now by another session** — `src/linear_ceiling/e9_tail.py` (208 lines)
and `tests/test_e9_tail.py` (85 lines) are present and **uncommitted** in the working tree, and `summarize_e9` has
no `--tail` flag, so the reader is the standalone module `python -m linear_ceiling.e9_tail --config …`. It already
follows the right discipline (it runs `summarize_e9.summarize` first, then re-reads the sha-pinned squares). **Do
not start a second implementation and do not edit those two files**; take them when they land. I did not run them.

So: Part A's **numbers** are computable today; Part A's **entry** still waits on ruling 4 below (which entry carries
the table).

---

## 2. The four GPU rows

Common to all four: **registered before requested** — the entry is appended *before* any prefill (R1), thresholds
fixed in it, and the run obeys R1–R12 of `docs/gpu-experiment-protocol.md` (unchanged since 09-14). Every figure
comes from a fail-closed reader in-process; no number is typed into an entry script.

**Minimum card, all four, in one line:** the Qwen3 pair's long cell peaks **31.56 GiB** at |S| = 80,111
(`09-10 runbook:127`) and **16.70 GiB** at 32,768 with weights 6.41 GiB (`09-13 runbook:96`). So: **48 GB is the
honest floor for E-TRUNC and E-BEH; 20 GB suffices for E-TAIL Part B.** The Llama pair is a different story — §3.

### 2a. E-TRUNC — length isolation (W2). *Recommended first.*

| | |
|---|---|
| **Waits on you** | the §5 **margin** (how close L32 must come to 0.0381 to read as "length"); the **L32-native** scope ruling; registration |
| **The entry must seal** | the four levels (FULL / L65 / L49 / L32) and that R is unchanged within a row; the **common matched subset M_∩** rule and the shrinkage gate (a handoff whose M_∩ is below a stated fraction of M_FULL is **void** for the comparison); the statistics (mean δ_K, p(τ_K), f*(τ_K), f*(0.03), 16+ seam bin, p_S'-rebinned profile); bootstrap seed/reps; the stopping rule and partial-close shape; that it is **descriptive** and moves no cell |
| **Code first** | `config.py` must accept `sender_head_truncate = L` (does not exist); per-level configs; the common-subset intersection and paired comparison in a new fail-closed reader. No upstream change, no injection |
| **Min card** | **48 GB** (FULL peaks 31.56 GiB). A 20 GB card runs only L32 / L32-native |
| **Time** | ≤ 3 h realistic, 4–5 h upper bound |
| **Correction to the design** | §8 says L49 differs for "the 18 over 49,152". It is **19** — recomputed from `results/e9l/align/coverage.json`; one handoff sits at \|S\| = **49,196**, and 18 is the count above the `s_len` bin edge **49,999**. Fix before registration; hours unaffected |

### 2b. E-TAIL Part B — attention-weighted deviation (W3). *Cheapest.*

| | |
|---|---|
| **Waits on you** | registration; the **Proposition 4 attribution quoted verbatim** (the design says the statement is not readable on this machine, so the entry must carry it before the quantity is tied to it); whether a band is registered or it stays descriptive |
| **The entry must seal** | that `a_ij` is the **fresh** receiver's attention (the reused cache's attention is a different, post-hoc quantity); the attention **backend pin** and the admission that δ comes from SDPA dumps while `a` comes from eager; the **identity tolerance** at which eager K/V must match the archived dumps or the run refuses; that w is reported *beside* µ and δ_max, never instead |
| **Code first** | a chunked eager-attention hook (query chunks of 2,048, reduce against δ on the fly, **never** materialize `[heads, \|R\|, \|R\|]` — that is ~25 GB per layer at p90 \|R\|); plus its own probe, `tools/ec2/probe_tailb.py`, which does not exist. `probe_e9l.py` is already generalised (`EXP`/`MAX_S`/`LADDER`) but measures a `load_model` **prefill**, not the hook — it cannot size Part B |
| **Min card** | **20 GB** (weights 6.41 GiB + ≈2.6 GB per chunk). The only row that would fit a 1g.20gb slice |
| **Time** | **< 1 h** for the 35 |

### 2c. E-BEH — behavioral check of τ_K (W1). *Most informative, least ready — run last.*

| | |
|---|---|
| **Waits on you** | the **bands** (the design proposes top-1 ≥ 0.95 HOLDS-B / < 0.90 DEGRADES-B, all `???`); whether `ledger_check.VERDICTS` learns the `-B` words or the entry reuses an existing band with its own hypothesis row; the minimum scored prefix that may report a verdict; the \|C\| cap |
| **The entry must seal** | the five arms exactly (FRESH / REUSE-ALL / REUSE-ORACLE-τ / CACHEBLEND-10,-20 / NULL) and that **NULL is mandatory**; the **FRESH-vs-FRESH identity control must be exactly zero** or the run refuses; determinism (SDPA, fp32); that the continuation was produced by a proprietary model, so this measures a representation effect on held-fixed text, **not generation quality**; the coverage rule for handoffs whose continuation is missing from the trace |
| **Code first** | the **cache-injection splice** on upstream `kvt/cache.py` — mixed cache (reused K/V at p_S re-rotated to p_R for M, fresh elsewhere) under a Qwen3 GQA `[28, 8]` layout plus in-situ recompute of a chosen subset. `0023:1367` requires this be **pinned by an entry before it runs**. Then the continuation extractor out of `traces/`, and the §9 correctness probe: recompute-ALL-in-situ must reproduce FRESH **bit-for-bit** |
| **Min card** | **48 GB** (S prefill 31.56 GiB; a 3g.40gb slice is marginal, 20 GB does not fit) |
| **Time** | ≈ 3 h |

### 2d. The Qwen3 short cell (the 25 of 0029) — **not yours to release**

`docs/2026-09-14-condition-1-status.md:177`: **Condition 1 (0032) is open** — that board does not release 0029's
figures, and the admission outcome must be recorded in a later numbered entry. Until the operator records it, the
short half is a **separate cell** that enters no registered verdict and is never pooled with the 35. The scaled
short cell (0038) is already closed and backed up, so **no GPU work is owed here**: the only open item is a ruling,
plus the owed co-author refutation of 0025–0029 (Path A) that Condition 1 hangs on.

Do not add the 25 to any E-TRUNC or E-TAIL table as a pooled row. A *separate* table is allowed and says so.

---

## 3. The second model family (W7) — and a correction on "1B→3B"

**The registered second family is `llama3.2-3b-to-llama3.1-8b` — Llama-3.2-**3B** → Llama-3.1-**8B**.** There is no
1B→3B pair: `src/linear_ceiling/pairs.py:93` carries exactly one Llama entry, and `LLAMA_LADDER` is the two-model
cross-release ladder 3B → 8B. If you meant the registered pair, read on. If you meant a genuinely new 1B→3B pair,
skip to "a third pair" at the end — it is a different proposal with a real advantage and a real risk.

**What the pair owners have already landed** (all on `main`, all recomputable once the clone is at P):

- **0039** family registration (τ_K ceiling 0.45 registered *before* the fit; ladder and prefix bound taken absolute
  from `config/e9.toml`), **0040** E8 figures (τ_K = **0.2861** = 1 − the pair's own k=1 generic held-out K R² of
  0.7139), **0041** the τ-ordering ruling (τ_agent_K < τ_K for this pair, the opposite of Qwen; `config.py`'s
  refusal became report-only), **0042** short-cell registration, **0043** pre-prefill amendment (atomic checkpoint,
  drain/stop protocol), **0044** **H-E9F HELD, 28 scored of 28 registered**.
- Tooling: `tools/runpod/` (29 commits) — a container-host box path beside `tools/ec2/`, with campaign cost
  ceilings, a drain supervisor and `pull_verify_b.py --final-partial`.
- R8: both mirrors are public under the pair owner's account and were verified against every sha pin 0040–0044
  (784/784 kept-dump files); e8f is `BACKUP VERIFIED`, e9f is complete by file count (§0).
- PR 5 merged `3902a16`.

**So the short Llama cohort has already run.** Your question "is a short-cohort Llama cell worth running first on
smaller hardware" is already answered twice over, and both answers are no:

1. It **ran** — 0044, 28/28, on an **A100-SXM4-80GB** at $1.59/h, driver 17:14:41Z → 18:18:30Z (≈ 64 min).
2. It **could not have run on smaller hardware.** A measured probe (`docs/probes/2026-09-18-llama-8b-fp32-prefill-memory.md`)
   put Llama-3.1-8B, fp32, `sdpa_repeat_kv`, native RoPE, on a 44.43 GiB A40:

   | T | peak GiB | outcome |
   |---:|---:|---|
   | 16,384 | 37.56 | ok |
   | 24,576 | 41.38 | ok |
   | **32,768** | **43.2** | **CUDA OUT OF MEMORY** |

   32,768 *is* `config/e9f.toml`'s registered cap, and that is the easiest case — one model, one forward, no driver
   holding the receiver while it takes three stride-1 dumps plus the identity, null and prefix-invariance controls.

**Which Llama cells fit a 48 GB card: none of them.** Not the long cell, not the short cell, not a re-run. The 3B
source side is never the constraint (23.51 GiB at 32,768) — it is the 8B **receiver** that OOMs below its own cap.
Any Llama GPU work on this pair needs **80 GB**.

**The LONG cell, per the staged drafts** (`append_0045.py` registration, `append_0046.py` figures — staged, unrun,
**numbers provisional until appended**; `config/e9fl.toml` already lists 0045 in `[e9.gate]`):

- Cap **81,920** and floor **32,768** in Llama-3 tokens — the floor equals the short cell's cap, so the two Llama
  cells **partition** their handoffs; 0045 asserts that the ids it excludes under the floor are *exactly* the short
  cell's included set, with the residual above the cap named and counted. The partition is audited, not asserted.
- **Neither side is scaled** (both natively 131,072): no `[e9.rope]`, no `[e9.bridge]`, no `--rope-scaling`. 0035's
  configuration-bridge reading is declared **inapplicable**, and two dump-derived controls stand in its place
  (native-window and a role-scoped RoPE identity — the two sides carry different llama3 factors, 32.0 and 8.0, so an
  unscoped assertion would refuse every correct run).
- It **cannot move, support or refute H-E9L**, and is **never pooled** with 0036's 35. 0046 reads
  `results/e9l/summary.json` only to state 0036's figures *beside* these, with non-comparability spelled out
  (different models, tokenizers, handoff sets, mappers, τ — and one receiver scaled past its pretraining window).
- **Card: 80 GB**, and it is a longer cell than the short one at an 81,920 cap. Budget on the 0044 sitting's rate,
  not on the Qwen numbers.

**What R8 must hold before the LONG cell's entry.** R8 is transport, not evidence, so it never substitutes for a
verified home mirror — but the entry should not land until: every kept dump and record of `results/e9fl/` is pushed;
the push is **two-way verified** (every local file on the Hub *and* every Hub file local, LFS files by `lfs.sha256`,
non-LFS downloaded and hashed) with **exit 0**; and the existing e8f/e9f mirrors stay verified so 0040–0044 remain
recomputable. Prefer the pair owner's account, which already holds the two verified datasets. The two **empty**
datasets under the operator's account should be deleted rather than filled, so there is one home per cell.

**A third pair (1B→3B), if that is what you meant.** Not covered by 0045/0046 and not what W7 asks for — W7 asks for
a second *family*, which exists. As a proposal it has one real advantage and one likely blocker:

- *Advantage:* the receiver would be Llama-3.2-3B, measured at **23.51 GiB at 32,768** — so unlike 3B→8B, a 1B→3B
  short cell **would fit a 48 GB card**, and probably much less.
- *Blocker:* `check_matched_kv` requires `num_key_value_heads` equal **and per-head dim equal**, and
  `scripts/dump_kv.py` calls it unconditionally on every dump — a mismatch is not a mapper question, it is "no dump
  exists". The 3B side is head_dim 128; the 1B side's per-head dim is **plausibly 64**, which would fail outright.
  **I could not verify this today** — `meta-llama/Llama-3.2-1B` is gated (`401` on its raw `config.json`) and no
  local snapshot exists. **Do not take my 64 as fact.**
- *Settle it for free, in a second, before anyone rents anything:* `tools/preflight_pair.py` is CPU-only,
  network-free, weights-free — it opens four JSON files and checks pair resolution, provenance (community
  re-uploads are **not** the same artifact), matched-KV with both the declared and derived head dim printed per
  side, and vocab equality. A `*.json`-only snapshot is enough.
- *If it passes:* it is still a new pair needing its own E8 fit, its own τ, and a family/pair registration entry
  before any E9 cell — i.e. a new campaign, not an add-on. Worth it only if the cheap card matters more than the
  four weeks left.

---

## 4. Per row: environment, probe, run, reader, one-command verify

**Host-agnostic first.** `tools/ec2/box.sh` is AWS-only; everything else is not. On your own box or a container
host, `setup.sh` / `probe_e9l.py` / `run.sh` / `release_sweep.sh` are the box-side scripts and
`pull.py` / `verify_mirror.py` are the home-side ones. If you are on a **rented container** (RunPod and friends),
read `tools/runpod/rp.py`'s header first — four box rules change, and each is a way to lose money or evidence:
`sudo shutdown -h` **does not stop billing**; **stop is not terminate**; **container disk is ephemeral**, which makes
R5 (pull → verify → delete) load-bearing rather than tidy; and there is no instance metadata, so R7's read-back
reads the pod id back from the API.

**Environment, once.** Two clones and two venvs: upstream `kv-transfer-replication` **detached at the cell's pin**
(for every Llama cell, `06f8d55`, now reachable per §0) with torch cu128, and `linear-ceiling` CPU-only. `setup.sh`
builds both idempotently and arms a 24 h self-halt; it also puts the mapper in place by sha and checks the traces
tarball against its manifest, then runs `e9 --check` and `--align-only`. Box scripts **must be LF** — a Windows
clone with `core.autocrlf` hands you CRLF copies that fail on the box.

```bash
# HOME, BEFORE the box exists — the gate does NOT check this and the summarizer refuses later without it (e9s, 09-14)
.venv/Scripts/python.exe -m linear_ceiling.summarize_e9 --calibrate-tau --config config/<exp>.toml
```

```bash
# BOX: probe (R2) before the run, never after. The probe is generalised; give it the RUN's longest prefill,
# not the config's context_cap (a bound, not the run's number).
EXP=<exp> MAX_S=<max n_sender/n_receiver from results/<exp>/align/coverage.json> \
  ~/kv-transfer-replication/.venv/bin/python ~/probe_e9l.py > ~/probe.log 2>&1
EXP=<exp> LADDER=32768,49152,65536,80111 ~/kv-transfer-replication/.venv/bin/python ~/probe_e9l.py   # E-TRUNC: all levels in one ladder

# BOX: run detached (R4). Rotates the log, `python -u`, exit code to ~/<exp>.rc
EXP=<exp> bash ~/run.sh            # or: bash ~/run.sh --resume

# HOME: mirror + verify + delete on the box as each kept dir lands (R5/R6)
BOX=<user>@<ip> .venv/Scripts/python.exe tools/ec2/pull.py <exp>
.venv/Scripts/python.exe tools/ec2/verify_mirror.py <exp>

# BOX: release (R7 steps 0-5), then terminate and read the state back
EXP=<exp> LAUNCH_UTC="<box launch, UTC>" bash ~/release_sweep.sh > ~/release.log 2>&1
```

> **Trap, before any sitting:** `release_sweep.sh:7`'s `OURS_FILES` is a **fixed allowlist of the e9l/e9s
> filenames**. Any new file your sitting puts in `~` — `probe_tailb.py`, a per-level driver, extra configs — is
> reported `NOT OURS` and the sweep returns `foreign=1` **on a clean box**. Extend `OURS_FILES` in the same change
> that adds the file. (The `${EXP}.records.sha256` generalisation is already in.)

**The fail-closed reader that must produce every figure** — one per row, and nothing else may be the source:

| row | reader (in-process, every figure from its verified output) | one-command verify |
|---|---|---|
| E-TAIL Part A | `python -m linear_ceiling.e9_tail --config config/e9l.toml` (**in flight, uncommitted**; runs `summarize_e9.summarize` first) | `.venv/Scripts/python.exe -m linear_ceiling.summarize_e9 --config config/e9l.toml` → PASSED, then the module on the same records |
| E-TRUNC | a **new** paired reader (common subset + paired levels), fail-closed like `summarize_e9`, inputs sha-pinned | `.venv/Scripts/python.exe -m linear_ceiling.e9 --check --config config/<level>.toml` then the reader → exit 0 |
| E-TAIL Part B | the same `e9_tail` surface extended, or a sibling; identity check against the archived dumps is part of it | reader exit 0 **and** the eager-vs-SDPA identity within the entry's stated tolerance |
| E-BEH | a new reader over the per-position KL/argmax summaries; **FRESH-vs-FRESH identity must be exactly 0** | reader exit 0 with the identity arm at 0 and NULL present |
| Llama LONG | `summarize_e9 --config config/e9fl.toml`, in-process inside `append_0046.py` | `.venv/Scripts/python.exe -m linear_ceiling.summarize_e9 --config config/e9fl.toml` |
| any R8 mirror | — | `.venv/Scripts/python.exe tools/hf_verify_backup.py <repo_id> <local_root>` → **exit 0 only when every file matches in both directions** (needs `HF_TOKEN` read scope in the env only) |
| the whole repo | — | `.venv/Scripts/python.exe -m linear_ceiling.ledger_check && … lint_scope && … seal verify` |

For the **R12 recompute** specifically (no new figures, no entry): clone-at-P plus the e9f mirror, then
`summarize_e9 --config config/e9f.toml` pointed at the mirror — and `hf_verify_backup.py` on
`C:\m\e9f` first, since §0's 1,054 = 1,054 is only a file count.

**Suite note, so a red run does not stop you:** the Windows suite is red on 28 + 26 cases (`os.fsync` on a
read-only handle at `e9.py:415`, plus tests that exec bash); Linux CI is green from `118d08e`. Run the suite on
Linux/WSL and treat Windows reds as known.

---

## 5. Return path

1. **Code and docs: a PR against `main`.** One concern per commit, explicit paths, no attribution trailers. Gates
   must pass in the PR: `ledger_check`, `lint_scope`, `seal verify`, and the suite on Linux. Do **not** touch
   `docs/paper/tex/` (another session's, untracked) or `docs/drafts/README.md` (the allocator — propose the change
   in the PR body instead of editing it).
2. **Results: Hub dataset + two-way verify.** Push the cell's `results/<exp>/` (plus the mapper files the entry
   pins), then run `tools/hf_verify_backup.py <repo_id> <local_root>` and **paste its exit-0 line into the PR**.
   R8 is transport, not evidence: the verified home mirror is the evidence, and the entry quotes the reader, not the
   dataset. Public is allowed (operator ruling 2026-09-11). Token in the environment only — **never in a file, a
   log, or a commit** (R9), and revoke the write token when the push is done.
3. **Entries: drafted, never appended.** Stage `docs/drafts/append_00NN.py` in the PR; **ledger appends are the
   operator's**, and so is the number — `docs/drafts/README.md` is the only allocator and assigns at staging time.
   Treat any number you write as provisional and keep every cross-reference a **literal**, not an offset from your
   own `NUM` (inserting an entry inside a block is what offsets got wrong). The script must run the reader
   in-process, refuse out of order, and run `ledger_check` after appending.
4. **Paper material carries no dataset or account names.** Hub dataset names and the account name are a
   **de-anonymization** question still open as ruling 6 in `review-response-map.md:82`; `lcfm_anon` is the
   double-blind copy. Cite entries and figures, never `<account>/<dataset>`.

---

## 6. Priority for the Oct 12 draft — and what the draft says for anything unrun

**In this order**, because it maximizes what the Oct 12 draft can state and defers what needs a card:

1. **The four grounded sentences** — W8, W7, W6, W4's abstract clause. No card, no ruling, no entry. These are the
   reviewer-facing wins and they are free today.
2. **E-TAIL Part A** once the in-flight reader lands — the tail table is the direct answer to W3 ("the mean passes,
   the tail may not"), costs CPU minutes, and is the one new *figure* that can realistically be entered before
   Oct 12. Needs ruling 4 for its carrier entry.
3. **The R12 recompute of 0040/0044**, now unblocked — it makes the second family recomputable from a clean
   checkout, which is what W7's T2 claim rests on. No new numbers, so no entry.
4. **E-TRUNC**, if and only if the margin ruling lands early enough — one config key plus a paired reader, no
   upstream change, ≈3 h on a 48 GB card. The highest-value GPU row per dollar and the only one plausibly *entered*
   by Oct 30.
5. **E-TAIL Part B** — cheapest card, but needs a hook and its own probe.
6. **E-BEH** — start the injection spec now if someone has time, but assume it is post-Oct-30.
7. **Llama LONG cell** — 80 GB, pin now valid; worth scheduling only if a card is already in hand, since W7's T1
   sentence does not need it.

**What the draft says for a row still unrun** — the rule, not a case-by-case decision: **name it as designed and
unrun, cite the design document, and state what it would decide.** Never present it as pending-but-expected, and
never let a reader infer a result. Concretely: "E-TRUNC (designed, unregistered, unrun) isolates length within a
handoff by head-truncating the same senders; it would attribute the residual short↔long gap to length or to the
handoffs." The `[VALIDATED]` / `[BASELINE]` / `[STRETCH]` tags are the repo's existing vocabulary — a designed-unrun
row is **not** `[BASELINE]`. If a row is dropped for time, say so in one clause rather than silently omitting it;
the E-RL appendix is being dropped for exactly this reason (N2).

And the standing sentence that only an entry reporting a number may retire: **"No downstream-quality number is
claimed."** It stands until E-BEH's entry lands. Do not soften it in the draft.

---

## 7. Rulings — answerable in one reply

Recommended default in **bold**; each is yours, and I have implemented none of them.

1. **E-TRUNC margin** — how close must the L32 far-from-seam median come to 0038's scaled-short 0.0381 to read as
   "length" rather than "the handoffs"? → **Default: register a band of ±0.005 absolute (≈13 % of 0.0381) and
   report "unattributed" between it and FULL's 0.0629.** Reason: 0037 registered "near/in between" with no
   threshold, and that gap is what made 0038's share unclassifiable; fix it before prefill this time.
2. **E-TRUNC shrinkage gate** — the minimum |M_∩| / |M_FULL| below which a handoff is void for the comparison. →
   **Default: 0.80, reported per handoff before any verdict is read.**
3. **E-TRUNC L32-native** — include the native-receiver cell, and if so, is R re-prefilled natively? →
   **Default: include it, keep R under YaRN, and state so** — it is the only cell where native vs YaRN is comparable
   on the same tokens, and keeping R fixed changes one thing at a time.
4. **E-TAIL Part A's carrier** — does the tail table ride the owed corrective f* entry, or get its own? →
   **Default: one entry, the corrective one, widened to carry the tail counts, the per-handoff maximum, the bin
   means and the |R| row.** Reason: they are all re-reads of the same verified records, and the corrective entry is
   owed anyway (README's H-E9 row still reads "f* = 0 at every matched token").
5. **E-TAIL Part B** — registered with a band, or descriptive? → **Default: descriptive for MLSys**, reported beside
   µ and δ_max. A band on a quantity whose attribution statement is not yet readable would be premature.
6. **E-BEH bands and verdict words** — the design proposes top-1 ≥ 0.95 HOLDS-B / < 0.90 DEGRADES-B. →
   **Default: accept those two numbers, and reuse the existing band words with a new hypothesis row rather than
   teaching `ledger_check.VERDICTS` the `-B` suffix** — fewer moving parts in the gate.
7. **W5 entry count** — one entry for the bin means, or two? → **Default: one** (folded into ruling 4's entry).
8. **Condition 1 / the Qwen3 short cell** — may the 25 appear in MLSys tables? → **Default: no pooled row; a
   separate table only, labelled as a separate cell**, until the admission outcome is recorded in a numbered entry.
   This is also the answer to "may the short cell ride along" from the box plan.
9. **A third pair (1B→3B)** — pursue, or stay on two families? → **Default: run `tools/preflight_pair.py` this week
   (free, CPU, no card) and decide on its output; do not plan a campaign before it passes matched-KV.** If it fails,
   the question closes for nothing.
10. **Llama LONG cell scheduling** — now that the pin is merged, request an 80 GB card before Oct 30? →
    **Default: no.** W7's T1 sentence is grounded on 0034 today; spend the remaining weeks on E-TRUNC and the tail
    table, and let the long Llama cell be the first post-deadline sitting.
11. **Housekeeping** — delete the two empty Hub datasets under the operator's account, and the
    `lc-e9l-2026-09-10` key pair / `lc-e9l-ssh` group in us-east-1? → **Default: delete the two empty datasets**
    (one home per cell, and they are what the review map calls "the Hub targets"); **keep the key pair and group**
    — both free, and the group is the one reviewed ingress rule this lane has.

**Not in this document, and not mine to decide:** the camera-ready date email to the workshop organizers, the
de-anonymization ruling (map:82), the Lean restatement, and the task-slot owners in
`docs/2026-09-30-team-status-wednesday.md`, which are still `???`.

# E-RL — design: KV reuse across RL post-training checkpoints

**Date:** 2026-09-02 · **Status:** design, unnumbered, not registered. The drafts README is the
only allocator; this document carries no entry number and no hypothesis number ("E-RL" is a
working name). Nothing here is a ledger figure. Where a value is proposed rather than verified it
is marked *(proposed)* or `???`. Where the pick-up session filled or corrected a line, the fill is
marked *(pick-up 2026-09-02)* and its evidence is in §10.

**Reframed 2026-09-02 (operator's ruling: "I'm not doing RL-algorithms").** E-RL is a systems
cost comparison — recompute cost vs stale-KV cost at a weight update — read for MLSys. The
operator's ruling promotes the stale-vs-fresh importance ratio and its effective sample size from
descriptive (Appendix A.3(b)) to verdict-bearing; per A.3(b)'s own rule the promotion is a named
amendment: **author Hossain Pazooki, 2026-09-02.** The own run becomes primary and unconditional;
OLMo becomes the descriptive far tail; the conditional gate is deleted.

**Checked at pick-up** (`main` at `8b6cced`; suite 356 passed / 1 skipped; `ledger_check`, seal
verify, `lint_scope`, `e9 --check` all green on the `36d73b3f` pin): 0023's τ_K = 0.3186,
τ_V = 0.4867, HOLDS ≤ 0.15, DEGRADES ≥ 0.50, centered per-token δ in R² units, f*(τ) as oracle
selective-recompute fraction, identity and δ_null controls, seam bins — byte-identical between
`ba35f7d` and HEAD. `list_repo_refs("allenai/OLMo-2-0425-1B-RLVR1")`: 13 branches,
`step_200` … `step_2600`, stride 200. The model card's "every 20 training steps" is template
text and is wrong for this repo; the branch list governs. `main` is a fourteenth revision whose
`model.safetensors` differs from `step_2600`'s and whose step is not on the branch list; it is
not a lag point *(pick-up 2026-09-02)*.

## 1. Question

*At a weight update in RL post-training, is it cheaper to recompute the in-flight KV cache under
the new weights or to continue on the cache the old weights wrote — and at what lag does the
answer flip? Does a linear mapper move that lag?*

The switch is structural, not observed: the rollout engine's cache was written by policy t and
is read by policy t+k, so cause 4 of the invalidation taxonomy is present by construction. Three
systems already take a position on it, and none of them measures the trade:

- **The recompute side — AReaL** (Fu, Gao, Shen et al., NeurIPS 2025; arXiv:2505.24298).
  Interruptible rollout workers: "Upon the interruption, the rollout workers discard KV caches
  computed by old weights, and re-compute them using the new weights" (§4.1, quoted at
  pick-up). AReaL pays to recompute.
- **The cost side — Laminar** (HKU + ByteDance Seed; arXiv:2510.12633; EuroSys 2026 per the
  HKU-hosted PDF's filename, not stated in the arXiv text). Criticizes exactly that choice, §2.3
  (quoted at pick-up): "The pause-and-sync cycle incurs significant overhead by forcing rollouts
  to rebuild the KVCache (i.e., re-prefill) for every interrupted trajectory, repeatedly in each
  RL iteration, wasting GPU resources without advancing generation. (2) Generating a single
  response with inconsistent policy versions can harm model convergence". Laminar calls the
  recompute a cost — and, in the same breath, calls continuing without it a convergence risk.
  That second clause is the stale side's harm claim, unmeasured there; it is what statistic (B)
  prices.
- **The production default — vLLM's async-RL API** (`docs.vllm.ai/en/stable/training/async_rl/`,
  read at pick-up). `pause_generation(mode="keep")` freezes in-flight requests; they "produce
  tokens from the old weights before the pause and tokens from the new weights after resume". The
  `clear_cache` flag decides the cache: `True` discards it so everything after resume is computed
  under the new weights; `False` keeps it so "some tokens in context may still reflect the old
  weights". The docs give no guidance on which to choose. The engine ships the switch with the
  decision left to the caller.

E-RL is the measurement that decides the flag. That is a Lane-B sentence (a policy fact, present
by construction) with no blog in it, not a Lane-A frequency, and is described as such. Public
agent traces cannot evidence model switches (H-E7a, NOT CONFIRMED, 0018/0024); this lane does not
need them to.

**Relation to E9.** Same measurement, other axis. A cached KV is a function of the context that
produced it and the weights that computed it. E9 fixes weights and changes context (re-render);
E-RL fixes context and changes weights (checkpoint step). Statistic (A), τ, bounds, and controls
are inherited from 0023 unchanged so that re-render loss, mapper loss, and step loss sit on one
yardstick. E-RL depends on E9 only for the measured per-checkpoint dump cost, not for its
verdict, and E9's pin does not move for it.

## 2. Hypothesis, statistics, cells

Two verdict-bearing statistics, one per question. Neither is merged into the other.

**(A) How many tokens go stale — f*(τ_K).** Per-token centered δ in R² units; f*(τ) median over
held-out sequences; K and V separately. τ_K = 0.3186 and τ_V = 0.4867 as archived — **not
recalibrated** (the recalibration defect is on the 0023 record, and a moved τ would break the
E9/E-RL comparison). f* is already a systems quantity: the fraction of tokens an oracle would
recompute. HOLDS ≤ 0.15 / DEGRADES ≥ 0.50 as in 0023.

**(B) Does the trainer notice — stale-vs-fresh importance ratio and ESS.** For a prompt prefix P
and lag k, with the *fresh* continuation y = y_1..y_T generated greedily by θ_{t+k} on
KV(P) recomputed under θ_{t+k}, and teacher-forcing y under θ_{t+k} on the *stale* KV(P)
written by θ_t:

  r_t = π_{θ_{t+k}}(y_t | P, y_{<t}; stale KV) / π_{θ_{t+k}}(y_t | P, y_{<t}; fresh KV)

per token; per sequence w = Π_t r_t (and the clipped form min(ρ, ·) reported alongside); over
the prompt set, ESS = (Σ_i w_i)² / Σ_i w_i², reported as ESS / N — Stable Asynchrony's own
definition, ESS ≜ (Σ w_i)² / Σ w_i² ∈ [1, B], and its ratio ρ_ess ≜ ESS / B (quoted at pick-up).
Identity at k = 0 gives r_t ≡ 1 and ESS / N = 1 exactly (a control, §5). This is the trainer's
own instrument for stale data: Stable Asynchrony (Han group, MIT; ICML 2026; arXiv:2602.17616)
shows stale rollouts produce heavy-tailed importance weights so a few trajectories dominate
updates, and that the variance is reliably predicted by collapsing ESS ("As the ESS ratio
collapses, updates become dominated by a few trajectories, leading to a KL explosion and an
abrupt drop in training reward"); its lag unit is PipelineRL-k, steps off-policy, tested to
k = 128. AIPO's clipped ratio min(π/μ, ρ) with "clipping constant of ρ ∈ [2, 10] seem to work
generally well" is LlamaRL §6 (Wu, Wang, Tang et al., arXiv:2505.24034, 2025-05-29; quoted at
pick-up). We cite their instrument, not their method.

*(pick-up 2026-09-02, skeptic's note, for the human.)* The ratio those papers correct is
behavior-policy vs current-policy — different weights, same cache. E-RL's ratio is the reverse:
same weights, different cache. The instrument (ESS of per-sequence weights) transfers; the numbers
do not. ρ ∈ [2, 10] is a clipping constant on a policy-version ratio, not a HOLDS/DEGRADES bound
on ESS / N, and Stable Asynchrony reports ESS as a predictor of variance, not as a threshold —
the body check at pick-up found the formula, the ratio, and "ESS ≪ B" as the failure regime, and
**no numeric threshold**; VCPO scales the learning rate by ρ_ess continuously instead of gating
on it. So (B)'s bounds are **operator judgment until anchored** and must be stated as such,
exactly as 0023 did for DEGRADES ≥ 0.50:

  HOLDS_B: median ESS / N ≥ `???` · DEGRADES_B: median ESS / N ≤ `???`

No external anchor with a number in it exists in the cited set; the paper's sentence will say
"the operator's stated judgment", as 0023's does.

**Per source, per statistic, two curves.** L_id = first lag at which identity leaves HOLDS;
L_map = the same for the fitted linear mapper. Four L's per source: L_id^A, L_map^A, L_id^B,
L_map^B. Lag is in that source's own unit.

**Cells, per source, per statistic, at the registered τ / bounds only:**

| cell | rule |
|---|---|
| MOVED | L_map ≥ L_id + 2 lag units |
| NOT DISTINGUISHED | \|L_map − L_id\| ≤ 1 |
| INVERTED | L_map < L_id − 1 (mapper fails first; a result) |
| BOUNDED BY RANGE | identity never leaves HOLDS in range; largest lag tested reported as a lower bound on L_id |

*(pick-up 2026-09-02, for the human, not rewritten)* The table is complete and disjoint when both
L_id and L_map are defined in range. Two cases fall between rows: (i) identity never leaves HOLDS
but the mapper does — BOUNDED BY RANGE by the identity clause, INVERTED by the mapper's, and the
table does not say which wins; (ii) L_id is defined but the mapper never leaves HOLDS and the
largest lag tested is under L_id + 2 — MOVED is not reachable and no row applies. Both need a
sentence before the seal. A third, new with (B): the two statistics' cells for one source may
disagree (A says BOUNDED BY RANGE, B says INVERTED). *(proposed)* they are reported as two cells
and never combined into one verdict word; the paper's sentence names both.

**Failure as result.** NOT DISTINGUISHED or BOUNDED BY RANGE on both statistics in the own run
means the linear ceiling is a fact about size, not steps, and identity is already the ceiling
across a step at engine lags; the lane closes with one paragraph in the paper, and the flag's
answer is `clear_cache=False` at those lags.

## 3. Sources and lag ladders

**Primary, unconditional: the own run.** An engine's decision is made at lag 1–8 policy
versions; that regime is only reachable with per-step checkpoints. Qwen3-0.6B, GRPO, full-weight
*(proposed; LoRA would make the identity residual rank-r by construction)*, checkpoint saved every
optimizer step to step 40 *(proposed)*. Lags 1, 2, 3, 4, 5, 6, 8 (the engine regime), 10, 20, 40
(the tail) *(proposed)*. Anchor t = step 8 *(proposed; after warm-up, before the run drifts)*, a
second anchor at step 24 if budget allows. Trainer: `???` (TRL, verl, or open-instruct — pinned
by commit before the run; a new dependency, not in the repo). Compute: GRPO on 0.6B for 40 steps
plus 41 per-step dumps of the held-out set (≈ 1.2 GB per checkpoint at stride 1, §4) — sized from
E9's measured numbers before the request, `???`. The 28-layer / 8-KV-head shape is E8's and the
mapper machinery applies unchanged.

**Descriptive extension: OLMo-2-0425-1B-RLVR1.** `Olmo2ForCausalLM`, 16 layers, 16 KV heads,
head_dim 128, rope_theta 500000, no rope_scaling (checked against the upstream shape rules).
Checkpoints at `step_200 … step_2600`. Lags realizable: 200, 400, …, 2400 — the far tail that
shows the ceiling, two orders of magnitude past any engine's lag. *(proposed)* anchors
t ∈ {step_200, step_1200}; partners at every lag from each anchor that exists; that is ≤ 13 dumps
(12 partners of step_200 plus 7 of step_1200, all drawn from the same 13 revisions — recounted at
pick-up). Both statistics and all controls are computed; cells are reported but the OLMo arm
decides nothing about the flag, because no engine runs at lag 200.

Pre-RLVR base: **`allenai/OLMo-2-0425-1B-DPO`** *(pick-up 2026-09-02: the card's `base_model`
frontmatter and its "Finetuned from model" line both name it)*. Registering it as lag 0 is
*(proposed)*: there is no `step_0` branch to compare weights against, so "the DPO `main` weights
are the RLVR initialization" rests on the card's sentence, not on a byte comparison.

"Step" must be pinned to optimizer steps before "lag 200" is used in any sentence: `???`.
*(pick-up 2026-09-02: not resolved. open-instruct's `scripts/train/olmo2/` holds GRPO scripts for
7B, 13B and 32B only; the card links no run config or wandb. The remaining probe is
open-instruct's GRPO trainer at a commit near 2025-04, where `training_step` is one rollout batch
and the optimizer runs `num_epochs × num_mini_batches` times per training step — that
relationship is what the pin must state.)* For the own run the unit is ours to fix: one
checkpoint per optimizer step, so lag = optimizer steps exactly.

**Shared axis.** Relative weight-delta norm ‖θ_{t+k} − θ_t‖ / ‖θ_t‖ and KL(π_t ‖ π_{t+k}) on a
fixed prompt set, computed for every pair in both sources. Descriptive. This is the only place
the two sources are read against each other.

## 4. Arms, costs and data

- **Identity arm.** K_t, V_t reused as-is; scored under θ_{t+k}'s context computation. This is
  the null, and it is what vLLM's `pause_generation(mode="keep")` with `clear_cache=False` does
  in production (§1). *(PipelineRL, arXiv:2509.19128, was the earlier citation for "somebody
  continues on stale KV"; its abstract does not state the cache behaviour and vLLM's flag now
  carries the claim, so it is dropped from the load-bearing role.)*
- **Mapper arm.** Per-head linear least squares K_t → K_{t+k}, V likewise, as in the pinned
  upstream, fit on the training split, scored held-out. One fit per (anchor, lag).
- **The recompute side (descriptive).** The price AReaL pays and Laminar counts: per
  interruption, tokens in flight × per-token prefill under θ_{t+k}. E9 measures a per-checkpoint
  dump cost; restated per token it is the recompute price on this stack. *(pick-up 2026-09-02:
  the E9 GPU pre-flight found the upstream runs float32 and materializes full logits, so that
  figure is an UPPER BOUND on a production prefill and is labelled so; a bf16 engine prefill on
  the same tokens is the number an engine actually pays and is measured separately if cheap
  *(proposed)*.)* Reported beside f* at every lag so the paper's sentence is "recompute costs X
  per interruption; continuing costs f* of the tokens' worth of deviation and an ESS of Y".
- **Held-out sequences.** *(proposed)* reuse the 0023 calibration's held-out set, for
  comparability. *(pick-up 2026-09-02: E9 has handoffs, not a held-out set; the set 0023 calibrated
  τ on is E8's generic dumps — fineweb-edu `sample-10BT`, 50 documents, first 1,024 tokens each,
  stride 4, last 20 % = 10 sequences held out, per `config/e8.toml` and upstream `kvt/data.py`.
  On Qwen3-0.6B, the own run's model, this set is unchanged literally. On OLMo "unchanged" can
  only mean the same documents: OLMo's tokenizer differs from Qwen's, so the token ids, the
  1,024-token spans and the held-out token count all differ.)* Fixed across all checkpoints.
- **Prompt set for (B) and the behavioral control.** `???` — provenance to be stated; the RL
  run's own prompt distribution (GSM/MATH-style for the own run) is the honest choice, since that
  is what the engine has in flight *(proposed)*.
- **Dumps.** Per kept token, upstream `dump_kv` writes K and V in float16 at every layer
  (K_stripped is derived at load): 28 × 8 × 128 × 2 × 2 B = 114,688 B on Qwen3-0.6B and
  16 × 16 × 128 × 2 × 2 B = 131,072 B on OLMo-2 1B *(recomputed at pick-up from the upstream
  writer and both configs)*. Pin anchors and lags rather than dump every checkpoint. A
  `config/e-rl-manifest` (sha256 + size per dump) from the first dump, on the 0024 track-b
  precedent; summarizer refuses on manifest disagreement.

## 5. τ ladder, behavioral control, controls

Folded in from the τ seed (2026-09-02); the seed is Appendix A of this document.

**τ ladder (descriptive).** f*(τ) at τ_K ∈ {0.3186, 0.10, 0.03} and τ_V ∈ {0.4867, 0.10, 0.03}
at every lag. Cells computed at the registered τ only. Ladder values *(proposed)*.

**Behavioral control (descriptive, use-case anchored).** Same *stale* / *fresh* construction as
(B). Greedy, fixed `max_new_tokens` (256 *(proposed)*), identical prompts. Per (prompt, lag):
exact-match fraction over the window; first-divergence position; mean per-position KL of
θ_{t+k}'s next-token distribution, stale vs fresh, teacher-forced on the fresh continuation.
Medians over the prompt set. These three stay descriptive; only the ratio / ESS of (B) was
promoted, and by the named amendment above.

**Controls.** Pipeline identity at k = 0 (f* = 0, r_t ≡ 1, ESS / N = 1, exact-match = 1.0,
KL = 0, exactly; halts on nonzero). Seeded δ_null (0023). Same-norm random delta *(proposed)*:
isotropic perturbation of θ_t at the pair's relative norm, scored under identity on both
statistics — one forward pass per lag; this is (B)'s null: an ESS collapse that a random delta of
the same size also produces says nothing about RL steps. Seam and depth profiles (0023).

## 6. Seal

First exercise of the seal machinery (seal verify currently reports no sealed predictions).
Hash-committed before the own run starts and before any OLMo checkpoint is downloaded. Shape,
all values to be challenged:

1. identity median f*(τ_K = 0.03) at lag 1 and lag 8, own run — `???`
2. identity median ESS / N at lag 1 and lag 8, own run — `???`
3. identity median exact-match over 256 tokens at lag 8, own run — `???`
4. the same three at lag 200 and lag 2400, OLMo — `???`
5. cell per source per statistic — `???`

A seal that predicts BOUNDED BY RANGE at the registered τ and nothing else is not accepted;
items 1–4 are what make it falsifiable.

## 7. Ledger and upstream mechanics

- Registration entry: next free number from the drafts README at append; no `verdict:` line.
  *(pick-up 2026-09-02: `ledger_check` requires every registered hypothesis to have a cell in the
  table, so the registration entry adds the H-row with `unresolved`; from 0024 on a cell changes
  only by a `verdict:` line, which the verdict entry carries.)* Two statistics means either two
  H-ids or one H-id whose verdict names both cells — `???`, decide before the row is added.
  Verdict entry later, own number, `verdict: H-?? = <CELL>` per source.
- Upstream: `Pair` has no revision field and the dump path hardcodes three Qwen pairs, so the
  same repo id at two revisions is inexpressible; nothing in `kvt/` or `scripts/` passes
  `revision=` to `from_pretrained` *(pick-up 2026-09-02, grep of the pinned tree)*. Change request:
  revision-aware `Pair` in `kvt/pairs.py` (for OLMo) and a local-path pair (for the own run's
  checkpoints), as a commit on a branch — the upstream tree is dirty with Run 8 WP3 in progress
  (`docs/ledger.md`, `scripts/eval_perplexity.py`, `scripts/summarize_perplexity.py`) and E-RL
  must not land on it. E-RL then gates on its own pin; E9 stays on `36d73b3f`.
- Statistic (B) and the behavioral control need a scorer the upstream does not have (teacher-
  forced log-probs under a supplied cache vs a recomputed one). Where it lives — upstream
  `scripts/` under the same pin discipline, or `src/linear_ceiling/` — `???`.
- The own run's trainer is a new dependency and its commit is pinned like the upstream.
- MLSys clause, stated now: E-RL runs only if it fits before Oct 30, on the same footing as E8;
  it competes with the n=420 refit and with E9's A100 day for GPU-days and pages. If cut, the
  registration entry ships as the design and both arms are future work.
- Historical handoff briefs and existing HANDOFF rows are not edited; a new row records this
  document.

## 8. Open before registration

- (B)'s bounds: numbers, stated as "operator's stated judgment" as 0023 used (no anchor with a
  number exists in the cited set — body check done, AIPO pinned).
- The three cell-table gaps in §2.
- Trainer choice and pin; compute sizing for the own run from E9's measured numbers; the prompt
  set and its provenance.
- One H-id or two (§7).
- Where the (B) scorer lives (§7).
- Lag-0 registration of the DPO base (card sentence only, no weight comparison possible); "step"
  unit for OLMo.
- Ladder values, window length, every seal number.
- Sequencing: A100 request for E9 first; E-RL sized from E9's numbers.

## 9. Verify

```
git clone https://github.com/hossainpazooki/linear-ceiling && cd linear-ceiling
awk '/^### 0023/,/^### 0024/' ledger/ledger.md
python -c "from huggingface_hub import list_repo_refs as r; print(sorted(b.name for b in r('allenai/OLMo-2-0425-1B-RLVR1').branches))"
python -c "from huggingface_hub import HfApi; a=HfApi(); print({rev:[(s.rfilename,s.lfs.sha256[:12]) for s in a.model_info('allenai/OLMo-2-0425-1B-RLVR1',revision=rev,files_metadata=True).siblings if s.rfilename.endswith('.safetensors')] for rev in ('main','step_2600')})"
```

## 10. Refutation record (pick-up 2026-09-02)

What was checked, how, and what it changed. Every line is a recomputation or a read of the
source, not a restatement.

| claim in this design | move | result |
|---|---|---|
| 0023 figures as quoted | diff of the 0023 block, `ba35f7d` vs `8b6cced` | identical; τ_K = 0.3186, τ_V = 0.4867, 0.15 / 0.50 confirmed in ledger lines 66-67, 84-91 and `config/e9.toml` |
| branch stride 200 | `list_repo_refs` | 13 `step_*` branches at stride 200 plus `main`; card's "every 20" refuted |
| `main` is a lag point | `model_info(files_metadata=True)` on `main`, `step_2600`, `step_200` | three distinct `model.safetensors` sha256; `main` ≠ `step_2600`; `main`'s step unknown; dropped as a lag point |
| ~131 KB and ~114 KB per token | upstream `kvt/data.py::dump_kv` (float16, K and V only) × both HF configs | 131,072 B and 114,688 B; claim holds |
| ≤ 13 dumps for two OLMo anchors | count of forward partners | 12 + 7 partners over 13 revisions; holds |
| cell table complete | case enumeration | two uncovered cases, a third with (B) (§2); left for the human |
| base repo id | RLVR1 card frontmatter | `allenai/OLMo-2-0425-1B-DPO`; filled |
| "step" = optimizer step (OLMo) | open-instruct `scripts/train/olmo2/` listing; card | no 1B script there, no run config on the card; still open |
| "E9's held-out set" | `config/e8.toml`, `summarize_e9.py`, upstream `kvt/data.py` | no such set on E9; the τ-calibration set is E8's 10 held-out fineweb-edu sequences; corrected |
| AReaL recomputes on interruption | arXiv:2505.24298 HTML, §4.1 | exact sentence quoted in §1; NeurIPS 2025 per papers.neurips.cc listing; holds |
| Laminar calls the recompute a cost | arXiv:2510.12633 HTML, §2.3 | exact sentence quoted in §1 (re-prefill overhead "wasting GPU resources", plus "inconsistent policy versions can harm model convergence"); affiliations HKU + ByteDance Seed in the text; EuroSys 2026 only from the HKU PDF filename; holds |
| vLLM `clear_cache` semantics | `docs.vllm.ai/en/stable/training/async_rl/` | `mode` abort (default) / wait / keep; `clear_cache` True discards, False keeps stale entries; old-weights-before / new-weights-after sentence quoted; no guidance on the choice; holds |
| Stable Asynchrony claims | arXiv:2602.17616 HTML body | ESS ≜ (Σw)²/Σw² ∈ [1,B], ρ_ess = ESS/B, "ESS ≪ B" failure regime, KL-explosion sentence quoted; lag unit PipelineRL-k to k = 128; **no numeric ESS threshold in the paper**; holds as instrument, not as bound |
| AIPO ρ ∈ [2, 10] | arXiv:2505.24034 HTML, §6 | LlamaRL (Wu, Wang, Tang et al., 2025-05-29): min(π/μ, ρ) with "ρ ∈ [2,10] seem to work generally well" quoted; pinned |
| PipelineRL as the stale-KV citation | arXiv abstract page | arXiv:2509.19128, Piché et al.; abstract does not state the cache behaviour; replaced by vLLM's flag |
| upstream scorers architecture-agnostic | grep of `scripts/score_positions.py`, `scripts/score_mapper.py`, `kvt/` | no architecture strings in the scorers; blocker is the revision-less `Pair` registry, not the scorers |
| upstream clean at the pin | `git status` in `../kv-transfer-replication` | dirty on four Run 8 files, none invoked by E9; `e9 --check` still ready |

---

## Appendix A — Seed: the τ concern and its resolution (2026-09-02)

Carried verbatim from the seed that preceded this design. Its §1 objection is the reason §5 and §6
above have the shape they do; its "lag 20" proposals were superseded by the stride-200 finding
before this design was written, and its section numbers refer to an earlier draft of §1. A.3(b)'s
"descriptive, not verdict-bearing" was amended for the ratio / ESS part by the named amendment in
this document's header; the exact-match, first-divergence and KL parts stay descriptive.

**Purpose:** carry one design objection and its fix into the session that writes the E-RL
registration entry. This is design, not ledger; no figure below is a result. The only numbers
that are on the record are 0023's: τ_K = 0.3186, τ_V = 0.4867, HOLDS ≤ 0.15, DEGRADES ≥ 0.50,
per-token centered δ in R² units, f*(τ) the oracle selective-recompute fraction.

### A.1 The concern

E-RL as first drafted took τ from 0023 verbatim and defined L_id and L_map as the first lag at
which identity's and the mapper's median f*(τ_K) leave HOLDS. τ_K = 0.3186 was set so a
size-transfer mapper (Qwen3-0.6B → 1.7B) could pass its own tolerance. A weight delta of a few
optimizer steps on a 1B model moves K far less than a size jump does, so under that τ identity
will read f* ≈ 0 at every lag in range, both curves stay in HOLDS, every source lands BOUNDED BY
RANGE, and the draft seal predicts exactly that. An experiment whose sealed prediction is its own
uninformativeness is registered wrong.

### A.2 Why the fix is not a looser or recalibrated τ

- The recalibration defect is on the record: τ at the median of the mapper's own δ made the
  mapper fail its own calibration (f* ≈ 6–7%); own-norm δ read ~4× better than unexplained
  variance and blew up on small-norm tokens. Both were caught before 0023 was written.
- A fixed τ is what makes E9 and E-RL one table: re-render loss, mapper loss, and checkpoint-step
  loss on one yardstick. "A step costs less than a re-render" is a measurement only if τ did not
  move between the two experiments.
- A τ tightened *for* E-RL, after seeing that the inherited one is loose, is a post-hoc choice of
  the kind pre-registration exists to prevent.

So the verdict-bearing τ stays. What changes is what is reported beside it and what is sealed.

### A.3 The resolution, three parts

**(a) τ ladder, descriptive.** f*(τ) is reported at τ_K ∈ {0.3186, 0.10, 0.03} and
τ_V ∈ {0.4867, 0.10, 0.03}, median over held-out sequences, K and V separately, at every lag in
both sources. The verdict cells are computed at the registered τ only. The ladder is descriptive
and says how far inside the tolerance identity sits, so BOUNDED BY RANGE at 0.3186 comes with the
lag at which 0.03 is crossed, if any. Ladder values are proposed and must be challenged before the
seal; they are not a citation.

**(b) Behavioral control, use-case anchored.** For a prompt prefix P and lag k: *stale* = KV(P)
computed under θ_t, continuation generated by θ_{t+k}; *fresh* = KV(P) recomputed under θ_{t+k},
continuation generated by θ_{t+k}. Greedy decoding, fixed `max_new_tokens`, identical prompts.
Three numbers per (prompt, lag): exact-match fraction over the generated window; position of
first divergence; mean per-position KL of θ_{t+k}'s next-token distribution, stale vs fresh,
under teacher forcing on the fresh continuation. Aggregated as medians over the prompt set. This
is what an async trainer loses when it continues on a stale cache; f*(τ) is a proxy for it.
Registered as **descriptive** in this cycle, not verdict-bearing: it has no null and no external
anchor yet, and promoting it is a future amendment with the author named, not a silent edit.

**(c) Seal shape.** The sealed prediction must include a number at the ladder and a number from
the behavioral control, so that BOUNDED BY RANGE at the registered τ is not the whole seal. A
prediction that identity holds at 0.03 *and* agrees greedily at the first realizable lag is
falsifiable; the original seal was not. (The seed's lag-20 values are superseded by §6.)

### A.4 Controls to register beside the above

- **Pipeline identity** at k = 0: f* = 0 exactly at every τ, exact-match = 1.0 exactly,
  KL = 0 exactly. Halts on nonzero, as 0023's control does.
- **Seeded δ_null**, inherited from 0023.
- **Same-norm random delta** (proposed, cheap): perturb θ_t by isotropic noise with the same
  relative norm ‖θ_{t+k} − θ_t‖ / ‖θ_t‖ and score identity against it. Says whether an RL step's
  effect on K/V is distinguishable from a random delta of the same size. One forward pass per
  lag; descriptive.
- **Seam and depth profiles**, inherited from 0023, so a HOLDS that is really "holds everywhere
  except the first 64 tokens" is visible.

### A.5 Compute impact

Small relative to dumps: the behavioral control is two short greedy generations per (prompt, lag)
on the θ_{t+k} checkpoint — for 50 prompts × 256 tokens × ~10 lags, well under one checkpoint's
dump cost. The same-norm null is one forward pass per lag.

### A.6 Vocabulary

"stale KV" / "fresh KV" as defined in A.3(b); "lag k" = k optimizer steps between the weights that
wrote the cache and the weights that read it; cause 4 = switch, from the invalidation taxonomy;
"descriptive" = reported, not verdict-bearing.

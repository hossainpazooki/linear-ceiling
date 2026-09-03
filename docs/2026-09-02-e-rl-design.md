# E-RL — design: KV reuse across RL post-training checkpoints

**Date:** 2026-09-02 · **Status:** design, unnumbered, not registered. The drafts README is the
only allocator; this document carries no entry number and no hypothesis number ("E-RL" is a
working name). Nothing here is a ledger figure. Where a value is proposed rather than verified it
is marked *(proposed)* or `???`. Where the pick-up session filled or corrected a line, the fill is
marked *(pick-up 2026-09-02)* and its evidence is in §10.

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

*Across optimizer steps of RL post-training, at what lag does identity KV reuse fail, and does a
linear mapper move that lag?*

Motivation, stated once: the cross-model KV literature assumes model switches are common; public
agent traces cannot evidence them (H-E7a, NOT CONFIRMED, 0018/0024). In RL post-training a switch
is structural — the rollout engine's cache was written by policy t and is read by policy t+k —
so cause 4 of the invalidation taxonomy is present by construction, not by observation. This
lane makes the paper's motivating sentence true by definition, and then measures what the switch
costs. It is Lane-B-shaped (a policy fact), not Lane-A-shaped (a measured frequency), and is
described as such.

**Relation to E9.** Same measurement, other axis. A cached KV is a function of the context that
produced it and the weights that computed it. E9 fixes weights and changes context (re-render);
E-RL fixes context and changes weights (checkpoint step). Statistic, τ, bounds, and controls are
inherited from 0023 unchanged so that re-render loss, mapper loss, and step loss sit on one
yardstick. E-RL depends on E9 only for the measured per-checkpoint dump cost, not for its
verdict, and E9's pin does not move for it.

## 2. Hypothesis, statistic, cells

**Statistic.** Per-token centered δ in R² units; f*(τ) median over held-out sequences; K and V
separately. τ_K = 0.3186 and τ_V = 0.4867 as archived — **not recalibrated** (the recalibration
defect is on the 0023 record, and a moved τ would break the E9/E-RL comparison).

**Per source, two curves.** L_id = first lag at which identity's median f*(τ_K) exceeds 0.15.
L_map = the same for the fitted linear mapper. Lag is in that source's own unit.

**Cells, per source, at the registered τ only:**

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
sentence before the seal.

Verdicts are per source. There is no pooled curve. The only cross-source statement is on the
shared physical axis (§3), never on lag.

**Failure as result.** NOT DISTINGUISHED or BOUNDED BY RANGE in both sources means the linear
ceiling is a fact about size, not steps, and identity is already the ceiling across a step; the
lane closes with one paragraph in the paper.

## 3. Sources and lag ladders

**Public: OLMo-2-0425-1B-RLVR1.** `Olmo2ForCausalLM`, 16 layers, 16 KV heads, head_dim 128,
rope_theta 500000, no rope_scaling (checked against the upstream shape rules). Checkpoints at
`step_200 … step_2600`. Lags realizable: 200, 400, …, 2400. *(proposed)* anchors t ∈
{step_200, step_1200}; partners at every lag from each anchor that exists; that is ≤ 13 dumps
(12 partners of step_200 plus 7 of step_1200, all drawn from the same 13 revisions — recounted at
pick-up).

Pre-RLVR base: **`allenai/OLMo-2-0425-1B-DPO`** *(pick-up 2026-09-02: the card's `base_model`
frontmatter and its "Finetuned from model" line both name it)*. Registering it as lag 0 is
*(proposed)*: there is no `step_0` branch to compare weights against, so "the DPO `main` weights
are the RLVR initialization" rests on the card's sentence, not on a byte comparison.

"Step" must be pinned to optimizer steps before "lag 200" is used in any sentence: `???`.
*(pick-up 2026-09-02: not resolved. open-instruct's `scripts/train/olmo2/` holds GRPO scripts for
7B, 13B and 32B only; the card links no run config or wandb. The remaining probe is
open-instruct's GRPO trainer at a commit near 2025-04, where `training_step` is one rollout batch
and the optimizer runs `num_epochs × num_mini_batches` times per training step — that
relationship is what the pin must state.)*

**Own run (conditional).** Qwen3-0.6B, GRPO, save every step to step 40 *(proposed)*. Lags
1–5, 10, 20, 40. Runs only if OLMo's lag-200 cell is not BOUNDED BY RANGE at τ_K = 0.03 with
high greedy agreement (§5); if OLMo holds there, lag 1–5 on a smaller per-step delta holds a
fortiori and the own run is future work, named as such.

**Shared axis.** Relative weight-delta norm ‖θ_{t+k} − θ_t‖ / ‖θ_t‖ and KL(π_t ‖ π_{t+k}) on a
fixed prompt set, computed for every pair in both sources. Descriptive. This is the only place
the two sources are read against each other.

## 4. Arms and data

- **Identity arm.** K_t, V_t reused as-is; scored under θ_{t+k}'s context computation. This is
  the null, and it is what in-flight-update trainers already do. Citation *(pick-up 2026-09-02)*:
  PipelineRL — Piché, Kamalloo, Pardinas, Chen, Bahdanau, arXiv:2509.19128 (v2, 2025-09-26). The
  abstract says the generation engine "receive[s] updated model weights with minimal interruption
  during the generation of token sequences"; that the in-progress sequences continue on their
  existing KV is the mechanism's description, and must be confirmed in the paper body before the
  paper cites it for that sentence.
- **Mapper arm.** Per-head linear least squares K_t → K_{t+k}, V likewise, as in the pinned
  upstream, fit on the training split, scored held-out. One fit per (anchor, lag).
- **Held-out sequences.** *(proposed)* reuse the 0023 calibration's held-out set, for
  comparability. *(pick-up 2026-09-02: E9 has handoffs, not a held-out set; the set 0023 calibrated
  τ on is E8's generic dumps — fineweb-edu `sample-10BT`, 50 documents, first 1,024 tokens each,
  stride 4, last 20 % = 10 sequences held out, per `config/e8.toml` and upstream `kvt/data.py`.
  "Unchanged" can only mean the same documents: OLMo's tokenizer differs from Qwen's, so the token
  ids, the 1,024-token spans and the held-out token count all differ.)* Fixed across all
  checkpoints.
- **Dumps.** Per kept token, upstream `dump_kv` writes K and V in float16 at every layer
  (K_stripped is derived at load): 16 × 16 × 128 × 2 × 2 B = 131,072 B on OLMo-2 1B and
  28 × 8 × 128 × 2 × 2 B = 114,688 B on Qwen3-0.6B *(recomputed at pick-up from the upstream
  writer and both configs)*. Pin anchors and lags rather than dump every checkpoint. A
  `config/e-rl-manifest` (sha256 + size per dump) from the first dump, on the 0024 track-b
  precedent; summarizer refuses on manifest disagreement.

## 5. τ ladder, behavioral control, controls

Folded in from the τ seed (2026-09-02); the seed is Appendix A of this document.

**τ ladder (descriptive).** f*(τ) at τ_K ∈ {0.3186, 0.10, 0.03} and τ_V ∈ {0.4867, 0.10, 0.03}
at every lag. Cells computed at the registered τ only. Ladder values *(proposed)*.

**Behavioral control (descriptive, use-case anchored).** For prompt prefix P and lag k:
*stale* = KV(P) under θ_t, continuation by θ_{t+k}; *fresh* = KV(P) recomputed under θ_{t+k},
continuation by θ_{t+k}. Greedy, fixed `max_new_tokens` (256 *(proposed)*), identical prompts.
Per (prompt, lag): exact-match fraction over the window; first-divergence position; mean
per-position KL of θ_{t+k}'s next-token distribution, stale vs fresh, teacher-forced on the fresh
continuation. Medians over the prompt set. Not verdict-bearing this cycle; promotion is a named
amendment.

**Controls.** Pipeline identity at k = 0 (f* = 0, exact-match = 1.0, KL = 0, exactly; halts on
nonzero). Seeded δ_null (0023). Same-norm random delta *(proposed)*: isotropic perturbation of
θ_t at the pair's relative norm, scored under identity — one forward pass per lag. Seam and depth
profiles (0023).

## 6. Seal

First exercise of the seal machinery (seal verify currently reports no sealed predictions).
Hash-committed before any checkpoint is downloaded. Shape, all values to be challenged:

1. identity median f*(τ_K = 0.03) at lag 200, OLMo — `???`
2. identity median exact-match over 256 tokens at lag 200, OLMo — `???`
3. the same two at lag 2400, OLMo — `???`
4. the same two at lag 5, own run, if it runs — `???`
5. cell per source — `???`

A seal that predicts BOUNDED BY RANGE at the registered τ and nothing else is not accepted;
items 1–4 are what make it falsifiable.

## 7. Ledger and upstream mechanics

- Registration entry: next free number from the drafts README at append; no `verdict:` line.
  *(pick-up 2026-09-02: `ledger_check` requires every registered hypothesis to have a cell in the
  table, so the registration entry adds the H-row with `unresolved`; from 0024 on a cell changes
  only by a `verdict:` line, which the verdict entry carries.)* Verdict entry later, own number,
  `verdict: H-?? = <CELL>` per source.
- Upstream: `Pair` has no revision field and the dump path hardcodes three Qwen pairs, so the
  same repo id at two revisions is inexpressible; nothing in `kvt/` or `scripts/` passes
  `revision=` to `from_pretrained` *(pick-up 2026-09-02, grep of the pinned tree)*. Change request:
  revision-aware `Pair` in `kvt/pairs.py`, as a commit on a branch — the upstream tree is dirty
  with Run 8 WP3 in progress (`docs/ledger.md`, `scripts/eval_perplexity.py`,
  `scripts/summarize_perplexity.py`) and E-RL must not land on it. E-RL then gates on its own
  pin; E9 stays on `36d73b3f`.
- MLSys clause, stated now: E-RL runs only if it fits before Oct 30, on the same footing as E8;
  it competes with the n=420 refit for GPU-days and pages. If cut, the registration entry ships
  as the design and the OLMo arm is future work.
- Historical handoff briefs and existing HANDOFF rows are not edited; a new row records this
  document.

## 8. Open before registration

- `???` items above: step unit (the one that gates the word "lag"); every seal number.
- The two cell-table gaps in §2.
- Lag-0 registration of the DPO base (card sentence only, no weight comparison possible).
- Full-weight vs LoRA for both sources; OLMo's RLVR recipe checked, own run pinned.
- Ladder values, window length, prompt set and provenance.
- PipelineRL body check for the stale-KV sentence.
- Sequencing: A100 request for E9 first; E-RL dumps sized from E9's numbers.

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
| ≤ 13 dumps for two anchors | count of forward partners | 12 + 7 partners over 13 revisions; holds |
| cell table complete | case enumeration | two uncovered cases (§2); left for the human |
| base repo id | RLVR1 card frontmatter | `allenai/OLMo-2-0425-1B-DPO`; filled |
| "step" = optimizer step | open-instruct `scripts/train/olmo2/` listing; card | no 1B script there, no run config on the card; still open |
| "E9's held-out set" | `config/e8.toml`, `summarize_e9.py`, upstream `kvt/data.py` | no such set on E9; the τ-calibration set is E8's 10 held-out fineweb-edu sequences; corrected |
| PipelineRL citation | arXiv abstract page | arXiv:2509.19128, Piché et al.; abstract does not state the stale-KV continuation; body check open |
| upstream scorers architecture-agnostic | grep of `scripts/score_positions.py`, `scripts/score_mapper.py`, `kvt/` | no architecture strings in the scorers; blocker is the revision-less `Pair` registry, not the scorers |
| upstream clean at the pin | `git status` in `../kv-transfer-replication` | dirty on four Run 8 files, none invoked by E9; `e9 --check` still ready |

---

## Appendix A — Seed: the τ concern and its resolution (2026-09-02)

Carried verbatim from the seed that preceded this design. Its §1 objection is the reason §5 and §6
above have the shape they do; its "lag 20" proposals were superseded by the stride-200 finding
before this design was written, and its section numbers refer to an earlier draft of §1.

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

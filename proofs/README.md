# Lean 4 formalization of the theory in *Carryover Effects in KV Caches Reused in Agentic Workflows and RL Training*

Machine-checked proofs of the theoretical content of the paper (earlier titles: *KV Cache Drift
Across Handoffs in Long-Horizon Agents* and, before it, *Carryover*, hence the namespace). It
covers the registered statistic of ledger entry 0023 (the paper's Equations `eq:delta` and
`eq:fstar`), Theorem `thm:identity`, Theorem `thm:sandwich`, Corollary `cor:seam`, Assumption
`ass:rope`, Proposition `prop:attn` with its value remark, and the numbers of the version titled
*KV Cache Drift Across Handoffs in Long-Horizon Agents* that the theorems explain. Theorem 1
(`thm:identity`), Theorem 2 (`thm:sandwich`), Corollary 3 (`cor:seam`) and Proposition 4 (`prop:attn`)
are the four statements that the paper that is public now numbers on one counter, 1 to 4; its
assumption and its two remarks are numbered separately.

It also covers statements that are not in the paper that is public now. They belong to the next public
form of the paper: the statements on the reader's next-token distribution under a fresh and a reused
cache, Theorem `thm:kl`, Theorem `thm:text` with the remark that follows it, Proposition `prop:greedy`
and Proposition `prop:flip`, except the parts named below as not formalized. Continuing the public
paper's numbering, they would be Theorem 5, Theorem 6, Proposition 7 and Proposition 8 in that form;
where this README writes those numbers, it means the numbers in that form.

Labels such as `thm:identity` refer to the paper's LaTeX source, which lives in the authors' Overleaf
project rather than in this repository.

`fstar` is the exact-criterion version of `f_star` in `src/linear_ceiling/e9_pertoken.py`: both
sort the deviations in descending order and take the least `k < n` whose remaining-token mean is
at most `τ`, else `1`. The implementation judges "at most `τ`" to a relative tolerance of `1e-9`
(plus `1e-15`) for float32 records; the theorems use the exact criterion.

Every file compiles against Mathlib, and no file contains `sorry` or `admit` or declares an axiom. The
114 headline results depend on no axiom other than Lean's three standard ones, `propext`,
`Classical.choice` and `Quot.sound` (`Audit.lean` prints them).

**Status, honestly stated.** On 2026-11-17 (UTC), on one macOS 27 machine (arm64), with Lean `v4.34.0` and
Mathlib `v4.34.0` at the pins below, `lake build` of this package compiled its eleven modules, exited 0 and
printed `Build completed successfully`, and `lake env lean Audit.lean` printed the 114 headline results: 110
depend on `propext`, `Classical.choice` and `Quot.sound`, and four (`gen_length`, `genStop_eq_gen_of_live`,
`genStop_length_of_live`, `genStop_prefix`) on `propext` alone. The fifteen files that build read
(`lean-toolchain`, `lakefile.toml`, `lake-manifest.json`, `Audit.lean`, `Carryover.lean` and the ten files of
`Carryover/`) are, byte for byte, those of the git tree `3c0798c6f1740482c3ed7eb751facd4f9e65553e`. That tree
is this directory in the commit that adds the five `Pred` files (`git rev-parse <commit>:proofs` prints it);
the commit that gives this README its present text changes no other file in `proofs/`. The other 78 of the
192 theorems and lemmas in `Carryover/` were type-checked by that build and are not printed by the audit. The
build has not been run in CI, on Linux or on Windows.

## The paper's results and their declarations

The paper that is public now has two theorems, a corollary and a proposition, numbered 1 to 4. The first
table gives the declarations that state them. The second table gives the declarations for the two
theorems, the remark and the two propositions that belong to the next public form of the paper and are
not in the public one; the two theorems and the two propositions are numbered 5 to 8 in that form. Each
declaration the two tables name as stating a result is among the 114 that `Audit.lean` prints;
`padTree`, which stands in a hypothesis, is a definition and is not printed.

| The paper that is public now | Lean declarations |
|---|---|
| Theorem 1 (`thm:identity`) | `thm_identity` (the whole statement); its parts `mean_devLH`, `mu_dev`, `theorem1` and `theorem1_verdict` in `Identity.lean`, and `fstar_eq_zero_iff` in `Fstar.lean` |
| Theorem 2 (`thm:sandwich`) | `fstar_antitone` (nonincreasing in `τ`) and `theorem2_sandwich` (the displayed bounds), in `Fstar.lean` |
| Corollary 3 (`cor:seam`) | `cor_seam` and `cor_seam_positions` (the upper bound and `f*(τ) = 0`), `cor_seam_converse`, `cor_seam_large_n`, in `Seams.lean` |
| Proposition 4 (`prop:attn`) | `abs_deltaZ_le` (logits), `prop_attn_weights_iSup` (weights), `prop_attn_diffuse` and `prop_attn_diffuse_causal` (diffuse), `prop_attn_tail_ret` (general), `prop_attn_concentrated_ret` (concentrated), in `Attention.lean` |

| The next public form of the paper (not in the public one) | Lean declarations |
|---|---|
| Theorem 5 (`thm:kl`) | `kl_softmax` (part a, the per-token KL as a cumulant gap); `kl_softmax_le_osc`, `kl_softmax_le_osc_sq` and `kl_softmax_le_of_abs` (part b, upper bounds by the oscillation of the logit shift); `hell_le_kl`, `l1_sq_le_four_hell` and `l1_sq_le_four_kl` (part c, lower bounds); `control_floor`, `holds_threshold_needs_osc` and `degrades_threshold_needs_osc` (the three numbers), in `PredKL.lean` |
| Theorem 6 (`thm:text`) | `meanKL_expect` (part a, the mean per-token KL of a text, with `kl_seqProb_expect`, `kl_seqProb` and `seqProb_marginal`); `kl_prod`, `kl_prod_eq_single`, `kl_prod_pos_of_ne`, `kl_branch_zero` and `kl_pos_of_ne` (part b, the example), in `PredKL.lean`; for part c, texts that end early, `kl_seqProb_stop` (the identity, under the hypothesis that after a text has ended both readers continue with one common law, the tree `R` of `padTree ended P R` and `padTree ended Q R`) and `meanKL_stop_bounds` (the two bounds, under that hypothesis and two more: the empty text has not ended, `ended [] = false`, and the limit is at least one token, `0 < T`), with `liveCount_pos`, `liveCount_le` and `liveCount_of_live`, in `PredStop.lean` |
| Remark after Theorem 6 (what a low mean can still hold) | `card_ge_mul_le` and `holds_at_most_two`, in `PredKL.lean` |
| Proposition 7 (`prop:greedy`) | `softmax_lt_iff`, `softmax_le_iff`, `argmax_stable` and `argmax_stable_of_abs` (part a), `near_tie_flip` (part c), in `PredFlip.lean`; `flip_needs_osc` (part a in contrapositive form) and `flip_forces_kl` (part b), in `PredMain.lean`; the latter is proved from `flip_forces_hell`, in `PredFlip.lean`, and `hell_le_kl`, in `PredKL.lean` |
| Proposition 8 (`prop:flip`) | `genStop_eq_iff` (part a) and `answer_flip_stop` (part b, as far as the last table of this README says: it states neither that the two runs differ nor that its position is the first at which they differ, and both follow from what it states), in `PredStop.lean`; `flips_le_divergences` (part c), in `PredFlip.lean` |

For Theorem 1 to Proposition 4, that each declaration states the paper's result was checked by reading
the two side by side. Several Lean statements are more general than the paper's (see *Modeling choices*).
The sentence of Assumption `ass:rope` on the YaRN temperature is not formalized: the temperature is
absorbed into `‖q_i‖`.

Of the statements that belong to the next public form of the paper (Theorem 5 to Proposition 8, not in
the public one), these parts are not formalized. In part b of Theorem 6: the formula for a general
source, the statement that the excess can be any factor, and the sentence that every text beginning
with the example's token has the stated mean. Before Theorem 5: the sentence that a shift equal on
every token leaves the distribution unchanged, which no single declaration states. And the sentences
between the statements: the paragraph after Theorem 5, the paragraph after Theorem 6 (it says, among
other things, that a reading on texts from one source gives no bound on a reading on texts from
another), the part of the remark on a median, the example after Proposition 7, the paragraph after
Proposition 8, and the sentence after its proof on the runs the paper reports. This list was made by
reading the present text of those statements against the declarations; the proofs written in the paper
were not compared with the Lean proofs.

## Building

Toolchain: Lean `v4.34.0`, Mathlib `v4.34.0` (pinned in `lean-toolchain`,
`lakefile.toml` and `lake-manifest.json`). Install Lean with `elan`.

```sh
cd proofs
lake exe cache get          # downloads the prebuilt Mathlib into .lake/ (several GB)
lake build                  # checks every proof
lake env lean Audit.lean    # prints the axioms of every headline result
./check.sh                  # the same two steps without lake (see below)
```

`check.sh` compiles each module with `lean -o` in dependency order and then runs `Audit.lean`,
without `lake`. It needs the Mathlib build in `.lake/packages`, from `lake exe cache get` or from
another project with the same `lake-manifest.json`. It was written for the earlier pins, the release
candidate `v4.34.0-rc2`, whose `lake` exits with `SIGTRAP` (exit code 133) on macOS 27, even for
`lake --version` (lean4 issue 15087, closed as fixed in `v4.34.0`). At the current pins it was run on
2026-11-17 (UTC) on macOS 27 (arm64), with `LEAN` set to the `lean` of the `v4.34.0` toolchain: it
compiled the ten modules and `Carryover.lean`, printed the audit's 114 results and exited 0.
`.lake/` is git-ignored.

## Files

| File | Paper content |
|---|---|
| `Carryover/Fstar.lean` | Equation `eq:fstar` (literal, via sorting), `μ`, `p(τ)`, `β(d)`, `δ_max`; Theorem 1's core `f*(τ)=0 ↔ μ ≤ τ`; all of Theorem 2; the subset characterisation of the statistic |
| `Carryover/Identity.lean` | Equation `eq:delta`, `R²` with the centered denominator, Theorem 1 (`μ = 1 − R̄²` and the verdict clause, for `L` layers and `H` heads), the retained-mean exchange used in the proof of Proposition 4 |
| `Carryover/Seams.lean` | Corollary 3 (both directions), with the near-seam set built from `m` windows of at most `w` matched tokens, or from receiver positions |
| `Carryover/Attention.lean` | Assumption `ass:rope`, the causally masked softmax, its Jacobian / mean-value bound, Proposition 4 (logits, weights, diffuse, general, concentrated), the value remark |
| `Carryover/Numbers.lean` | The numbers of the *KV Cache Drift* version that Theorems 1 and 2 explain (that version's Tables 1, 2 and 6, the configuration bridge, the matched configuration comparison) |
| `Carryover/Pred.lean` | Definitions the four files below share, in the namespace `Carryover.Pred`: a next-token distribution on a finite vocabulary (`IsDist`), `kl`, `hell`, the softmax over the whole vocabulary (`Carryover.softmax` is the masked one of `Attention.lean`), the bound `OscLe` on the oscillation of a logit shift, greedy generation `gen` |
| `Carryover/PredKL.lean` | Next public form of the paper: Theorem 5 (the per-token KL between the fresh and the reused next-token distribution: the cumulant gap, the upper and the lower bounds, the three numbers); Theorem 6's chain rule over a generated text, its mean per-token KL and its example; the remark after Theorem 6 |
| `Carryover/PredFlip.lean` | Next public form of the paper: Proposition 7 parts a and c (the greedy token and the logit margin, the near-tie example); the first position at which two greedy runs differ; Proposition 8 part c. Apart from the paper, in the same file: one numeric value of the Hoeffding tail expression (the inequality itself is not proved) |
| `Carryover/PredMain.lean` | Next public form of the paper: Proposition 7 part b (a change of greedy token bounds the KL from below) and part a in contrapositive form (a changed greedy token forces the fresh logit margin to be at most any bound on the shift's oscillation); two greedy runs are equal exactly when the two rules agree along the fresh run; an answer flip forces the KL lower bound at one position |
| `Carryover/PredStop.lean` | Next public form of the paper: the same facts for runs and texts that end before their token limit, Proposition 8 parts a and b and the part of Theorem 6 on texts that end early |
| `Audit.lean` | `#print axioms` for every headline result |
| `check.sh` | Builds and audits with `lean` directly, without `lake` |

## Paper statement → Lean theorem

The matched tokens of one handoff, arm and read-out are `Fin n`; `δ : Fin n → ℝ` is the deviation.
Keys of one attention query are indexed by the `N = |R|` receiver positions.

| Paper | Lean |
|---|---|
| `μ = (1/n) ∑_{t∈M} δ(t)` | `mu` |
| `δ_(1) ≥ … ≥ δ_(n)` and `m(k)` | `sorted` (ascending), `tailMean` |
| Eq. `eq:fstar`, the oracle removal fraction `f*(τ)` | `fstar` (least feasible `k`, else `1`); `fstar_spec`, `fstar_nonneg`, `fstar_le_one` |
| `f*(τ) = 0 ⟺ μ ≤ τ` | `fstar_eq_zero_iff`, `fstar_pos_iff` |
| "the oracle retains a set whose mean is at most τ" | `exists_retained_set`; converse `fstar_le_of_subset` |
| Eq. `eq:delta`: `s²_{l,h}`, `δ_{l,h}(t)`, `δ(t)` | `s2`, `devLH`, `dev` |
| `R²(l,h) = 1 − SSE/SST`, `R̄²` | `R2`, `R2bar` |
| Thm 1: `(1/n)∑ δ_{l,h} = 1 − R²(l,h)` | `mean_devLH` |
| Thm 1: `μ = 1 − R̄²` | `mu_dev` |
| Thm 1: `f*(τ) = 0 ⟺ R̄² ≥ 1 − τ` | `theorem1`, `theorem1_pos` |
| Thm 1: with `τ_K = 1 − R²_map`, `f*(τ_K)=0 ⟺ R̄² ≥ R²_map` | `theorem1_verdict` |
| Thm 1 as stated, for `L` layers and `H` KV heads | `thm_identity` |
| Thm 2: `f*` nonincreasing in `τ` | `fstar_antitone` |
| Thm 2: `f*(τ) ≤ p(τ)` | `fstar_le_p` |
| Thm 2: `p(τ) ≤ min{1, μ/τ}` (Markov) | `p_le_one`, `p_le_mu_div` |
| Thm 2: `(μ−τ)⁺/(δ_max−τ) ≤ f*(τ)`, read as 0 if `δ_max ≤ τ` | `lower_bound_max`, `lower_bound_deltaMax`, `fstar_eq_zero_of_deltaMax_le` |
| Thm 2: `(β(d)d−τ)⁺/(d−τ) ≤ f*(τ)` for each `d > τ`, and the `sup` | `lower_bound_beta`, `lower_bound_beta_pos`, `lower_bound_beta_iSup` |
| Thm 2 as displayed | `theorem2_sandwich` |
| Cor 3: `m` seams, at most `w` matched tokens following each | `nearSet`, `card_nearSet_le`; from positions `posWindow`, `card_posWindow_le` |
| Cor 3: `μ ≤ δ_far + (mw/n)(δ_near − δ_far)` and `f*(τ)=0` | `cor_seam` (from `seam_mean_le`, `seam_zero_floor`); `cor_seam_positions` |
| Cor 3 converse: `μ ≥ (1 − mw/n) δ'` and `f*(τ) > 0` | `cor_seam_converse` (from `seam_mean_ge`, `seam_pos_floor`) |
| Cor 3: "which holds for all large `n`" | `cor_seam_large_n` |
| Assumption `ass:rope`: `z_ij = q_iᵀ R_{j−i} k̃_j /√d`, `R` orthogonal, `d` the head dimension | `logit` (with `R : E ≃ₗᵢ[ℝ] E`), `logits` |
| Causal masking: query `i` attends to positions `j ≤ i` | `softmax V` (zero off `V`), `causalMask` |
| Prop 4: `|Δz_ij| ≤ ‖q_i‖ s √(δ(j)/d)` | `logit_shift_le`, `abs_deltaZ_le` |
| Prop 4: unmatched / repaired tokens have `Δk̃_j = 0`, so `Δz_ij = 0` | `deltaZ_eq_zero` |
| Softmax Jacobian `diag(a) − aaᵀ` along the path | `hasDerivAt_softmax_path` |
| Prop 4: `‖a' − a‖₁ ≤ 2 sup_u ∑_j a_j(u)|Δz_j|` | `softmax_l1_shift` (mean-value form), `softmax_l1_shift_le`, `softmax_l1_shift_iSup`, `prop_attn_weights`, `prop_attn_weights_iSup` |
| Prop 4, diffuse: `a_ij(u) ≤ c/|R|` gives `‖a' − a‖₁ ≤ 2c‖q‖ s √(μ^ret/d)`, `μ^ret` over the full retained set | `diffuse_bound`, `prop_attn_diffuse`, `prop_attn_diffuse_causal` |
| Proof: the average over `(l,h)` of `μ^ret_{l,h}` is at most `τ` | `retained_mean_avg`, `retained_mean_le` |
| Prop 4, general: `‖a' − a‖₁ ≤ 2‖q‖ s √(δ^max/d)` | `weighted_le_max`, `prop_attn_tail`, `prop_attn_tail_ret` (`retMax`) |
| Prop 4, concentrated (all but an `ε` share on one token `j`) | `concentrated_bound`, `prop_attn_concentrated`, `prop_attn_concentrated_ret` |
| Remark: `‖o' − o‖ ≤ ‖a' − a‖₁ max‖v_j‖ + ∑ a'_j ‖Δv_j‖`, `‖Δv_j‖ = s^V √δ^V(j)` | `value_shift_le`, `norm_deltaV_eq` |
| `τ_K = 1 − 0.6814`, `τ_V = 1 − 0.5133` | `tauK_eq`, `tauV_eq` |
| Table 1 and the bridge, read through Thm 1 | `arms_same_K`, `arms_same_V`, `arms_cross_K`, `arms_cross_V`, `bridge_zero` |
| Ladder signs read through Thm 1 (`R²` medians `0.8894`, `0.8779 < 0.9`; scaled short `μ = 0.0895`) | `ladder_mid_K_pos`, `ladder_mid_V_pos`, `scaled_short_identity`, `matched_zero`, `scaled_short_mid_zero`, `short_low_pos` |
| Tables 2 and 6 nondecreasing as `τ` tightens (Thm 2) | `additional_models_monotone`, `tau_ladder_monotone` |
| Matched comparison: `0 ≤ p(τ_K) ≤ μ/τ_K` on medians; shares `0.43`, `0.39` | `matched_upper_chain`, `matched_shares` |
| Seam levels: `0.03 < 0.0629 < τ_K`; far level within `τ_K` gives `f* = 0` | `seam_levels`, `far_level_zero` |

The last six rows are the number checks of `Carryover/Numbers.lean`. They are those of the *KV Cache Drift*
version, and the tables they name are that version's.

### The next-token statements (`Carryover.Pred`)

At one position the vocabulary is a finite type `ι`. The reader's next-token distribution is `p = softmax z`
under its fresh cache and `q = softmax (z + e)` under the reused cache, with `e` the shift of the logits.
A text of `T` tokens is drawn from a tree of conditionals, one next-token distribution for each prefix.

Every statement in this table belongs to the next public form of the paper; the paper that is public now
holds none of them. Thm 5, Thm 6, Prop 7 and Prop 8 are their numbers in that form.

| The next public form of the paper (not in the public one) | Lean |
|---|---|
| A next-token distribution; `KL(p ‖ q)`; `∑_i (√p_i − √q_i)²`; the softmax of a logit vector; a shift whose oscillation `e_i − e_j` is at most `w` | `IsDist`, `kl`, `hell`, `softmax`, `OscLe` |
| Thm 5 (a): `KL(p ‖ q) = log ∑_i p_i exp(e_i) − ∑_i p_i e_i` | `kl_softmax` (from `softmax_shift`) |
| Thm 5 (b): `KL(p ‖ q) ≤ w`, `≤ w²/8`, and `≤ ε²/2` when every `|e_i| ≤ ε` | `kl_softmax_le_osc`, `kl_softmax_le_osc_sq` (from `log_sum_exp_sub_le`), `kl_softmax_le_of_abs` |
| Thm 5 (c): `∑_i (√p_i − √q_i)² ≤ KL(p ‖ q)`, `(∑_i |p_i − q_i|)² ≤ 4 ∑_i (√p_i − √q_i)²`, `(∑_i |p_i − q_i|)² ≤ 4 KL(p ‖ q)` | `hell_le_kl`, `l1_sq_le_four_hell`, `l1_sq_le_four_kl`; also `kl_nonneg`, `kl_pos_of_ne`, `kl_self` |
| Thm 5, the numbers: `|e_i| ≤ 5e-4` gives a KL of at most `1.25e-7`; a KL above `1e-3` needs an oscillation above `0.089`; a KL of at least `1e-1` needs one above `0.894` | `control_floor`, `holds_threshold_needs_osc`, `degrades_threshold_needs_osc` |
| Thm 6 (a): the KL between the two distributions over texts of `T` tokens is the expectation, over a text drawn from the fresh reader, of the sum over positions of the per-token KL read on that text; the expectation of the mean per-token KL is that KL divided by `T` | `seqProb`, `kl_seqProb`, `seqProb_marginal`, `kl_seqProb_expect`, `meanKL_expect` |
| Thm 6 (b), the example on two tokens: the chain rule; equal first-token distributions and continuations that differ after one token `a` only give the probability of `a` times the KL after `a`, which is positive, while a text that starts with another token reads zero at both positions | `kl_prod`, `kl_prod_eq_single`, `kl_prod_pos_of_ne`, `kl_branch_zero`, `kl_pos_of_ne` |
| Thm 6 (c), texts that end early. Hypothesis of `kl_seqProb_stop` and of `meanKL_stop_bounds`: after a text has ended, the fresh and the reused reader continue with one common law (the tree `R` of `padTree ended P R` and `padTree ended Q R`). Under it, the same identity with the sum taken over the positions before the text's end. Under it and two more, that the empty text has not ended (`ended [] = false`) and that the limit is at least one token (`0 < T`): the expectation of the mean over the text's own length lies between the KL divided by `T` and the KL | `padTree`, `liveCount`, `liveSum`, `kl_seqProb_stop`, `meanKL_stop_bounds`; `liveCount_pos`, `liveCount_le`, `liveCount_of_live` |
| Remark after Thm 6: on 256 tokens, a mean per-token KL of at most `1e-3` leaves at most two positions that read `1e-1` or more | `card_ge_mul_le` (Markov), `holds_at_most_two` |
| Prop 7 (a): the greedy token is the argmax of the logits, and a shift whose oscillation is under the fresh logit margin leaves it unchanged; in contrapositive form, if a token leads every other by a margin in the fresh logits and another token is at least as large in the reused logits, that margin is at most any bound on the shift's oscillation | `softmax_lt_iff`, `softmax_le_iff`, `argmax_stable`, `argmax_stable_of_abs`; the contrapositive form is `flip_needs_osc`, in `PredMain.lean` |
| Prop 7 (b): a change of greedy token from `a` to `b` forces `KL(p ‖ q) ≥ (√p_a − √p_b)²/2` | `flip_forces_kl`, in `PredMain.lean` (from `flip_forces_hell`, in `PredFlip.lean`, and `hell_le_kl`, in `PredKL.lean`) |
| Prop 7 (c): for every `η > 0` there are two distributions with `KL(p ‖ q) ≤ η` and different greedy tokens | `near_tie_flip` |
| Prop 8 (a): two greedy runs under one stopping rule are equal exactly when the reused rule chooses the fresh rule's token at every prefix of the fresh run that has not ended | `genStop`, `genStop_eq_iff`; for runs of a fixed length `gen`, `gen_eq_iff` |
| Prop 8 (b), as far as the declaration states it: if the answers read off the two runs differ, there is a number of steps `t < T` after which the two runs hold one common text, which has not ended and has `t` tokens; that text followed by the fresh greedy token is a prefix of the fresh run, and followed by the reused greedy token a prefix of the reused run; the two tokens differ; the KL lower bound of Prop 7 (b) holds at that text; and any bound on the oscillation of the shift there is at least any margin by which the fresh token leads in the fresh logits. The declaration states neither that the two runs differ nor that this position is the first at which they differ; both follow from what it states | `answer_flip_stop` (from `answer_flip_first_divergence_stop`, `flip_forces_kl`, `flip_needs_osc`) |
| Prop 8 (c): over a set of problems, the answer flips are at most as many as the problems whose two runs differ | `flips_le_divergences` |

## Empirical scope

These proofs establish conditional mathematical statements. The numerical lemmas are
per-handoff statements; they do not establish that plotted medians are uniform token bounds,
that every handoff equals a reported median, or that a tolerance preserves generation quality
across configurations. The attention result holds the query fixed.

## Modeling choices

* `fstar` is Equation `eq:fstar` taken literally: deviations are sorted with `Tuple.sort`, and the
  least feasible `k` is `sInf {k | Feasible δ τ k}`. The key lemma `sum_first_sorted_le` (the sum
  of the `r` smallest deviations is at most the sum over any `r` tokens) links the sorted
  definition to arbitrary retained sets.
* Standing hypotheses match the paper's: `0 < n` (a handoff has a matched token), `0 ≤ δ`,
  `0 < τ`, `0 < s_{l,h}`. Theorem 1 is stated without `0 < s_{l,h}`. It also holds under Lean's
  `x / 0 = 0` convention, and with `0 < s_{l,h}` it is exactly the paper's statement.
* Theorem 1 is proved for any centering vector, so it holds verbatim for the centered `R²`.
* Assumption `ass:rope` models each `R_{j−i}` as a linear isometry equivalence of a real inner
  product space (one per key, which is more general than depending on `j − i` only). The YaRN
  temperature is absorbed into `‖q_i‖`, as the paper states.
* Attention is the causally masked softmax `softmax V`: weights are normalized over the visible
  keys `V` (`causalMask i` for the query at position `i`) and are zero elsewhere. Keys range over
  all `|R|` receiver positions, so the diffuse bound uses `c/|R|` and the full retained set,
  including positions after the query, exactly as stated. `c ≥ 0` is derived, not assumed.
* Corollary 3's near-seam set is the union of `m` per-seam windows of at most `w` matched tokens
  (`nearSet`). `posWindow` realises a window from receiver positions: distinct matched tokens sit
  at distinct positions, so the window `(σ, σ + w]` holds at most `w` of them.
* The mean-value theorem replaces the paper's integral of the softmax Jacobian; it yields the
  same bound with an explicit `ξ ∈ (0,1)`.

## Discrepancies found and fixed in the paper

This pass (2026-10-03):

* Theorem 1 used `μ` without defining it. The statement now defines `μ = n⁻¹ ∑_{t∈M} δ(t)`
  (`thm_identity`); Theorem 2 and Corollary 3 use the same `μ`.
* Corollary 3's converse assumed a bound for "every matched token farther than `w` from a seam".
  Read two-sidedly, that excludes up to `2mw` tokens and the proof's count `n − mw` fails. The
  statement now names the per-seam token sets as windows and quantifies over tokens outside them
  (`cor_seam_converse`).
* Assumption `ass:rope` divided by `√d` without saying what `d` is; it is now defined as the head
  dimension (`logit`).

Earlier pass (the *Carryover* draft):

* Proposition 4 used `μ^ret_{l,h}` without defining it; the statement now defines it as the mean
  of `δ_{l,h}` over the retained tokens.
* The "concentrated on one retained token" clause was vacuous for a softmax (all visible weights
  are positive); it became the general bound plus the `ε`-share version.
* Corollary 3's converse needed `δ' ≥ 0` and now states the threshold `n(δ' − τ) > mw δ'`.
* The proof of Corollary 3 wrote `(n − mw) δ_far` for the far tokens, which is only literal when
  `mw ≤ n`; it now counts the `a ≤ mw` near tokens and uses `δ_far ≤ δ_near`.
* The proof of Theorem 2 skipped the `f* = 1` case in the second lower bound and left the first
  case unjustified; both now say why the bound is at most `1`.

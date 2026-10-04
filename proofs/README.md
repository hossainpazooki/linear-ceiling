# Lean 4 formalization of the theory in *KV Cache Drift Across Handoffs in Long-Horizon Agents*

Machine-checked proofs of the theoretical content of the paper (earlier title: *Carryover*,
hence the namespace). It covers the registered statistic of ledger entry 0023 (the paper's
Equations `eq:delta` and `eq:fstar`), Theorem `thm:identity`, Theorem `thm:sandwich`, Corollary
`cor:seam`, Assumption `ass:rope`, Proposition `prop:attn` with its value remark, and the
reported numbers the theorems explain. Labels such as `thm:identity` refer to the paper's LaTeX
source, which lives in the authors' Overleaf project rather than in this repository.

`fstar` is the exact-criterion version of `f_star` in `src/linear_ceiling/e9_pertoken.py`: both
sort the deviations in descending order and take the least `k < n` whose remaining-token mean is
at most `τ`, else `1`. The implementation judges "at most `τ`" to a relative tolerance of `1e-9`
(plus `1e-15`) for float32 records; the theorems use the exact criterion, as the paper states.

Every file compiles against Mathlib with no `sorry`, no `admit` and no new axioms. The only
axioms used are Lean's three standard ones: `propext`, `Classical.choice` and `Quot.sound`
(`Audit.lean` prints them for all 52 headline results).

## Building

Toolchain: Lean `v4.34.0-rc2`, Mathlib `v4.34.0-rc2` (pinned in `lean-toolchain`,
`lakefile.toml` and `lake-manifest.json`). Install Lean with `elan`.

```sh
cd proofs
lake exe cache get          # downloads the prebuilt Mathlib into .lake/ (several GB)
lake build                  # checks every proof
lake env lean Audit.lean    # prints the axioms of every headline result
./check.sh                  # the same two steps without lake (see below)
```

`check.sh` compiles each module with `lean -o` in dependency order and then runs `Audit.lean`.
Use it where `lake` is unavailable: on one macOS machine (checked 2026-10-03), `lake` for this
toolchain exits with `SIGTRAP` (exit code 133) before doing any work, even for `lake --version`,
while `lean` runs normally. It needs the Mathlib build in `.lake/packages`, from
`lake exe cache get` or from another project with the same `lake-manifest.json`. The full run
took about 21 minutes there, almost all of it loading Mathlib. `.lake/` is git-ignored.

## Files

| File | Paper content |
|---|---|
| `Carryover/Fstar.lean` | Equation `eq:fstar` (literal, via sorting), `μ`, `p(τ)`, `β(d)`, `δ_max`; Theorem 1's core `f*(τ)=0 ↔ μ ≤ τ`; all of Theorem 2; the subset characterisation of the statistic |
| `Carryover/Identity.lean` | Equation `eq:delta`, `R²` with the centered denominator, Theorem 1 (`μ = 1 − R̄²` and the verdict clause, for `L` layers and `H` heads), the retained-mean exchange used in the proof of Proposition 4 |
| `Carryover/Seams.lean` | Corollary 3 (both directions), with the near-seam set built from `m` windows of at most `w` matched tokens, or from receiver positions |
| `Carryover/Attention.lean` | Assumption `ass:rope`, the causally masked softmax, its Jacobian / mean-value bound, Proposition 4 (logits, weights, diffuse, general, concentrated), the value remark |
| `Carryover/Numbers.lean` | The reported numbers that Theorems 1 and 2 explain (Tables 1, 2 and 6, the configuration bridge, the matched configuration comparison) |
| `Audit.lean` | `#print axioms` for every headline result |
| `check.sh` | Builds and audits with `lean` directly, for machines where `lake` is broken |

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

This pass (2026-10-03, marked in purple in the paper source):

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

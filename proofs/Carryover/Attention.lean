import Carryover.Fstar

/-!
# Assumption `ass:rope` and Proposition `prop:attn`: what the key deviation bounds

* `logit q R k d = ⟪q, R k⟫ / √d` is the rotary logit of Assumption `ass:rope`; `R` is an
  orthogonal map (a linear isometry equivalence) depending only on `j - i` and the schedule, and
  `d` is the head dimension.
* Keys are indexed by the `N = |R|` receiver positions. `softmax V z` is the attention of one
  query: it normalizes over the keys `V` the query can see and puts zero weight at masked
  positions. For the query at receiver position `i`, `V = causalMask i = {j | j ≤ i}`.
* The perturbation bound `‖a' - a‖₁ ≤ 2 sup_u ∑_j a_j(u)|e_j|` is proved through the softmax
  Jacobian and the mean value theorem (`softmax_l1_shift`).
* The diffuse, general (tail) and concentrated regimes, and the value remark. The retained set
  `Mret` is a set of receiver positions, so it may include positions after the query, as in the
  paper.
-/

namespace Carryover

open Finset Real

/-! ## The logit bound -/

section Norm

variable {E : Type*} [NormedAddCommGroup E]

/-- `‖v‖ = s √(‖v‖²/s²)`: the norm of a perturbation in units of the receiver's deviation. -/
lemma norm_eq_s_mul_sqrt {s : ℝ} (hs : 0 < s) (v : E) : ‖v‖ = s * √(‖v‖ ^ 2 / s ^ 2) := by
  rw [Real.sqrt_div' _ (sq_nonneg s), Real.sqrt_sq (norm_nonneg v), Real.sqrt_sq hs.le]
  field_simp

end Norm

section Logits

variable {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]

/-- Assumption `ass:rope`: `z_ij = q_iᵀ R_{j-i} k̃_j / √d`. -/
noncomputable def logit (q : E) (R : E ≃ₗᵢ[ℝ] E) (k : E) (d : ℕ) : ℝ :=
  inner ℝ q (R k) / √(d : ℝ)

lemma logit_sub (q : E) (R : E ≃ₗᵢ[ℝ] E) (k Δk : E) (d : ℕ) :
    logit q R (k + Δk) d - logit q R k d = inner ℝ q (R Δk) / √(d : ℝ) := by
  unfold logit
  rw [map_add, inner_add_right, add_div]
  ring

/-- Cauchy–Schwarz and orthogonality: `|Δz| ≤ ‖q‖ ‖Δk̃‖ / √d`, independent of the position and of
the rotary schedule. -/
theorem logit_shift_le_norm (q : E) (R : E ≃ₗᵢ[ℝ] E) (k Δk : E) (d : ℕ) :
    |logit q R (k + Δk) d - logit q R k d| ≤ ‖q‖ * ‖Δk‖ / √(d : ℝ) := by
  rw [logit_sub, abs_div, abs_of_nonneg (Real.sqrt_nonneg _)]
  have h := abs_real_inner_le_norm q (R Δk)
  rw [LinearIsometryEquiv.norm_map] at h
  exact div_le_div_of_nonneg_right h (Real.sqrt_nonneg _)

/-- **Proposition `prop:attn`, first claim.** `|Δz_ij| ≤ ‖q_i‖ s_{l,h} √(δ_{l,h}(j)/d)` with
`δ_{l,h}(j) = ‖Δk̃_j‖²/s²_{l,h}`. -/
theorem logit_shift_le (q : E) (R : E ≃ₗᵢ[ℝ] E) (k Δk : E) {s : ℝ} (hs : 0 < s) (d : ℕ) :
    |logit q R (k + Δk) d - logit q R k d| ≤ ‖q‖ * s * √((‖Δk‖ ^ 2 / s ^ 2) / d) := by
  refine (logit_shift_le_norm q R k Δk d).trans (le_of_eq ?_)
  calc ‖q‖ * ‖Δk‖ / √(d : ℝ) = ‖q‖ * (s * √(‖Δk‖ ^ 2 / s ^ 2)) / √(d : ℝ) := by
        rw [← norm_eq_s_mul_sqrt hs]
    _ = ‖q‖ * s * √((‖Δk‖ ^ 2 / s ^ 2) / d) := by
        rw [Real.sqrt_div' _ (Nat.cast_nonneg d)]; ring

end Logits

/-! ## Masked softmax and its perturbation bound -/

section Softmax

variable {N : ℕ}

/-- The attention weights of one query that sees the keys `V`:
`softmax V z j = exp z_j / ∑_{k ∈ V} exp z_k` for `j ∈ V`, and `0` at masked positions. -/
noncomputable def softmax (V : Finset (Fin N)) (z : Fin N → ℝ) (j : Fin N) : ℝ :=
  if j ∈ V then Real.exp (z j) / ∑ k ∈ V, Real.exp (z k) else 0

/-- The causal mask of the query at receiver position `i`: the keys at positions `j ≤ i`. -/
def causalMask (i : Fin N) : Finset (Fin N) := Finset.Iic i

lemma causalMask_nonempty (i : Fin N) : (causalMask i).Nonempty :=
  ⟨i, Finset.mem_Iic.mpr le_rfl⟩

lemma softmax_of_mem {V : Finset (Fin N)} (z : Fin N → ℝ) {j : Fin N} (hj : j ∈ V) :
    softmax V z j = Real.exp (z j) / ∑ k ∈ V, Real.exp (z k) := by simp [softmax, hj]

lemma softmax_of_not_mem {V : Finset (Fin N)} (z : Fin N → ℝ) {j : Fin N} (hj : j ∉ V) :
    softmax V z j = 0 := by simp [softmax, hj]

lemma sum_exp_pos {V : Finset (Fin N)} (hV : V.Nonempty) (z : Fin N → ℝ) :
    0 < ∑ k ∈ V, Real.exp (z k) :=
  Finset.sum_pos (fun _ _ => Real.exp_pos _) hV

lemma softmax_nonneg (V : Finset (Fin N)) (z : Fin N → ℝ) (j : Fin N) : 0 ≤ softmax V z j := by
  by_cases hj : j ∈ V
  · rw [softmax_of_mem z hj]
    exact div_nonneg (Real.exp_pos _).le (sum_exp_pos ⟨j, hj⟩ z).le
  · rw [softmax_of_not_mem z hj]

/-- A weighted sum against the attention weights only involves the visible keys. -/
lemma sum_softmax_mul (V : Finset (Fin N)) (z f : Fin N → ℝ) :
    ∑ k, softmax V z k * f k = (∑ k ∈ V, Real.exp (z k) * f k) / ∑ k ∈ V, Real.exp (z k) := by
  rw [← Finset.sum_subset (Finset.subset_univ V)
    (fun k _ hk => by rw [softmax_of_not_mem z hk, zero_mul]), Finset.sum_div]
  exact Finset.sum_congr rfl fun k hk => by rw [softmax_of_mem z hk]; ring

lemma sum_softmax {V : Finset (Fin N)} (hV : V.Nonempty) (z : Fin N → ℝ) :
    ∑ j, softmax V z j = 1 := by
  have h := sum_softmax_mul V z (fun _ => 1)
  simp only [mul_one] at h
  rw [h, div_self (sum_exp_pos hV z).ne']

lemma softmax_le_one (V : Finset (Fin N)) (z : Fin N → ℝ) (j : Fin N) : softmax V z j ≤ 1 := by
  by_cases hj : j ∈ V
  · have h := sum_softmax ⟨j, hj⟩ z
    have := Finset.single_le_sum (fun k _ => softmax_nonneg V z k) (mem_univ j)
    linarith
  · rw [softmax_of_not_mem z hj]; exact zero_le_one

/-- The path `u ↦ softmax V (z + u e)_j` has derivative `a_j (e_j - aᵀe)`: the softmax Jacobian
`diag(a) - a aᵀ` applied to `e`. At a masked position both sides are `0`. -/
lemma hasDerivAt_softmax_path (V : Finset (Fin N)) (z e : Fin N → ℝ) (j : Fin N) (s : ℝ) :
    HasDerivAt (fun s : ℝ => softmax V (z + s • e) j)
      (softmax V (z + s • e) j * (e j - ∑ k, softmax V (z + s • e) k * e k)) s := by
  by_cases hj : j ∈ V
  · have hlin : ∀ k : Fin N, HasDerivAt (fun s : ℝ => z k + s * e k) (e k) s := fun k => by
      simpa using ((hasDerivAt_id s).mul_const (e k)).const_add (z k)
    have hnum := (hlin j).exp
    have hden : HasDerivAt (fun s : ℝ => ∑ k ∈ V, Real.exp (z k + s * e k))
        (∑ k ∈ V, Real.exp (z k + s * e k) * e k) s :=
      HasDerivAt.fun_sum fun k _ => (hlin k).exp
    have hpos : (∑ k ∈ V, Real.exp (z k + s * e k)) ≠ 0 :=
      (Finset.sum_pos (fun _ _ => Real.exp_pos _) ⟨j, hj⟩).ne'
    have key : HasDerivAt (fun s : ℝ => Real.exp (z j + s * e j) / ∑ k ∈ V, Real.exp (z k + s * e k))
        ((Real.exp (z j + s * e j) * e j * ∑ k ∈ V, Real.exp (z k + s * e k)
          - Real.exp (z j + s * e j) * ∑ k ∈ V, Real.exp (z k + s * e k) * e k)
          / (∑ k ∈ V, Real.exp (z k + s * e k)) ^ 2) s := hnum.div hden hpos
    have hfun : (fun s : ℝ => softmax V (z + s • e) j) =
        fun s : ℝ => Real.exp (z j + s * e j) / ∑ k ∈ V, Real.exp (z k + s * e k) := by
      funext s; simp [softmax, hj]
    rw [hfun]
    refine key.congr_deriv ?_
    rw [sum_softmax_mul, softmax_of_mem _ hj]
    simp only [Pi.add_apply, Pi.smul_apply, smul_eq_mul]
    field_simp
  · have hconst : (fun s : ℝ => softmax V (z + s • e) j) = fun _ => 0 := by
      funext s; exact softmax_of_not_mem _ hj
    rw [hconst, softmax_of_not_mem _ hj, zero_mul]
    exact hasDerivAt_const s 0

/-- **Softmax perturbation bound.** For some `ξ ∈ (0,1)`,
`‖softmax(z+e) - softmax z‖₁ ≤ 2 ∑_j softmax(z + ξ e)_j |e_j|`. -/
theorem softmax_l1_shift {V : Finset (Fin N)} (hV : V.Nonempty) (z e : Fin N → ℝ) :
    ∃ ξ ∈ Set.Ioo (0 : ℝ) 1,
      ∑ j, |softmax V (z + e) j - softmax V z j| ≤ 2 * ∑ j, softmax V (z + ξ • e) j * |e j| := by
  let σ : Fin N → ℝ := fun j => if 0 ≤ softmax V (z + e) j - softmax V z j then 1 else -1
  let φ : ℝ → ℝ := fun s => ∑ j, σ j * softmax V (z + s • e) j
  let φ' : ℝ → ℝ := fun s =>
    ∑ j, σ j * (softmax V (z + s • e) j * (e j - ∑ k, softmax V (z + s • e) k * e k))
  have hderiv : ∀ s, HasDerivAt φ (φ' s) s := fun s =>
    HasDerivAt.fun_sum fun j _ => (hasDerivAt_softmax_path V z e j s).const_mul (σ j)
  have hcont : ContinuousOn φ (Set.Icc 0 1) := fun s _ =>
    (hderiv s).continuousAt.continuousWithinAt
  obtain ⟨ξ, hξ, hslope⟩ :=
    exists_hasDerivAt_eq_slope φ φ' zero_lt_one hcont (fun s _ => hderiv s)
  refine ⟨ξ, hξ, ?_⟩
  have hσ : ∀ j, |σ j| = 1 := fun j => by
    simp only [σ]; split_ifs <;> simp
  have h10 : φ 1 - φ 0 = ∑ j, |softmax V (z + e) j - softmax V z j| := by
    simp only [φ, one_smul, zero_smul, add_zero, ← Finset.sum_sub_distrib]
    refine Finset.sum_congr rfl fun j _ => ?_
    rw [← mul_sub]
    simp only [σ]
    split_ifs with h
    · rw [one_mul, abs_of_nonneg h]
    · rw [neg_one_mul, abs_of_neg (not_le.mp h)]
  have hsum1 : ∑ j, softmax V (z + ξ • e) j = 1 := sum_softmax hV _
  set m := ∑ k, softmax V (z + ξ • e) k * e k with hm_def
  have hm : |m| ≤ ∑ k, softmax V (z + ξ • e) k * |e k| := by
    refine (Finset.abs_sum_le_sum_abs _ _).trans (le_of_eq ?_)
    refine Finset.sum_congr rfl fun k _ => ?_
    rw [abs_mul, abs_of_nonneg (softmax_nonneg _ _ _)]
  have hterm : ∀ j, σ j * (softmax V (z + ξ • e) j * (e j - m))
      ≤ softmax V (z + ξ • e) j * |e j| + softmax V (z + ξ • e) j * |m| := by
    intro j
    have ha := softmax_nonneg V (z + ξ • e) j
    have habs : |e j - m| ≤ |e j| + |m| := by
      rw [abs_le]
      constructor <;> linarith [le_abs_self (e j), neg_abs_le (e j), le_abs_self m, neg_abs_le m]
    calc σ j * (softmax V (z + ξ • e) j * (e j - m))
        ≤ |σ j * (softmax V (z + ξ • e) j * (e j - m))| := le_abs_self _
      _ = softmax V (z + ξ • e) j * |e j - m| := by
          rw [abs_mul, hσ, one_mul, abs_mul, abs_of_nonneg ha]
      _ ≤ softmax V (z + ξ • e) j * (|e j| + |m|) := mul_le_mul_of_nonneg_left habs ha
      _ = _ := by ring
  have hφ' : φ' ξ ≤ 2 * ∑ j, softmax V (z + ξ • e) j * |e j| := by
    calc φ' ξ = ∑ j, σ j * (softmax V (z + ξ • e) j * (e j - m)) := rfl
      _ ≤ ∑ j, (softmax V (z + ξ • e) j * |e j| + softmax V (z + ξ • e) j * |m|) :=
          Finset.sum_le_sum fun j _ => hterm j
      _ = ∑ j, softmax V (z + ξ • e) j * |e j| + (∑ j, softmax V (z + ξ • e) j) * |m| := by
          rw [Finset.sum_add_distrib, Finset.sum_mul]
      _ ≤ ∑ j, softmax V (z + ξ • e) j * |e j| + 1 * ∑ k, softmax V (z + ξ • e) k * |e k| := by
          rw [hsum1]; linarith
      _ = 2 * ∑ j, softmax V (z + ξ • e) j * |e j| := by ring
  rw [sub_zero, div_one] at hslope
  linarith [h10, hslope, hφ']

/-- The bound with any uniform majorant `B` of `∑_j a_j(u)|e_j|` on `[0,1]`. -/
theorem softmax_l1_shift_le {V : Finset (Fin N)} (hV : V.Nonempty) (z e : Fin N → ℝ) {B : ℝ}
    (hB : ∀ s ∈ Set.Icc (0 : ℝ) 1, ∑ j, softmax V (z + s • e) j * |e j| ≤ B) :
    ∑ j, |softmax V (z + e) j - softmax V z j| ≤ 2 * B := by
  obtain ⟨ξ, hξ, h⟩ := softmax_l1_shift hV z e
  have := hB ξ ⟨hξ.1.le, hξ.2.le⟩
  linarith

/-- The bound with the supremum over `u ∈ [0,1]`, as written in the proposition. -/
theorem softmax_l1_shift_iSup {V : Finset (Fin N)} (hV : V.Nonempty) (z e : Fin N → ℝ) :
    ∑ j, |softmax V (z + e) j - softmax V z j|
      ≤ 2 * ⨆ s : Set.Icc (0 : ℝ) 1, ∑ j, softmax V (z + (s : ℝ) • e) j * |e j| := by
  have hbdd : BddAbove (Set.range fun s : Set.Icc (0 : ℝ) 1 =>
      ∑ j, softmax V (z + (s : ℝ) • e) j * |e j|) := by
    refine ⟨∑ j, |e j|, ?_⟩
    rintro _ ⟨s, rfl⟩
    exact Finset.sum_le_sum fun j _ =>
      mul_le_of_le_one_left (abs_nonneg _) (softmax_le_one _ _ _)
  exact softmax_l1_shift_le hV z e fun s hs => le_ciSup hbdd ⟨s, hs⟩

/-! ### The three attention regimes, as inequalities on weights -/

/-- **Diffuse attention.** If `a_j ≤ c/N` on the retained set and `e` vanishes off it, with
`|e_j| ≤ K √(g_j)`, then `∑_j a_j |e_j| ≤ c K √(mean_{Mret} g)` (Jensen for `√` over the `N`
positions, then `|Mret| ≤ N`). -/
theorem diffuse_bound (a e g : Fin N → ℝ) (hg : ∀ j, 0 ≤ g j)
    (Mret : Finset (Fin N)) (he : ∀ j ∉ Mret, e j = 0) {c K : ℝ} (hc : 0 ≤ c) (hK : 0 ≤ K)
    (hdiff : ∀ j ∈ Mret, a j ≤ c / N) (heg : ∀ j ∈ Mret, |e j| ≤ K * √(g j)) :
    ∑ j, a j * |e j| ≤ c * K * √((∑ j ∈ Mret, g j) / Mret.card) := by
  have h1 : ∑ j, a j * |e j| = ∑ j ∈ Mret, a j * |e j| :=
    (Finset.sum_subset (Finset.subset_univ Mret) (fun j _ hj => by simp [he j hj])).symm
  have h2 : ∑ j ∈ Mret, a j * |e j| ≤ c / N * K * ∑ j ∈ Mret, √(g j) := by
    rw [Finset.mul_sum]
    refine Finset.sum_le_sum fun j hj => ?_
    calc a j * |e j| ≤ (c / N) * (K * √(g j)) :=
          mul_le_mul (hdiff j hj) (heg j hj) (abs_nonneg _) (by positivity)
      _ = c / N * K * √(g j) := by ring
  have h3 : (∑ j ∈ Mret, √(g j)) ^ 2 ≤ Mret.card * ∑ j ∈ Mret, g j := by
    have := Finset.sum_mul_sq_le_sq_mul_sq Mret (fun _ => (1 : ℝ)) (fun j => √(g j))
    have e1 : ∑ j ∈ Mret, (1 : ℝ) * √(g j) = ∑ j ∈ Mret, √(g j) := by simp
    have e2 : ∑ _j ∈ Mret, ((1 : ℝ)) ^ 2 = Mret.card := by simp
    have e3 : ∑ j ∈ Mret, (√(g j)) ^ 2 = ∑ j ∈ Mret, g j :=
      Finset.sum_congr rfl fun j _ => Real.sq_sqrt (hg j)
    rw [e1, e2, e3] at this
    exact this
  have h4 : (∑ j ∈ Mret, √(g j)) / N ≤ √((∑ j ∈ Mret, g j) / Mret.card) := by
    rcases Mret.eq_empty_or_nonempty with hM | hM
    · simp [hM]
    · have hMpos : (0 : ℝ) < Mret.card := by exact_mod_cast Finset.card_pos.mpr hM
      have hMN : (Mret.card : ℝ) ≤ N := by
        exact_mod_cast (Finset.card_le_univ Mret).trans_eq (Fintype.card_fin N)
      have hsg : 0 ≤ ∑ j ∈ Mret, g j := Finset.sum_nonneg fun j _ => hg j
      have hs0 : 0 ≤ ∑ j ∈ Mret, √(g j) := Finset.sum_nonneg fun j _ => Real.sqrt_nonneg _
      have hNpos : (0 : ℝ) < N := lt_of_lt_of_le hMpos hMN
      rw [Real.le_sqrt (div_nonneg hs0 (Nat.cast_nonneg N)) (div_nonneg hsg (Nat.cast_nonneg _)),
        div_pow, div_le_div_iff₀ (pow_pos hNpos 2) hMpos]
      nlinarith [h3, hMpos, hMN, hsg, mul_le_mul hMN hMN hMpos.le (by positivity)]
  calc ∑ j, a j * |e j| = ∑ j ∈ Mret, a j * |e j| := h1
    _ ≤ c / N * K * ∑ j ∈ Mret, √(g j) := h2
    _ = c * K * ((∑ j ∈ Mret, √(g j)) / N) := by ring
    _ ≤ c * K * √((∑ j ∈ Mret, g j) / Mret.card) :=
        mul_le_mul_of_nonneg_left h4 (by positivity)

/-- **General (tail) regime.** With weights summing to one, `∑_j a_j |e_j| ≤ max_j |e_j|`. -/
theorem weighted_le_max (a e : Fin N → ℝ) (ha : ∀ j, 0 ≤ a j) (hsum : ∑ j, a j = 1) {Emax : ℝ}
    (hE : ∀ j, |e j| ≤ Emax) : ∑ j, a j * |e j| ≤ Emax := by
  calc ∑ j, a j * |e j| ≤ ∑ j, a j * Emax :=
        Finset.sum_le_sum fun j _ => mul_le_mul_of_nonneg_left (hE j) (ha j)
    _ = Emax := by rw [← Finset.sum_mul, hsum, one_mul]

/-- **Concentrated attention.** If all but an `ε` share of the weight sits on one token `j₀`,
then `∑_j a_j |e_j| ≤ |e_{j₀}| + ε max_j |e_j|`. -/
theorem concentrated_bound (a e : Fin N → ℝ) (ha : ∀ j, 0 ≤ a j) (hsum : ∑ j, a j = 1)
    (j0 : Fin N) {ε Emax : ℝ} (hε : ∑ j ∈ univ.erase j0, a j ≤ ε) (hE : ∀ j, |e j| ≤ Emax) :
    ∑ j, a j * |e j| ≤ |e j0| + ε * Emax := by
  rw [← Finset.add_sum_erase _ _ (mem_univ j0)]
  have hE0 : 0 ≤ Emax := (abs_nonneg _).trans (hE j0)
  have ha0 : a j0 ≤ 1 := by
    rw [← hsum]; exact Finset.single_le_sum (fun j _ => ha j) (mem_univ j0)
  have h1 : a j0 * |e j0| ≤ |e j0| := mul_le_of_le_one_left (abs_nonneg _) ha0
  have h2 : ∑ j ∈ univ.erase j0, a j * |e j| ≤ ε * Emax := by
    calc ∑ j ∈ univ.erase j0, a j * |e j| ≤ ∑ j ∈ univ.erase j0, a j * Emax :=
          Finset.sum_le_sum fun j _ => mul_le_mul_of_nonneg_left (hE j) (ha j)
      _ = (∑ j ∈ univ.erase j0, a j) * Emax := by rw [Finset.sum_mul]
      _ ≤ ε * Emax := mul_le_mul_of_nonneg_right hε hE0
  linarith

end Softmax

/-! ## Proposition `prop:attn` assembled -/

section Proposition

variable {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E] {N : ℕ}

/-- Logits of one query against the `N = |R|` receiver positions under Assumption `ass:rope`. -/
noncomputable def logits (q : E) (R : Fin N → E ≃ₗᵢ[ℝ] E) (k : Fin N → E) (d : ℕ) : Fin N → ℝ :=
  fun j => logit q (R j) (k j) d

/-- `Δz_ij`: the logit shift from replacing the fresh content-space keys `k` by `k + Δk`. -/
noncomputable def deltaZ (q : E) (R : Fin N → E ≃ₗᵢ[ℝ] E) (k Δk : Fin N → E) (d : ℕ) :
    Fin N → ℝ :=
  fun j => logits q R (fun j => k j + Δk j) d j - logits q R k d j

lemma logits_pert (q : E) (R : Fin N → E ≃ₗᵢ[ℝ] E) (k Δk : Fin N → E) (d : ℕ) :
    logits q R (fun j => k j + Δk j) d = logits q R k d + deltaZ q R k Δk d := by
  funext j; simp [deltaZ]

/-- Unmatched tokens and tokens the oracle repairs have `Δk̃_j = 0`, hence `Δz_ij = 0`. -/
lemma deltaZ_eq_zero (q : E) (R : Fin N → E ≃ₗᵢ[ℝ] E) (k Δk : Fin N → E) (d : ℕ) {j : Fin N}
    (h : Δk j = 0) : deltaZ q R k Δk d j = 0 := by
  simp [deltaZ, logits, h]

/-- **Proposition `prop:attn`, logits.** `|Δz_ij| ≤ ‖q_i‖ s √(δ(j)/d)` for every `i` and `j`. -/
theorem abs_deltaZ_le (q : E) (R : Fin N → E ≃ₗᵢ[ℝ] E) (k Δk : Fin N → E) {s : ℝ} (hs : 0 < s)
    (d : ℕ) (j : Fin N) :
    |deltaZ q R k Δk d j| ≤ ‖q‖ * s * √((‖Δk j‖ ^ 2 / s ^ 2) / d) :=
  logit_shift_le q (R j) (k j) (Δk j) hs d

/-- **Proposition `prop:attn`, weights.** `‖a_i' - a_i‖₁ ≤ 2 ∑_j a_ij(ξ) |Δz_ij|` for some
`ξ ∈ (0,1)`. -/
theorem prop_attn_weights (V : Finset (Fin N)) (hV : V.Nonempty) (q : E)
    (R : Fin N → E ≃ₗᵢ[ℝ] E) (k Δk : Fin N → E) (d : ℕ) :
    ∃ ξ ∈ Set.Ioo (0 : ℝ) 1,
      ∑ j, |softmax V (logits q R (fun j => k j + Δk j) d) j - softmax V (logits q R k d) j|
        ≤ 2 * ∑ j, softmax V (logits q R k d + ξ • deltaZ q R k Δk d) j
            * |deltaZ q R k Δk d j| := by
  rw [logits_pert]
  exact softmax_l1_shift hV _ _

/-- **Proposition `prop:attn`, weights, supremum form** (`‖a_i'-a_i‖₁ ≤ 2 sup_u ∑_j a_ij(u)|Δz_ij|`). -/
theorem prop_attn_weights_iSup (V : Finset (Fin N)) (hV : V.Nonempty) (q : E)
    (R : Fin N → E ≃ₗᵢ[ℝ] E) (k Δk : Fin N → E) (d : ℕ) :
    ∑ j, |softmax V (logits q R (fun j => k j + Δk j) d) j - softmax V (logits q R k d) j|
      ≤ 2 * ⨆ s : Set.Icc (0 : ℝ) 1,
          ∑ j, softmax V (logits q R k d + (s : ℝ) • deltaZ q R k Δk d) j
            * |deltaZ q R k Δk d j| := by
  rw [logits_pert]
  exact softmax_l1_shift_iSup hV _ _

/-- **Proposition `prop:attn`, diffuse case.** Keys are the `N = |R|` receiver positions and the
query sees `V`. If `a_ij(u) ≤ c/|R|` for every retained matched token `j` and every `u ∈ [0,1]`,
with `Δk̃ = 0` off the retained set `Mret`, then `‖a_i' - a_i‖₁ ≤ 2 c ‖q_i‖ s √(μ^ret/d)`, where
`μ^ret` is the mean of `δ_{l,h}` over the full retained set (which may include positions the query
cannot see). `c ≥ 0` is not assumed: it follows from the hypothesis at any retained token. -/
theorem prop_attn_diffuse (V : Finset (Fin N)) (hV : V.Nonempty) (q : E)
    (R : Fin N → E ≃ₗᵢ[ℝ] E) (k Δk : Fin N → E) {s : ℝ} (hs : 0 < s) (d : ℕ)
    (Mret : Finset (Fin N)) (hM : Mret.Nonempty) (hΔ : ∀ j ∉ Mret, Δk j = 0) {c : ℝ}
    (hdiff : ∀ u ∈ Set.Icc (0 : ℝ) 1, ∀ j ∈ Mret,
      softmax V (logits q R k d + u • deltaZ q R k Δk d) j ≤ c / N) :
    ∑ j, |softmax V (logits q R (fun j => k j + Δk j) d) j - softmax V (logits q R k d) j|
      ≤ 2 * c * ‖q‖ * s * √(((∑ j ∈ Mret, ‖Δk j‖ ^ 2 / s ^ 2) / Mret.card) / d) := by
  have hc : 0 ≤ c := by
    obtain ⟨j0, hj0⟩ := hM
    have h1 := hdiff 0 ⟨le_rfl, zero_le_one⟩ j0 hj0
    have h0 := softmax_nonneg V (logits q R k d + (0 : ℝ) • deltaZ q R k Δk d) j0
    have hN : (0 : ℝ) < N := by exact_mod_cast Fin.pos j0
    by_contra hneg
    have : c / N < 0 := div_neg_of_neg_of_pos (lt_of_not_ge hneg) hN
    linarith
  obtain ⟨ξ, hξ, hshift⟩ := prop_attn_weights V hV q R k Δk d
  have hK : 0 ≤ ‖q‖ * s / √(d : ℝ) := by positivity
  have heg : ∀ j ∈ Mret, |deltaZ q R k Δk d j|
      ≤ (‖q‖ * s / √(d : ℝ)) * √(‖Δk j‖ ^ 2 / s ^ 2) := by
    intro j _
    refine (abs_deltaZ_le q R k Δk hs d j).trans (le_of_eq ?_)
    rw [Real.sqrt_div' _ (Nat.cast_nonneg d)]; ring
  have he0 : ∀ j ∉ Mret, deltaZ q R k Δk d j = 0 := fun j hj =>
    deltaZ_eq_zero q R k Δk d (hΔ j hj)
  have hdb := diffuse_bound (softmax V (logits q R k d + ξ • deltaZ q R k Δk d))
    (deltaZ q R k Δk d) (fun j => ‖Δk j‖ ^ 2 / s ^ 2)
    (fun j => by positivity) Mret he0 hc hK (hdiff ξ ⟨hξ.1.le, hξ.2.le⟩) heg
  calc _ ≤ _ := hshift
    _ ≤ 2 * (c * (‖q‖ * s / √(d : ℝ)) * √((∑ j ∈ Mret, ‖Δk j‖ ^ 2 / s ^ 2) / Mret.card)) := by
        linarith
    _ = 2 * c * ‖q‖ * s * √(((∑ j ∈ Mret, ‖Δk j‖ ^ 2 / s ^ 2) / Mret.card) / d) := by
        rw [Real.sqrt_div' _ (Nat.cast_nonneg d)]; ring

/-- The diffuse case for the causal mask of the query at receiver position `i`, with the retained
set allowed to contain positions after `i`. -/
theorem prop_attn_diffuse_causal (i : Fin N) (q : E) (R : Fin N → E ≃ₗᵢ[ℝ] E)
    (k Δk : Fin N → E) {s : ℝ} (hs : 0 < s) (d : ℕ)
    (Mret : Finset (Fin N)) (hM : Mret.Nonempty) (hΔ : ∀ j ∉ Mret, Δk j = 0) {c : ℝ}
    (hdiff : ∀ u ∈ Set.Icc (0 : ℝ) 1, ∀ j ∈ Mret,
      softmax (causalMask i) (logits q R k d + u • deltaZ q R k Δk d) j ≤ c / N) :
    ∑ j, |softmax (causalMask i) (logits q R (fun j => k j + Δk j) d) j
        - softmax (causalMask i) (logits q R k d) j|
      ≤ 2 * c * ‖q‖ * s * √(((∑ j ∈ Mret, ‖Δk j‖ ^ 2 / s ^ 2) / Mret.card) / d) :=
  prop_attn_diffuse (causalMask i) (causalMask_nonempty i) q R k Δk hs d Mret hM hΔ hdiff

/-- `δ^max_{l,h}`, the largest retained deviation. -/
noncomputable def retMax (Mret : Finset (Fin N)) (hM : Mret.Nonempty) (Δk : Fin N → E) (s : ℝ) :
    ℝ :=
  Mret.sup' hM fun j => ‖Δk j‖ ^ 2 / s ^ 2

omit [InnerProductSpace ℝ E] in
/-- Every deviation is at most `δ^max`, because deviations vanish off the retained set. -/
lemma dev_le_retMax (Mret : Finset (Fin N)) (hM : Mret.Nonempty) (Δk : Fin N → E) (s : ℝ)
    (hΔ : ∀ j ∉ Mret, Δk j = 0) (j : Fin N) : ‖Δk j‖ ^ 2 / s ^ 2 ≤ retMax Mret hM Δk s := by
  by_cases hj : j ∈ Mret
  · exact Finset.le_sup' (fun j => ‖Δk j‖ ^ 2 / s ^ 2) hj
  · obtain ⟨j0, hj0⟩ := hM
    rw [hΔ j hj, norm_zero]
    calc (0 : ℝ) ^ 2 / s ^ 2 = 0 := by simp
      _ ≤ ‖Δk j0‖ ^ 2 / s ^ 2 := by positivity
      _ ≤ retMax Mret ⟨j0, hj0⟩ Δk s := Finset.le_sup' (fun j => ‖Δk j‖ ^ 2 / s ^ 2) hj0

/-- **Proposition `prop:attn`, general bound**, with any upper bound `Dmax` on the deviations. -/
theorem prop_attn_tail (V : Finset (Fin N)) (hV : V.Nonempty) (q : E)
    (R : Fin N → E ≃ₗᵢ[ℝ] E) (k Δk : Fin N → E) {s : ℝ} (hs : 0 < s) (d : ℕ) {Dmax : ℝ}
    (hDmax : ∀ j, ‖Δk j‖ ^ 2 / s ^ 2 ≤ Dmax) :
    ∑ j, |softmax V (logits q R (fun j => k j + Δk j) d) j - softmax V (logits q R k d) j|
      ≤ 2 * (‖q‖ * s * √(Dmax / d)) := by
  obtain ⟨ξ, hξ, hshift⟩ := prop_attn_weights V hV q R k Δk d
  have hE : ∀ j, |deltaZ q R k Δk d j| ≤ ‖q‖ * s * √(Dmax / d) := fun j =>
    (abs_deltaZ_le q R k Δk hs d j).trans (by gcongr; exact hDmax j)
  have := weighted_le_max (softmax V (logits q R k d + ξ • deltaZ q R k Δk d))
    (deltaZ q R k Δk d) (softmax_nonneg _ _) (sum_softmax hV _) hE
  linarith

/-- **Proposition `prop:attn`, general bound, as stated**: `‖a_i' - a_i‖₁ ≤ 2 ‖q_i‖ s √(δ^max/d)`
with `δ^max` the largest retained deviation. -/
theorem prop_attn_tail_ret (V : Finset (Fin N)) (hV : V.Nonempty) (q : E)
    (R : Fin N → E ≃ₗᵢ[ℝ] E) (k Δk : Fin N → E) {s : ℝ} (hs : 0 < s) (d : ℕ)
    (Mret : Finset (Fin N)) (hM : Mret.Nonempty) (hΔ : ∀ j ∉ Mret, Δk j = 0) :
    ∑ j, |softmax V (logits q R (fun j => k j + Δk j) d) j - softmax V (logits q R k d) j|
      ≤ 2 * (‖q‖ * s * √(retMax Mret hM Δk s / d)) :=
  prop_attn_tail V hV q R k Δk hs d (dev_le_retMax Mret hM Δk s hΔ)

/-- **Proposition `prop:attn`, concentrated case.** If all but an `ε` share of `a_i(u)` sits on one
token `j₀` for every `u ∈ [0,1]`, then
`‖a_i' - a_i‖₁ ≤ 2 ‖q_i‖ s (√(δ(j₀)/d) + ε √(Dmax/d))`. -/
theorem prop_attn_concentrated (V : Finset (Fin N)) (hV : V.Nonempty) (q : E)
    (R : Fin N → E ≃ₗᵢ[ℝ] E) (k Δk : Fin N → E) {s : ℝ} (hs : 0 < s) (d : ℕ) (j0 : Fin N)
    {ε Dmax : ℝ}
    (hconc : ∀ u ∈ Set.Icc (0 : ℝ) 1,
      ∑ j ∈ univ.erase j0, softmax V (logits q R k d + u • deltaZ q R k Δk d) j ≤ ε)
    (hDmax : ∀ j, ‖Δk j‖ ^ 2 / s ^ 2 ≤ Dmax) :
    ∑ j, |softmax V (logits q R (fun j => k j + Δk j) d) j - softmax V (logits q R k d) j|
      ≤ 2 * (‖q‖ * s * √((‖Δk j0‖ ^ 2 / s ^ 2) / d) + ε * (‖q‖ * s * √(Dmax / d))) := by
  obtain ⟨ξ, hξ, hshift⟩ := prop_attn_weights V hV q R k Δk d
  have hE : ∀ j, |deltaZ q R k Δk d j| ≤ ‖q‖ * s * √(Dmax / d) := fun j =>
    (abs_deltaZ_le q R k Δk hs d j).trans (by gcongr; exact hDmax j)
  have hcb := concentrated_bound (softmax V (logits q R k d + ξ • deltaZ q R k Δk d))
    (deltaZ q R k Δk d) (softmax_nonneg _ _) (sum_softmax hV _) j0
    (hconc ξ ⟨hξ.1.le, hξ.2.le⟩) hE
  have hj0 := abs_deltaZ_le q R k Δk hs d j0
  linarith

/-- **Proposition `prop:attn`, concentrated case, as stated**, with `δ^max` the largest retained
deviation. -/
theorem prop_attn_concentrated_ret (V : Finset (Fin N)) (hV : V.Nonempty) (q : E)
    (R : Fin N → E ≃ₗᵢ[ℝ] E) (k Δk : Fin N → E) {s : ℝ} (hs : 0 < s) (d : ℕ)
    (Mret : Finset (Fin N)) (hM : Mret.Nonempty) (hΔ : ∀ j ∉ Mret, Δk j = 0) (j0 : Fin N)
    {ε : ℝ}
    (hconc : ∀ u ∈ Set.Icc (0 : ℝ) 1,
      ∑ j ∈ univ.erase j0, softmax V (logits q R k d + u • deltaZ q R k Δk d) j ≤ ε) :
    ∑ j, |softmax V (logits q R (fun j => k j + Δk j) d) j - softmax V (logits q R k d) j|
      ≤ 2 * (‖q‖ * s * √((‖Δk j0‖ ^ 2 / s ^ 2) / d)
          + ε * (‖q‖ * s * √(retMax Mret hM Δk s / d))) :=
  prop_attn_concentrated V hV q R k Δk hs d j0 hconc (dev_le_retMax Mret hM Δk s hΔ)

/-! ## The value remark -/

/-- **Remark after Proposition `prop:attn`.** With `o_i = ∑_j a_ij v_j` and the perturbed
`o_i' = ∑_j a_ij' (v_j + Δv_j)`,
`‖o_i' - o_i‖ ≤ ‖a_i' - a_i‖₁ max_j ‖v_j‖ + ∑_j a_ij' ‖Δv_j‖`. -/
theorem value_shift_le {F : Type*} [NormedAddCommGroup F] [NormedSpace ℝ F]
    (a a' : Fin N → ℝ) (ha' : ∀ j, 0 ≤ a' j) (v Δv : Fin N → F) {V : ℝ}
    (hV : ∀ j, ‖v j‖ ≤ V) :
    ‖∑ j, a' j • (v j + Δv j) - ∑ j, a j • v j‖
      ≤ (∑ j, |a' j - a j|) * V + ∑ j, a' j * ‖Δv j‖ := by
  have heq : ∑ j, a' j • (v j + Δv j) - ∑ j, a j • v j
      = ∑ j, (a' j - a j) • v j + ∑ j, a' j • Δv j := by
    simp only [smul_add, sub_smul, Finset.sum_add_distrib, Finset.sum_sub_distrib]
    abel
  rw [heq]
  refine (norm_add_le _ _).trans (add_le_add ?_ ?_)
  · refine (norm_sum_le _ _).trans ?_
    rw [Finset.sum_mul]
    refine Finset.sum_le_sum fun j _ => ?_
    rw [norm_smul, Real.norm_eq_abs]
    exact mul_le_mul_of_nonneg_left (hV j) (abs_nonneg _)
  · refine (norm_sum_le _ _).trans ?_
    refine Finset.sum_le_sum fun j _ => ?_
    rw [norm_smul, Real.norm_eq_abs, abs_of_nonneg (ha' j)]

/-- `‖Δv_j‖ = s^V √(δ^V(j))`, Equation `eq:delta` applied to the value read-out. -/
theorem norm_deltaV_eq {F : Type*} [NormedAddCommGroup F]
    {sV : ℝ} (hs : 0 < sV) (Δv : F) : ‖Δv‖ = sV * √(‖Δv‖ ^ 2 / sV ^ 2) :=
  norm_eq_s_mul_sqrt hs Δv

end Proposition

end Carryover

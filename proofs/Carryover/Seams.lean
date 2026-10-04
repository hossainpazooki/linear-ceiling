import Carryover.Fstar

/-!
# Corollary 3: long context with a fixed number of seams

`Near` is the set of matched tokens within `w` positions after one of the `m` seams, so
`|Near| ≤ m w`. Tokens in `Near` deviate by at most `δ_near`, all others by at most `δ_far`.
-/

namespace Carryover

open Finset

variable {n : ℕ}

lemma card_compl_eq (Near : Finset (Fin n)) :
    ((univ \ Near).card : ℝ) = n - Near.card := by
  have hNn : Near.card ≤ n := (Finset.card_le_univ _).trans (by simp)
  rw [Finset.card_univ_sdiff, Fintype.card_fin, Nat.cast_sub hNn]

/-- **Corollary 3, upper bound.** `μ ≤ δ_far + (mw/n)(δ_near - δ_far)`. -/
theorem seam_mean_le (hn : 0 < n) (δ : Fin n → ℝ) (Near : Finset (Fin n)) (m w : ℕ)
    (hN : Near.card ≤ m * w) {δnear δfar : ℝ} (hfn : δfar ≤ δnear)
    (hnear : ∀ t ∈ Near, δ t ≤ δnear) (hfar : ∀ t ∉ Near, δ t ≤ δfar) :
    mu δ ≤ δfar + ((m * w : ℕ) : ℝ) / n * (δnear - δfar) := by
  have hn' : (0 : ℝ) < n := by exact_mod_cast hn
  have hsplit : ∑ i, δ i = ∑ i ∈ Near, δ i + ∑ i ∈ univ \ Near, δ i := by
    rw [add_comm, Finset.sum_sdiff (Finset.subset_univ Near)]
  have h1 : ∑ i ∈ Near, δ i ≤ Near.card * δnear := by
    have := Finset.sum_le_card_nsmul Near δ δnear hnear
    simpa [nsmul_eq_mul] using this
  have h2 : ∑ i ∈ univ \ Near, δ i ≤ ((n : ℝ) - Near.card) * δfar := by
    have := Finset.sum_le_card_nsmul (univ \ Near) δ δfar
      (fun t ht => hfar t (Finset.mem_sdiff.mp ht).2)
    simp only [nsmul_eq_mul] at this
    rwa [card_compl_eq] at this
  have hNmw : (Near.card : ℝ) ≤ ((m * w : ℕ) : ℝ) := by exact_mod_cast hN
  have hprod : (Near.card : ℝ) * (δnear - δfar) ≤ ((m * w : ℕ) : ℝ) * (δnear - δfar) :=
    mul_le_mul_of_nonneg_right hNmw (sub_nonneg.mpr hfn)
  have hexp : ((m * w : ℕ) : ℝ) / n * (δnear - δfar) * n = ((m * w : ℕ) : ℝ) * (δnear - δfar) := by
    rw [div_mul_eq_mul_div, div_mul_cancel₀ _ hn'.ne']
  unfold mu
  rw [div_le_iff₀ hn', add_mul, hexp]
  linarith [h1, h2, hsplit, hprod]

/-- **Corollary 3, first consequence.** The floor is zero whenever the bound is within `τ`. -/
theorem seam_zero_floor (hn : 0 < n) (δ : Fin n → ℝ) (Near : Finset (Fin n)) (m w : ℕ)
    (hN : Near.card ≤ m * w) {δnear δfar τ : ℝ} (hfn : δfar ≤ δnear)
    (hnear : ∀ t ∈ Near, δ t ≤ δnear) (hfar : ∀ t ∉ Near, δ t ≤ δfar)
    (hτ : δfar + ((m * w : ℕ) : ℝ) / n * (δnear - δfar) ≤ τ) : fstar δ τ = 0 :=
  (fstar_eq_zero_iff hn δ τ).mpr ((seam_mean_le hn δ Near m w hN hfn hnear hfar).trans hτ)

/-- **Corollary 3, converse.** If every token farther than `w` from a seam deviates by at least
`δ' ≥ 0`, then `μ ≥ (1 - mw/n) δ'`. -/
theorem seam_mean_ge (hn : 0 < n) (δ : Fin n → ℝ) (hδ : ∀ i, 0 ≤ δ i) (Near : Finset (Fin n))
    (m w : ℕ) (hN : Near.card ≤ m * w) {δ' : ℝ} (hδ' : 0 ≤ δ')
    (hfar : ∀ t ∉ Near, δ' ≤ δ t) :
    (1 - ((m * w : ℕ) : ℝ) / n) * δ' ≤ mu δ := by
  have hn' : (0 : ℝ) < n := by exact_mod_cast hn
  have h1 : ((n : ℝ) - Near.card) * δ' ≤ ∑ i ∈ univ \ Near, δ i := by
    have := Finset.card_nsmul_le_sum (univ \ Near) δ δ'
      (fun t ht => hfar t (Finset.mem_sdiff.mp ht).2)
    simp only [nsmul_eq_mul] at this
    rwa [card_compl_eq] at this
  have h2 : ∑ i ∈ univ \ Near, δ i ≤ ∑ i, δ i :=
    Finset.sum_le_sum_of_subset_of_nonneg (Finset.subset_univ _) (fun i _ _ => hδ i)
  have hNmw : (Near.card : ℝ) ≤ ((m * w : ℕ) : ℝ) := by exact_mod_cast hN
  have hprod : (Near.card : ℝ) * δ' ≤ ((m * w : ℕ) : ℝ) * δ' :=
    mul_le_mul_of_nonneg_right hNmw hδ'
  have hexp : (1 - ((m * w : ℕ) : ℝ) / n) * δ' * n = δ' * n - ((m * w : ℕ) : ℝ) * δ' := by
    rw [sub_mul, one_mul, sub_mul, div_mul_eq_mul_div, div_mul_cancel₀ _ hn'.ne']
  unfold mu
  rw [le_div_iff₀ hn', hexp]
  linarith [h1, h2, hprod]

/-- **Corollary 3, second consequence.** Once `δ' > τ` and `n (δ' - τ) > m w δ'` (all large `n`),
the floor is positive. -/
theorem seam_pos_floor (hn : 0 < n) (δ : Fin n → ℝ) (hδ : ∀ i, 0 ≤ δ i) (Near : Finset (Fin n))
    (m w : ℕ) (hN : Near.card ≤ m * w) {δ' τ : ℝ} (hτ : 0 < τ) (hτδ : τ < δ')
    (hfar : ∀ t ∉ Near, δ' ≤ δ t) (hbig : ((m * w : ℕ) : ℝ) * δ' < n * (δ' - τ)) :
    0 < fstar δ τ := by
  rw [fstar_pos_iff hn]
  have hn' : (0 : ℝ) < n := by exact_mod_cast hn
  have hge := seam_mean_ge hn δ hδ Near m w hN (by linarith) hfar
  have hexp : (1 - ((m * w : ℕ) : ℝ) / n) * δ' = (n * δ' - ((m * w : ℕ) : ℝ) * δ') / n := by
    field_simp
  have key : τ < (1 - ((m * w : ℕ) : ℝ) / n) * δ' := by
    rw [hexp, lt_div_iff₀ hn']
    linarith
  linarith

/-! ### The corollary as stated: `m` seams, each followed by at most `w` matched tokens -/

/-- The matched tokens following the `m` seams: the union of the per-seam windows. -/
def nearSet {m : ℕ} (win : Fin m → Finset (Fin n)) : Finset (Fin n) := univ.biUnion win

/-- `m` windows of at most `w` matched tokens hold at most `m w` tokens. -/
lemma card_nearSet_le {m w : ℕ} (win : Fin m → Finset (Fin n)) (hw : ∀ j, (win j).card ≤ w) :
    (nearSet win).card ≤ m * w := by
  unfold nearSet
  calc (univ.biUnion win).card ≤ ∑ j, (win j).card := Finset.card_biUnion_le
    _ ≤ ∑ _j : Fin m, w := Finset.sum_le_sum fun j _ => hw j
    _ = m * w := by simp

/-- The window of a seam at receiver position `σ`: matched tokens at positions `σ < p ≤ σ + w`. -/
def posWindow (pos : Fin n → ℕ) (σ w : ℕ) : Finset (Fin n) :=
  univ.filter fun t => σ < pos t ∧ pos t ≤ σ + w

/-- Distinct matched tokens sit at distinct receiver positions, so a window holds at most `w`. -/
lemma card_posWindow_le (pos : Fin n → ℕ) (hpos : Function.Injective pos) (σ w : ℕ) :
    (posWindow pos σ w).card ≤ w := by
  have hsub : (posWindow pos σ w).image pos ⊆ Finset.Ioc σ (σ + w) := by
    intro x hx
    obtain ⟨t, ht, rfl⟩ := Finset.mem_image.mp hx
    simp only [posWindow, Finset.mem_filter, Finset.mem_univ, true_and] at ht
    exact Finset.mem_Ioc.mpr ht
  calc (posWindow pos σ w).card = ((posWindow pos σ w).image pos).card :=
        (Finset.card_image_of_injective _ hpos).symm
    _ ≤ (Finset.Ioc σ (σ + w)).card := Finset.card_le_card hsub
    _ = w := by simp

/-- **Corollary `cor:seam`**, as stated. If each of the `m` seams is followed by at most `w`
matched tokens with `δ ≤ δ_near`, and every other matched token has `δ ≤ δ_far ≤ δ_near`, then
`μ ≤ δ_far + (mw/n)(δ_near - δ_far)`, and `f*(τ) = 0` whenever the right-hand side is at most `τ`. -/
theorem cor_seam {m w : ℕ} (hn : 0 < n) (δ : Fin n → ℝ) (win : Fin m → Finset (Fin n))
    (hw : ∀ j, (win j).card ≤ w) {δnear δfar τ : ℝ} (hfn : δfar ≤ δnear)
    (hnear : ∀ t ∈ nearSet win, δ t ≤ δnear) (hfar : ∀ t ∉ nearSet win, δ t ≤ δfar) :
    mu δ ≤ δfar + ((m * w : ℕ) : ℝ) / n * (δnear - δfar) ∧
      (δfar + ((m * w : ℕ) : ℝ) / n * (δnear - δfar) ≤ τ → fstar δ τ = 0) :=
  ⟨seam_mean_le hn δ _ m w (card_nearSet_le win hw) hfn hnear hfar,
    seam_zero_floor hn δ _ m w (card_nearSet_le win hw) hfn hnear hfar⟩

/-- **Corollary `cor:seam`, converse**, as stated. If every matched token outside the seam windows
has deviation at least `δ' ≥ 0`, then `μ ≥ (1 - mw/n) δ'`, and `f*(τ) > 0` once `δ' > τ` and
`n(δ' - τ) > m w δ'`. -/
theorem cor_seam_converse {m w : ℕ} (hn : 0 < n) (δ : Fin n → ℝ) (hδ : ∀ i, 0 ≤ δ i)
    (win : Fin m → Finset (Fin n)) (hw : ∀ j, (win j).card ≤ w) {δ' τ : ℝ} (hδ' : 0 ≤ δ')
    (hfar : ∀ t ∉ nearSet win, δ' ≤ δ t) :
    (1 - ((m * w : ℕ) : ℝ) / n) * δ' ≤ mu δ ∧
      (τ < δ' → ((m * w : ℕ) : ℝ) * δ' < n * (δ' - τ) → 0 < fstar δ τ) := by
  have hge := seam_mean_ge hn δ hδ _ m w (card_nearSet_le win hw) hδ' hfar
  refine ⟨hge, fun _ hbig => ?_⟩
  rw [fstar_pos_iff hn]
  have hn' : (0 : ℝ) < n := by exact_mod_cast hn
  have hexp : (1 - ((m * w : ℕ) : ℝ) / n) * δ' = (n * δ' - ((m * w : ℕ) : ℝ) * δ') / n := by
    field_simp
  have key : τ < (1 - ((m * w : ℕ) : ℝ) / n) * δ' := by
    rw [hexp, lt_div_iff₀ hn']
    linarith
  linarith

/-- "Which holds for all large `n`": for fixed `m`, `w` and `δ' > τ`,
`n(δ' - τ) > m w δ'` for every `n` beyond some `N₀`. -/
theorem cor_seam_large_n {m w : ℕ} {δ' τ : ℝ} (h : τ < δ') :
    ∃ N₀ : ℕ, ∀ n ≥ N₀, ((m * w : ℕ) : ℝ) * δ' < n * (δ' - τ) := by
  have hpos : 0 < δ' - τ := sub_pos.mpr h
  obtain ⟨N₀, hN₀⟩ := exists_nat_gt (((m * w : ℕ) : ℝ) * δ' / (δ' - τ))
  refine ⟨N₀, fun n hn => ?_⟩
  have h1 : ((m * w : ℕ) : ℝ) * δ' / (δ' - τ) < n :=
    lt_of_lt_of_le hN₀ (by exact_mod_cast hn)
  rwa [div_lt_iff₀ hpos] at h1

/-- The corollary with seams given by receiver positions: matched token `t` sits at position
`pos t` (injective) and seam `j` at `seam j`; its window is `seam j < pos t ≤ seam j + w`. -/
theorem cor_seam_positions {m w : ℕ} (hn : 0 < n) (δ : Fin n → ℝ) (pos : Fin n → ℕ)
    (hpos : Function.Injective pos) (seam : Fin m → ℕ) {δnear δfar τ : ℝ} (hfn : δfar ≤ δnear)
    (hnear : ∀ t ∈ nearSet (fun j => posWindow pos (seam j) w), δ t ≤ δnear)
    (hfar : ∀ t ∉ nearSet (fun j => posWindow pos (seam j) w), δ t ≤ δfar) :
    mu δ ≤ δfar + ((m * w : ℕ) : ℝ) / n * (δnear - δfar) ∧
      (δfar + ((m * w : ℕ) : ℝ) / n * (δnear - δfar) ≤ τ → fstar δ τ = 0) :=
  cor_seam hn δ _ (fun j => card_posWindow_le pos hpos (seam j) w) hfn hnear hfar

end Carryover

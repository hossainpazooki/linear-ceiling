import Mathlib

/-!
# The registered statistic and Theorems 1–2

Tokens of one handoff, arm and read-out are indexed by `Fin n` (the matched set `M`, `n = |M|`).
`δ : Fin n → ℝ` is the per-token deviation of Equation `eq:delta`; it is nonnegative.

`fstar δ τ` is Equation `eq:fstar`, written literally: sort the deviations, and take the least
`k < n` such that the mean of the `n - k` smallest deviations (the paper's `m(k)`) is at most `τ`;
if no such `k` exists the value is `1`.

This file proves
* `fstar_eq_zero_iff` — the kernel of Theorem `thm:identity`: `f*(τ) = 0 ↔ μ ≤ τ`;
* `fstar_antitone`, `fstar_le_p`, `p_le_one`, `p_le_mu_div`, `lower_bound_max`,
  `lower_bound_deltaMax`, `lower_bound_beta`, `lower_bound_beta_iSup` and the packaged
  `theorem2_sandwich` — Theorem `thm:sandwich`;
* `fstar_le_of_subset` and `exists_retained_set` — the subset characterisation used in the
  proof of Proposition `prop:attn` ("the oracle repair retains a set whose mean is at most τ").
-/

namespace Carryover

open Finset

variable {n : ℕ}

/-- The mean deviation `μ = (1/n) ∑_{t ∈ M} δ(t)`. -/
noncomputable def mu (δ : Fin n → ℝ) : ℝ := (∑ i, δ i) / n

/-- The deviations sorted in ascending order, `sorted δ 0 ≤ sorted δ 1 ≤ …`; the paper's
descending `δ_(i)` is `sorted δ (n - i)`. -/
noncomputable def sorted (δ : Fin n → ℝ) : Fin n → ℝ := δ ∘ Tuple.sort δ

lemma sorted_monotone (δ : Fin n → ℝ) : Monotone (sorted δ) := Tuple.monotone_sort δ

lemma sum_sorted (δ : Fin n → ℝ) : ∑ i, sorted δ i = ∑ i, δ i :=
  Equiv.sum_comp (Tuple.sort δ) δ

/-- The first `r` sorted indices, i.e. the `r` smallest deviations. -/
def first (n r : ℕ) : Finset (Fin n) := univ.filter (fun i => i.val < r)

lemma mem_first {r : ℕ} {i : Fin n} : i ∈ first n r ↔ i.val < r := by
  simp [first]

lemma card_first (r : ℕ) (hr : r ≤ n) : (first n r).card = r := by
  have : first n r = (univ : Finset (Fin r)).map (Fin.castLEEmb hr) := by
    ext i
    simp only [mem_first, mem_map, mem_univ, true_and]
    constructor
    · intro h; exact ⟨⟨i.val, h⟩, by ext; simp⟩
    · rintro ⟨j, rfl⟩; simp
  rw [this, card_map, card_univ, Fintype.card_fin]

lemma first_self : first n n = univ := by
  ext i; simp [mem_first, i.isLt]

/-- The paper's `m(k)`: the mean of the `n - k` smallest deviations. -/
noncomputable def tailMean (δ : Fin n → ℝ) (k : ℕ) : ℝ :=
  (∑ i ∈ first n (n - k), sorted δ i) / ((n - k : ℕ) : ℝ)

/-- `k` is feasible at tolerance `τ`: `0 ≤ k < n` and `m(k) ≤ τ`. -/
def Feasible (δ : Fin n → ℝ) (τ : ℝ) (k : ℕ) : Prop := k < n ∧ tailMean δ k ≤ τ

open Classical in
/-- Equation `eq:fstar`: `f*(τ) = min {k/n : 0 ≤ k < n, m(k) ≤ τ}`, and `1` if no nonempty
retained set qualifies. -/
noncomputable def fstar (δ : Fin n → ℝ) (τ : ℝ) : ℝ :=
  if ∃ k, Feasible δ τ k then ((sInf {k | Feasible δ τ k} : ℕ) : ℝ) / n else 1

/-- Share of matched tokens strictly above the tolerance, `p(τ)`. -/
noncomputable def pTail (δ : Fin n → ℝ) (τ : ℝ) : ℝ :=
  ((univ.filter (fun i => τ < δ i)).card : ℝ) / n

/-- Share of matched tokens with deviation at least `d`, `β(d)`. -/
noncomputable def beta (δ : Fin n → ℝ) (d : ℝ) : ℝ :=
  ((univ.filter (fun i => d ≤ δ i)).card : ℝ) / n

/-- `δ_max`, the largest deviation of the handoff. -/
noncomputable def deltaMax (hn : 0 < n) (δ : Fin n → ℝ) : ℝ :=
  univ.sup' ⟨⟨0, hn⟩, mem_univ _⟩ δ

lemma le_deltaMax (hn : 0 < n) (δ : Fin n → ℝ) (i : Fin n) : δ i ≤ deltaMax hn δ :=
  le_sup' δ (mem_univ i)

/-! ### Sums over equal-size sets of pairwise ordered values -/

/-- If every value on `P` is at most every value on `Q` and `|P| = |Q|`, the sums compare. -/
lemma sum_le_sum_of_pairwise {ι : Type*} (g : ι → ℝ) (P Q : Finset ι) (hcard : P.card = Q.card)
    (h : ∀ p ∈ P, ∀ q ∈ Q, g p ≤ g q) : ∑ p ∈ P, g p ≤ ∑ q ∈ Q, g q := by
  have h1 : (Q.card : ℝ) * ∑ p ∈ P, g p ≤ (P.card : ℝ) * ∑ q ∈ Q, g q := by
    calc (Q.card : ℝ) * ∑ p ∈ P, g p = ∑ p ∈ P, ∑ q ∈ Q, g p := by
          rw [Finset.mul_sum]; congr 1; ext p; simp [Finset.sum_const, mul_comm]
      _ ≤ ∑ p ∈ P, ∑ q ∈ Q, g q :=
          Finset.sum_le_sum fun p hp => Finset.sum_le_sum fun q hq => h p hp q hq
      _ = (P.card : ℝ) * ∑ q ∈ Q, g q := by simp [Finset.sum_const]
  rcases Nat.eq_zero_or_pos P.card with h0 | hpos
  · have hP : P = ∅ := Finset.card_eq_zero.mp h0
    have hQ : Q = ∅ := Finset.card_eq_zero.mp (hcard ▸ h0)
    simp [hP, hQ]
  · rw [← hcard] at h1
    exact le_of_mul_le_mul_left h1 (by exact_mod_cast hpos)

/-- For a monotone `g` on `Fin n`, the sum of the first `r` values is at most the sum over any
`r`-element subset. -/
lemma sum_first_le_sum_of_monotone (g : Fin n → ℝ) (hg : Monotone g) (U : Finset (Fin n))
    (r : ℕ) (hU : U.card = r) (hr : r ≤ n) :
    ∑ i ∈ first n r, g i ≤ ∑ i ∈ U, g i := by
  set A := first n r with hA
  have hAcard : A.card = r := card_first r hr
  have hsplitA : ∑ i ∈ A, g i = ∑ i ∈ A \ U, g i + ∑ i ∈ A ∩ U, g i := by
    rw [← Finset.sum_sdiff (Finset.inter_subset_left (s₂ := U)), Finset.sdiff_inter_self_left]
  have hsplitU : ∑ i ∈ U, g i = ∑ i ∈ U \ A, g i + ∑ i ∈ A ∩ U, g i := by
    rw [Finset.inter_comm, ← Finset.sum_sdiff (Finset.inter_subset_left (s₂ := A)),
      Finset.sdiff_inter_self_left]
  rw [hsplitA, hsplitU]
  have hcard : (A \ U).card = (U \ A).card := by
    have h1 := Finset.card_sdiff_add_card_inter A U
    have h2 := Finset.card_sdiff_add_card_inter U A
    rw [Finset.inter_comm] at h2
    omega
  refine add_le_add (sum_le_sum_of_pairwise g _ _ hcard ?_) le_rfl
  intro p hp q hq
  apply hg
  have hp' : p.val < r := mem_first.mp (Finset.mem_sdiff.mp hp).1
  have hq' : ¬ q.val < r := fun h => (Finset.mem_sdiff.mp hq).2 (mem_first.mpr h)
  exact Fin.le_def.mpr (by omega)

/-- The sum of the `r` smallest deviations is at most the sum over any `r` tokens. -/
lemma sum_first_sorted_le (δ : Fin n → ℝ) (T : Finset (Fin n)) (r : ℕ) (hT : T.card = r)
    (hr : r ≤ n) : ∑ i ∈ first n r, sorted δ i ≤ ∑ j ∈ T, δ j := by
  set σ := Tuple.sort δ
  have hmap : ∑ j ∈ T, δ j = ∑ i ∈ T.map σ.symm.toEmbedding, sorted δ i := by
    rw [Finset.sum_map]
    simp [sorted, σ]
  rw [hmap]
  exact sum_first_le_sum_of_monotone (sorted δ) (sorted_monotone δ) _ r
    (by rw [Finset.card_map, hT]) hr

/-! ### Basic properties of `f*` -/

lemma tailMean_zero (δ : Fin n → ℝ) : tailMean δ 0 = mu δ := by
  simp only [tailMean, mu, Nat.sub_zero, first_self, sum_sorted]

lemma fstar_of_feasible {δ : Fin n → ℝ} {τ : ℝ} (h : ∃ k, Feasible δ τ k) :
    fstar δ τ = ((sInf {k | Feasible δ τ k} : ℕ) : ℝ) / n := by
  simp only [fstar, h, ↓reduceIte]

lemma fstar_of_not_feasible {δ : Fin n → ℝ} {τ : ℝ} (h : ¬ ∃ k, Feasible δ τ k) :
    fstar δ τ = 1 := by
  simp only [fstar, h, ↓reduceIte]

/-- When some `k` is feasible, `f*(τ) = k*/n` for the least feasible `k*`. -/
lemma fstar_spec {δ : Fin n → ℝ} {τ : ℝ} (h : ∃ k, Feasible δ τ k) :
    ∃ k, Feasible δ τ k ∧ fstar δ τ = (k : ℝ) / n ∧ ∀ k', Feasible δ τ k' → k ≤ k' :=
  ⟨sInf {k | Feasible δ τ k}, Nat.sInf_mem h, fstar_of_feasible h, fun _ hk' => Nat.sInf_le hk'⟩

/-- `f*(τ) ≤ k / n` for every feasible `k`. -/
lemma fstar_le_of_feasible {δ : Fin n → ℝ} {τ : ℝ} {k : ℕ} (hk : Feasible δ τ k) :
    fstar δ τ ≤ (k : ℝ) / n := by
  obtain ⟨k0, -, hfk, hmin⟩ := fstar_spec ⟨k, hk⟩
  rw [hfk]
  have : (k0 : ℝ) ≤ k := by exact_mod_cast hmin k hk
  exact div_le_div_of_nonneg_right this (Nat.cast_nonneg n)

lemma fstar_nonneg (δ : Fin n → ℝ) (τ : ℝ) : 0 ≤ fstar δ τ := by
  by_cases h : ∃ k, Feasible δ τ k
  · obtain ⟨k, -, hfk, -⟩ := fstar_spec h
    rw [hfk]; positivity
  · rw [fstar_of_not_feasible h]; exact zero_le_one

lemma fstar_le_one (δ : Fin n → ℝ) (τ : ℝ) : fstar δ τ ≤ 1 := by
  by_cases h : ∃ k, Feasible δ τ k
  · obtain ⟨k, hk, hfk, -⟩ := fstar_spec h
    rw [hfk]
    have hn : (0 : ℝ) < n := by exact_mod_cast (lt_of_le_of_lt (Nat.zero_le _) hk.1)
    rw [div_le_one hn]
    exact_mod_cast hk.1.le
  · rw [fstar_of_not_feasible h]

/-- **Theorem 1, kernel.** `f*(τ) = 0` if and only if the mean deviation is within tolerance. -/
theorem fstar_eq_zero_iff (hn : 0 < n) (δ : Fin n → ℝ) (τ : ℝ) :
    fstar δ τ = 0 ↔ mu δ ≤ τ := by
  have hn' : (n : ℝ) ≠ 0 := by exact_mod_cast hn.ne'
  constructor
  · intro h0
    by_cases h : ∃ k, Feasible δ τ k
    · obtain ⟨k, hk, hfk, -⟩ := fstar_spec h
      rw [hfk] at h0
      have hk0 : (k : ℝ) = 0 := (div_eq_zero_iff.mp h0).resolve_right hn'
      have : k = 0 := by exact_mod_cast hk0
      subst this
      simpa [tailMean_zero] using hk.2
    · rw [fstar_of_not_feasible h] at h0
      exact absurd h0 one_ne_zero
  · intro hμ
    have hf : Feasible δ τ 0 := ⟨hn, by simpa [tailMean_zero] using hμ⟩
    have h1 := fstar_le_of_feasible hf
    have h2 := fstar_nonneg δ τ
    simp only [Nat.cast_zero, zero_div] at h1
    linarith

theorem fstar_pos_iff (hn : 0 < n) (δ : Fin n → ℝ) (τ : ℝ) : 0 < fstar δ τ ↔ τ < mu δ := by
  rw [lt_iff_not_ge, ← not_le, not_iff_not]
  constructor
  · intro h; exact (fstar_eq_zero_iff hn δ τ).mp (le_antisymm h (fstar_nonneg δ τ))
  · intro h; exact ((fstar_eq_zero_iff hn δ τ).mpr h).le

/-- **Theorem 2, monotonicity.** `f*` is nonincreasing in `τ`. -/
theorem fstar_antitone (δ : Fin n → ℝ) {τ τ' : ℝ} (h : τ ≤ τ') : fstar δ τ' ≤ fstar δ τ := by
  by_cases hτ : ∃ k, Feasible δ τ k
  · obtain ⟨k, hk, hfk, -⟩ := fstar_spec hτ
    rw [hfk]
    exact fstar_le_of_feasible ⟨hk.1, hk.2.trans h⟩
  · rw [fstar_of_not_feasible hτ]; exact fstar_le_one δ τ'

/-- Subset characterisation: any nonempty retained set `T` with mean at most `τ` bounds the floor
by `1 - |T|/n`. -/
theorem fstar_le_of_subset (δ : Fin n → ℝ) (τ : ℝ) (T : Finset (Fin n)) (hT : T.Nonempty)
    (hmean : (∑ t ∈ T, δ t) / T.card ≤ τ) : fstar δ τ ≤ 1 - (T.card : ℝ) / n := by
  have hTn : T.card ≤ n := by simpa using Finset.card_le_univ T
  have hpos : 0 < T.card := Finset.card_pos.mpr hT
  have hfeas : Feasible δ τ (n - T.card) := by
    refine ⟨by omega, ?_⟩
    unfold tailMean
    have hsub : n - (n - T.card) = T.card := by omega
    rw [hsub]
    have hle := sum_first_sorted_le δ T T.card rfl hTn
    exact (div_le_div_of_nonneg_right hle (by positivity)).trans hmean
  have := fstar_le_of_feasible hfeas
  have hn : (0 : ℝ) < n := by exact_mod_cast (lt_of_lt_of_le hpos hTn)
  calc fstar δ τ ≤ ((n - T.card : ℕ) : ℝ) / n := this
    _ = 1 - (T.card : ℝ) / n := by
        rw [Nat.cast_sub hTn, sub_div, div_self hn.ne']

/-- Conversely, when `f*(τ) < 1` the oracle retains a set of `n(1 - f*(τ))` tokens whose mean
deviation is at most `τ` (the `n - k` smallest deviations, mapped back to tokens). -/
theorem exists_retained_set (δ : Fin n → ℝ) (τ : ℝ) (h : fstar δ τ < 1) :
    ∃ T : Finset (Fin n), (T.card : ℝ) = n * (1 - fstar δ τ) ∧
      (∑ t ∈ T, δ t) / T.card ≤ τ := by
  by_cases hf : ∃ k, Feasible δ τ k
  · obtain ⟨k, hk, hfk, -⟩ := fstar_spec hf
    have hkn : k < n := hk.1
    have hn : (0 : ℝ) < n := by exact_mod_cast (lt_of_le_of_lt (Nat.zero_le _) hkn)
    refine ⟨(first n (n - k)).map (Tuple.sort δ).toEmbedding, ?_, ?_⟩
    · rw [Finset.card_map, card_first _ (Nat.sub_le _ _), hfk, Nat.cast_sub hkn.le]
      have : (n : ℝ) * ((k : ℝ) / n) = k := by field_simp
      rw [mul_sub, mul_one, this]
    · rw [Finset.card_map, card_first _ (Nat.sub_le _ _), Finset.sum_map]
      exact hk.2
  · rw [fstar_of_not_feasible hf] at h
    exact absurd h (lt_irrefl 1)

/-! ### Theorem 2: the upper bounds -/

/-- `f*(τ) ≤ p(τ)`: removing exactly the tokens above the tolerance is feasible. -/
theorem fstar_le_p (hn : 0 < n) (δ : Fin n → ℝ) (τ : ℝ) : fstar δ τ ≤ pTail δ τ := by
  set T := univ.filter (fun i => ¬ τ < δ i) with hT
  have hcompl : (univ.filter (fun i => τ < δ i)).card + T.card = n := by
    have := Finset.card_filter_add_card_filter_not (s := (univ : Finset (Fin n)))
      (fun i => τ < δ i)
    rwa [Finset.card_univ, Fintype.card_fin] at this
  have hn' : (n : ℝ) ≠ 0 := by exact_mod_cast hn.ne'
  by_cases hTe : T.Nonempty
  · have hmean : (∑ t ∈ T, δ t) / T.card ≤ τ := by
      have hpos : (0 : ℝ) < T.card := by exact_mod_cast Finset.card_pos.mpr hTe
      rw [div_le_iff₀ hpos]
      have := Finset.sum_le_card_nsmul T δ τ
        (fun i hi => not_lt.mp (Finset.mem_filter.mp hi).2)
      simp only [nsmul_eq_mul] at this
      linarith
    have := fstar_le_of_subset δ τ T hTe hmean
    unfold pTail
    have hc : ((univ.filter (fun i => τ < δ i)).card : ℝ) = n - T.card := by
      have := congrArg (fun m : ℕ => (m : ℝ)) hcompl
      push_cast at this
      linarith
    rw [hc, sub_div, div_self hn']
    exact this
  · have hT0 : T.card = 0 := by
      rw [Finset.not_nonempty_iff_eq_empty] at hTe; simp [hTe]
    unfold pTail
    have hc : (univ.filter (fun i => τ < δ i)).card = n := by omega
    rw [hc, div_self hn']
    exact fstar_le_one δ τ

theorem p_le_one (hn : 0 < n) (δ : Fin n → ℝ) (τ : ℝ) : pTail δ τ ≤ 1 := by
  unfold pTail
  rw [div_le_one (by exact_mod_cast hn)]
  exact_mod_cast (Finset.card_le_univ _).trans (by simp)

theorem p_nonneg (δ : Fin n → ℝ) (τ : ℝ) : 0 ≤ pTail δ τ := by
  unfold pTail; positivity

/-- Markov's inequality: `p(τ) ≤ μ / τ`. -/
theorem p_le_mu_div (δ : Fin n → ℝ) (hδ : ∀ i, 0 ≤ δ i) {τ : ℝ} (hτ : 0 < τ) :
    pTail δ τ ≤ mu δ / τ := by
  unfold pTail mu
  set S := univ.filter (fun i => τ < δ i)
  have h1 : τ * S.card ≤ ∑ i ∈ S, δ i := by
    have := Finset.card_nsmul_le_sum S δ τ (fun i hi => (Finset.mem_filter.mp hi).2.le)
    simp only [nsmul_eq_mul] at this
    linarith
  have h2 : ∑ i ∈ S, δ i ≤ ∑ i, δ i :=
    Finset.sum_le_sum_of_subset_of_nonneg (Finset.subset_univ S) (fun i _ _ => hδ i)
  rcases Nat.eq_zero_or_pos n with h0 | hn
  · subst h0; simp
  · have hn' : (0 : ℝ) < n := by exact_mod_cast hn
    rw [div_div, div_le_div_iff₀ hn' (by positivity)]
    nlinarith [h1, h2]

/-! ### Theorem 2: the lower bounds -/

/-- The sum of the removed deviations is at most `k · D` when every deviation is at most `D`. -/
lemma sum_removed_le (δ : Fin n → ℝ) {D : ℝ} (hD : ∀ i, δ i ≤ D) (k : ℕ) (hk : k ≤ n) :
    ∑ i ∈ univ \ first n (n - k), sorted δ i ≤ k * D := by
  have hcard : (univ \ first n (n - k)).card = k := by
    rw [Finset.card_univ_sdiff, card_first _ (Nat.sub_le _ _), Fintype.card_fin]; omega
  have := Finset.sum_le_card_nsmul (univ \ first n (n - k)) (sorted δ) D
    (fun i _ => hD (Tuple.sort δ i))
  rw [hcard] at this
  simpa [nsmul_eq_mul] using this

/-- The retained sum is at most `(n - k) τ` for a feasible `k`. -/
lemma sum_retained_le {δ : Fin n → ℝ} {τ : ℝ} {k : ℕ} (hk : Feasible δ τ k) :
    ∑ i ∈ first n (n - k), sorted δ i ≤ ((n : ℝ) - k) * τ := by
  have hpos : (0 : ℝ) < ((n - k : ℕ) : ℝ) := by exact_mod_cast Nat.sub_pos_of_lt hk.1
  have := hk.2
  unfold tailMean at this
  rw [div_le_iff₀ hpos, Nat.cast_sub hk.1.le] at this
  linarith

lemma mu_le_of_forall_le (hn : 0 < n) (δ : Fin n → ℝ) {D : ℝ} (hD : ∀ i, δ i ≤ D) : mu δ ≤ D := by
  have hn' : (0 : ℝ) < n := by exact_mod_cast hn
  unfold mu
  rw [div_le_iff₀ hn']
  have := Finset.sum_le_card_nsmul (univ : Finset (Fin n)) δ D (fun i _ => hD i)
  simp only [nsmul_eq_mul, Finset.card_univ, Fintype.card_fin] at this
  linarith

/-- **Theorem 2, first lower bound**, with any upper bound `D ≥ δ_max`:
`(μ - τ)/(D - τ) ≤ f*(τ)` when `τ < D`. -/
theorem lower_bound_max (hn : 0 < n) (δ : Fin n → ℝ) {τ D : ℝ} (hD : ∀ i, δ i ≤ D)
    (hτD : τ < D) : (mu δ - τ) / (D - τ) ≤ fstar δ τ := by
  have hn' : (0 : ℝ) < n := by exact_mod_cast hn
  have hn0 : (n : ℝ) ≠ 0 := hn'.ne'
  have hDτ : 0 < D - τ := by linarith
  have hμD : mu δ ≤ D := mu_le_of_forall_le hn δ hD
  by_cases hf : ∃ k, Feasible δ τ k
  · obtain ⟨k, hk, hfk, -⟩ := fstar_spec hf
    rw [hfk]
    have hret := sum_retained_le hk
    have hrem := sum_removed_le δ hD k hk.1.le
    have htot : ∑ i, sorted δ i =
        ∑ i ∈ first n (n - k), sorted δ i + ∑ i ∈ univ \ first n (n - k), sorted δ i := by
      rw [add_comm, Finset.sum_sdiff (Finset.subset_univ _)]
    have hμ : mu δ * n = ∑ i, sorted δ i := by
      unfold mu; rw [sum_sorted]; field_simp
    rw [div_le_div_iff₀ hDτ hn']
    nlinarith [hret, hrem, htot, hμ]
  · rw [fstar_of_not_feasible hf, div_le_one hDτ]
    linarith

/-- The first lower bound in the paper's form, with `δ_max` and the positive part. -/
theorem lower_bound_deltaMax (hn : 0 < n) (δ : Fin n → ℝ) {τ : ℝ} (hτ : τ < deltaMax hn δ) :
    max (mu δ - τ) 0 / (deltaMax hn δ - τ) ≤ fstar δ τ := by
  rcases le_or_gt (mu δ - τ) 0 with h | h
  · rw [max_eq_right h, zero_div]; exact fstar_nonneg δ τ
  · rw [max_eq_left h.le]; exact lower_bound_max hn δ (le_deltaMax hn δ) hτ

/-- When `δ_max ≤ τ` the floor is zero (the bound is "read as 0"). -/
theorem fstar_eq_zero_of_deltaMax_le (hn : 0 < n) (δ : Fin n → ℝ) {τ : ℝ}
    (h : deltaMax hn δ ≤ τ) : fstar δ τ = 0 :=
  (fstar_eq_zero_iff hn δ τ).mpr ((mu_le_of_forall_le hn δ (le_deltaMax hn δ)).trans h)

/-- Counting is invariant under the sorting permutation. -/
lemma card_filter_sorted (δ : Fin n → ℝ) (p : ℝ → Prop) [DecidablePred p] :
    (univ.filter (fun i => p (sorted δ i))).card = (univ.filter (fun i => p (δ i))).card := by
  apply Finset.card_equiv (Tuple.sort δ)
  intro i
  rw [Finset.mem_filter, Finset.mem_filter]
  simp [sorted]

/-- **Theorem 2, second lower bound**: for every `d > τ`,
`(β(d) d - τ)/(d - τ) ≤ f*(τ)`. -/
theorem lower_bound_beta (hn : 0 < n) (δ : Fin n → ℝ) (hδ : ∀ i, 0 ≤ δ i) {τ d : ℝ}
    (hτ : 0 < τ) (hd : τ < d) : (beta δ d * d - τ) / (d - τ) ≤ fstar δ τ := by
  have hn' : (0 : ℝ) < n := by exact_mod_cast hn
  have hdτ : 0 < d - τ := by linarith
  have hd0 : 0 < d := by linarith
  have hβ1 : beta δ d ≤ 1 := by
    unfold beta
    rw [div_le_one hn']
    exact_mod_cast (Finset.card_le_univ _).trans (by simp)
  by_cases hf : ∃ k, Feasible δ τ k
  · obtain ⟨k, hk, hfk, -⟩ := fstar_spec hf
    rw [hfk]
    have hkn : k < n := hk.1
    set S := first n (n - k) with hS
    have hScard : S.card = n - k := card_first _ (Nat.sub_le _ _)
    have hret : ∑ i ∈ S, sorted δ i ≤ ((n : ℝ) - k) * τ := sum_retained_le hk
    -- `B` counts tokens with deviation at least `d`, in either coordinate system
    set B := (univ.filter (fun i => d ≤ δ i)).card with hB
    have hBβ : beta δ d = (B : ℝ) / n := rfl
    have hBs : (univ.filter (fun i => d ≤ sorted δ i)).card = B :=
      card_filter_sorted δ (fun x => d ≤ x)
    have hBn : B ≤ n := by
      rw [hB]; exact (Finset.card_le_univ _).trans (by simp)
    -- split the retained set by the threshold `d`
    have hSsplit : (S.filter (fun i => d ≤ sorted δ i)).card
        + (S.filter (fun i => ¬ d ≤ sorted δ i)).card = S.card :=
      Finset.card_filter_add_card_filter_not (s := S) (fun i => d ≤ sorted δ i)
    have hLoAll : (univ.filter (fun i => ¬ d ≤ sorted δ i)).card = n - B := by
      have := Finset.card_filter_add_card_filter_not (s := (univ : Finset (Fin n)))
        (fun i => d ≤ sorted δ i)
      rw [hBs, Finset.card_univ, Fintype.card_fin] at this
      omega
    have hSLo : (S.filter (fun i => ¬ d ≤ sorted δ i)).card ≤ n - B := by
      rw [← hLoAll]
      apply Finset.card_le_card
      intro x hx
      simp only [Finset.mem_filter] at hx ⊢
      exact ⟨Finset.mem_univ _, hx.2⟩
    have hcount : (B : ℝ) - k ≤ ((S.filter (fun i => d ≤ sorted δ i)).card : ℝ) := by
      have h1 : n - k ≤ (S.filter (fun i => d ≤ sorted δ i)).card + (n - B) := by omega
      have h2 : ((n - k : ℕ) : ℝ) ≤ ((S.filter (fun i => d ≤ sorted δ i)).card : ℝ)
          + ((n - B : ℕ) : ℝ) := by exact_mod_cast h1
      rw [Nat.cast_sub hkn.le, Nat.cast_sub hBn] at h2
      linarith
    have hsumHi : d * ((S.filter (fun i => d ≤ sorted δ i)).card : ℝ)
        ≤ ∑ i ∈ S.filter (fun i => d ≤ sorted δ i), sorted δ i := by
      have := Finset.card_nsmul_le_sum (S.filter (fun i => d ≤ sorted δ i)) (sorted δ) d
        (fun i hi => (Finset.mem_filter.mp hi).2)
      simp only [nsmul_eq_mul] at this
      linarith
    have hsub : ∑ i ∈ S.filter (fun i => d ≤ sorted δ i), sorted δ i ≤ ∑ i ∈ S, sorted δ i :=
      Finset.sum_le_sum_of_subset_of_nonneg (Finset.filter_subset _ _)
        (fun i _ _ => hδ (Tuple.sort δ i))
    have hexp : ((B : ℝ) / n * d - τ) * n = B * d - τ * n := by
      field_simp
    rw [hBβ, div_le_div_iff₀ hdτ hn', hexp]
    have hprod := mul_le_mul_of_nonneg_left hcount hd0.le
    linarith [hret, hsumHi, hsub, hprod]
  · rw [fstar_of_not_feasible hf, div_le_one hdτ]
    nlinarith [hβ1, hd0]

/-- The second lower bound with the positive part, as displayed in the theorem. -/
theorem lower_bound_beta_pos (hn : 0 < n) (δ : Fin n → ℝ) (hδ : ∀ i, 0 ≤ δ i) {τ d : ℝ}
    (hτ : 0 < τ) (hd : τ < d) : max (beta δ d * d - τ) 0 / (d - τ) ≤ fstar δ τ := by
  rcases le_or_gt (beta δ d * d - τ) 0 with h | h
  · rw [max_eq_right h, zero_div]; exact fstar_nonneg δ τ
  · rw [max_eq_left h.le]; exact lower_bound_beta hn δ hδ hτ hd

/-- The supremum over `d > τ` of the second lower bound. -/
theorem lower_bound_beta_iSup (hn : 0 < n) (δ : Fin n → ℝ) (hδ : ∀ i, 0 ≤ δ i) {τ : ℝ}
    (hτ : 0 < τ) :
    (⨆ d : {d : ℝ // τ < d}, max (beta δ d.1 * d.1 - τ) 0 / (d.1 - τ)) ≤ fstar δ τ := by
  have : Nonempty {d : ℝ // τ < d} := ⟨⟨τ + 1, by linarith⟩⟩
  exact ciSup_le fun d => lower_bound_beta_pos hn δ hδ hτ d.2

/-- **Theorem 2 (Two-sided bounds on the floor)**, packaged as displayed, with the first lower
bound read as `0` when `δ_max ≤ τ`. -/
theorem theorem2_sandwich (hn : 0 < n) (δ : Fin n → ℝ) (hδ : ∀ i, 0 ≤ δ i) {τ : ℝ}
    (hτ : 0 < τ) :
    max (if deltaMax hn δ ≤ τ then 0 else max (mu δ - τ) 0 / (deltaMax hn δ - τ))
        (⨆ d : {d : ℝ // τ < d}, max (beta δ d.1 * d.1 - τ) 0 / (d.1 - τ))
      ≤ fstar δ τ ∧
    fstar δ τ ≤ pTail δ τ ∧
    pTail δ τ ≤ min 1 (mu δ / τ) := by
  refine ⟨max_le ?_ (lower_bound_beta_iSup hn δ hδ hτ), fstar_le_p hn δ τ,
    le_min (p_le_one hn δ τ) (p_le_mu_div δ hδ hτ)⟩
  split_ifs with h
  · exact fstar_nonneg δ τ
  · exact lower_bound_deltaMax hn δ (lt_of_not_ge h)

end Carryover

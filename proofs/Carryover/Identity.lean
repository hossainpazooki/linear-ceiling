import Carryover.Fstar

/-!
# Theorem 1: the floor is a variance-explained threshold

Equation `eq:delta` at one layer/head pair `p = (l, h)`: with `x_R t p` the fresh receiver cache
and `xhat t p` the candidate, `s2 p` is the receiver's per-head variance over the matched set,
`devLH t p` the `(l,h)` term of the deviation and `dev t` its average over the `LH` pairs.
`R2 p` is the coefficient of determination of `xhat` against `x_R` with the centered denominator
(Appendix D), and `R2bar` its average over `(l, h)`.
-/

namespace Carryover

open Finset

variable {n : ℕ} {P : Type*} [Fintype P] {E : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]

/-- `x̄_R(l,h)`, the mean over matched tokens. -/
noncomputable def meanR (xR : Fin n → P → E) (p : P) : E := (n : ℝ)⁻¹ • ∑ t, xR t p

/-- `s²_{l,h}`, the receiver's per-head variance over `M`. -/
noncomputable def s2 (xR : Fin n → P → E) (p : P) : ℝ :=
  (∑ t, ‖xR t p - meanR xR p‖ ^ 2) / n

/-- The `(l,h)` term of Equation `eq:delta`. -/
noncomputable def devLH (xhat xR : Fin n → P → E) (t : Fin n) (p : P) : ℝ :=
  ‖xhat t p - xR t p‖ ^ 2 / s2 xR p

/-- `δ(t)`, Equation `eq:delta`. -/
noncomputable def dev (xhat xR : Fin n → P → E) (t : Fin n) : ℝ :=
  (∑ p, devLH xhat xR t p) / Fintype.card P

noncomputable def SSE (xhat xR : Fin n → P → E) (p : P) : ℝ := ∑ t, ‖xhat t p - xR t p‖ ^ 2

noncomputable def SST (xR : Fin n → P → E) (p : P) : ℝ := ∑ t, ‖xR t p - meanR xR p‖ ^ 2

/-- `R²(l,h) = 1 - SSE/SST` with the centered denominator. -/
noncomputable def R2 (xhat xR : Fin n → P → E) (p : P) : ℝ := 1 - SSE xhat xR p / SST xR p

/-- `R̄²`, averaged over `(l,h)`. -/
noncomputable def R2bar (xhat xR : Fin n → P → E) : ℝ := (∑ p, R2 xhat xR p) / Fintype.card P

omit [Fintype P] in
lemma devLH_nonneg (xhat xR : Fin n → P → E) (t : Fin n) (p : P) : 0 ≤ devLH xhat xR t p := by
  unfold devLH s2; positivity

lemma dev_nonneg (xhat xR : Fin n → P → E) (t : Fin n) : 0 ≤ dev xhat xR t := by
  unfold dev
  exact div_nonneg (Finset.sum_nonneg fun p _ => devLH_nonneg xhat xR t p) (Nat.cast_nonneg _)

omit [Fintype P] in
lemma SST_eq (hn : 0 < n) (xR : Fin n → P → E) (p : P) : SST xR p = n * s2 xR p := by
  unfold SST s2
  have : (n : ℝ) ≠ 0 := by exact_mod_cast hn.ne'
  field_simp

omit [Fintype P] in
/-- The `(l,h)` step of the proof: `(1/n) ∑_t δ_{l,h}(t) = SSE/SST = 1 - R²(l,h)`. -/
theorem mean_devLH (hn : 0 < n) (xhat xR : Fin n → P → E) (p : P) :
    (∑ t, devLH xhat xR t p) / n = 1 - R2 xhat xR p := by
  unfold devLH R2 SSE
  rw [← Finset.sum_div, div_div, mul_comm (s2 xR p) (n : ℝ), ← SST_eq hn xR p]
  ring

/-- **Theorem 1, identity.** `μ = 1 - R̄²`. -/
theorem mu_dev (hn : 0 < n) (hP : 0 < Fintype.card P) (xhat xR : Fin n → P → E) :
    mu (dev xhat xR) = 1 - R2bar xhat xR := by
  have hP' : (Fintype.card P : ℝ) ≠ 0 := by exact_mod_cast hP.ne'
  unfold mu dev R2bar
  rw [← Finset.sum_div, Finset.sum_comm, div_right_comm, Finset.sum_div]
  simp_rw [mean_devLH hn]
  rw [Finset.sum_sub_distrib, Finset.sum_const, Finset.card_univ, nsmul_eq_mul, mul_one, sub_div,
    div_self hP']

/-- **Theorem 1.** `f*(τ) = 0 ↔ R̄² ≥ 1 - τ`. -/
theorem theorem1 (hn : 0 < n) (hP : 0 < Fintype.card P) (xhat xR : Fin n → P → E) (τ : ℝ) :
    fstar (dev xhat xR) τ = 0 ↔ 1 - τ ≤ R2bar xhat xR := by
  rw [fstar_eq_zero_iff hn, mu_dev hn hP]
  constructor <;> intro h <;> linarith

/-- **Theorem 1, verdict clause.** With `τ_K = 1 - R²_map`, `f*(τ_K) = 0` holds exactly when the
reused cache explains at least as much variance as the map. -/
theorem theorem1_verdict (hn : 0 < n) (hP : 0 < Fintype.card P) (xhat xR : Fin n → P → E)
    (R2map : ℝ) : fstar (dev xhat xR) (1 - R2map) = 0 ↔ R2map ≤ R2bar xhat xR := by
  rw [theorem1 hn hP]
  constructor <;> intro h <;> linarith

theorem theorem1_pos (hn : 0 < n) (hP : 0 < Fintype.card P) (xhat xR : Fin n → P → E) (τ : ℝ) :
    0 < fstar (dev xhat xR) τ ↔ R2bar xhat xR < 1 - τ := by
  rw [fstar_pos_iff hn, mu_dev hn hP]
  constructor <;> intro h <;> linarith

omit [Fintype P] in
/-- Equation `eq:delta` averages over the `L H` layer–head pairs. -/
lemma card_layer_head (L H : ℕ) : Fintype.card (Fin L × Fin H) = L * H := by simp

omit [Fintype P] in
/-- **Theorem `thm:identity`**, as stated, for `L` layers and `H` KV heads and
`μ = (1/n) ∑_{t ∈ M} δ(t)`: `μ = 1 - R̄²`; `f*(τ) = 0 ↔ R̄² ≥ 1 - τ`; and with `τ_K = 1 - R²_map`,
`f*(τ_K) = 0 ↔ R̄² ≥ R²_map`. -/
theorem thm_identity {L H : ℕ} (hn : 0 < n) (hL : 0 < L) (hH : 0 < H)
    (xhat xR : Fin n → Fin L × Fin H → E) (τ R2map : ℝ) :
    mu (dev xhat xR) = 1 - R2bar xhat xR ∧
      (fstar (dev xhat xR) τ = 0 ↔ 1 - τ ≤ R2bar xhat xR) ∧
      (fstar (dev xhat xR) (1 - R2map) = 0 ↔ R2map ≤ R2bar xhat xR) := by
  have hP : 0 < Fintype.card (Fin L × Fin H) := by
    rw [card_layer_head]; exact Nat.mul_pos hL hH
  exact ⟨mu_dev hn hP xhat xR, theorem1 hn hP xhat xR τ, theorem1_verdict hn hP xhat xR R2map⟩

/-! ### The retained-set mean, per `(l,h)` and averaged (used in Proposition 4) -/

/-- The average over `(l,h)` of the retained means `μ^ret_{l,h}` equals the retained mean of
`δ`, so it is at most `τ` whenever the retained set passes the tolerance. -/
theorem retained_mean_avg (T : Finset (Fin n)) (D : Fin n → P → ℝ) :
    (∑ p, (∑ t ∈ T, D t p) / T.card) / Fintype.card P
      = (∑ t ∈ T, (∑ p, D t p) / Fintype.card P) / T.card := by
  rw [← Finset.sum_div, ← Finset.sum_div, Finset.sum_comm, div_right_comm]

theorem retained_mean_le (xhat xR : Fin n → P → E) (T : Finset (Fin n)) {τ : ℝ}
    (hT : (∑ t ∈ T, dev xhat xR t) / T.card ≤ τ) :
    (∑ p, (∑ t ∈ T, devLH xhat xR t p) / T.card) / Fintype.card P ≤ τ := by
  rw [retained_mean_avg]; exact hT

end Carryover

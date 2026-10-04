import Carryover.Identity
import Carryover.Seams

/-!
# The numbers reported beside the theorems

Ledger macros of `main.tex` checked against Theorems `thm:identity` and `thm:sandwich`.

Both theorems are per-handoff statements, while the paper reports cohort medians. Two facts link
them. (i) Theorem 1 gives `f*(τ) = 0 ↔ R̄² ≥ 1 - τ` for every handoff, so a median `R̄²` at or above
(below) `1 - τ` puts at least half of the handoffs at `f*(τ) = 0` (`> 0`); with an odd cohort
(25 or 35 handoffs) the median `f*(τ)` is then `0` (`> 0`). (ii) A pointwise inequality between
two per-handoff quantities carries over to their medians and other quantiles. The lemmas below
state the per-handoff fact; the docstrings name the reported medians it explains.
-/

namespace Carryover

open Finset

/-! ### Tolerances: `\tauK = 1 - \rTwoK`, `\tauV = 1 - \rTwoV` -/

theorem tauK_eq : (0.3186 : ℝ) = 1 - 0.6814 := by norm_num
theorem tauV_eq : (0.4867 : ℝ) = 1 - 0.5133 := by norm_num

/-! ### Theorem 1 against Table `tab:arms-long` and the configuration bridge -/

section Theorem1

variable {n : ℕ} {P : Type*} [Fintype P] {E : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]

/-- Same-model keys (`R²_K` median `0.8894 ≥ 1 - τ_K`): `f*(τ_K) = 0`, as reported (`0.0000`). -/
theorem arms_same_K (hn : 0 < n) (hP : 0 < Fintype.card P) (xhat xR : Fin n → P → E)
    (hR : (0.8894 : ℝ) ≤ R2bar xhat xR) : fstar (dev xhat xR) 0.3186 = 0 := by
  rw [theorem1 hn hP]; linarith

/-- Same-model values (`R²_V` median `0.8779 ≥ 1 - τ_V`): `f*(τ_V) = 0`, as reported. -/
theorem arms_same_V (hn : 0 < n) (hP : 0 < Fintype.card P) (xhat xR : Fin n → P → E)
    (hR : (0.8779 : ℝ) ≤ R2bar xhat xR) : fstar (dev xhat xR) 0.4867 = 0 := by
  rw [theorem1 hn hP]; linarith

/-- Cross-model keys (`R²_K` median `0.4214 < 1 - τ_K`): `f*(τ_K) > 0` (reported `0.9640`). -/
theorem arms_cross_K (hn : 0 < n) (hP : 0 < Fintype.card P) (xhat xR : Fin n → P → E)
    (hR : R2bar xhat xR ≤ 0.4214) : 0 < fstar (dev xhat xR) 0.3186 := by
  rw [theorem1_pos hn hP]; linarith

/-- Cross-model values (`R²_V` median `0.1478 < 1 - τ_V`): `f*(τ_V) > 0` (reported `0.9456`). -/
theorem arms_cross_V (hn : 0 < n) (hP : 0 < Fintype.card P) (xhat xR : Fin n → P → E)
    (hR : R2bar xhat xR ≤ 0.1478) : 0 < fstar (dev xhat xR) 0.4867 := by
  rw [theorem1_pos hn hP]; linarith

/-- Tolerance ladder, keys: the median `R²_K = 0.8894 < 0.9` puts `μ` above `0.1`, so
`f*(0.1) > 0`, matching the positive median `0.0119` of Table `tab:tau-ladder-long`. -/
theorem ladder_mid_K_pos (hn : 0 < n) (hP : 0 < Fintype.card P) (xhat xR : Fin n → P → E)
    (hR : R2bar xhat xR ≤ 0.8894) : 0 < fstar (dev xhat xR) 0.1 := by
  rw [theorem1_pos hn hP]; linarith

/-- Tolerance ladder, values: `R²_V = 0.8779 < 0.9`, so `f*(0.1) > 0` (reported `0.0254`). -/
theorem ladder_mid_V_pos (hn : 0 < n) (hP : 0 < Fintype.card P) (xhat xR : Fin n → P → E)
    (hR : R2bar xhat xR ≤ 0.8779) : 0 < fstar (dev xhat xR) 0.1 := by
  rw [theorem1_pos hn hP]; linarith

/-- Configuration bridge: `R²_K = 0.8932` and `R²_V = 0.8603` pass `τ_K` and `τ_V`, so `f* = 0`
for keys and values, as reported. -/
theorem bridge_zero (hn : 0 < n) (hP : 0 < Fintype.card P) (xK xRK xV xRV : Fin n → P → E)
    (hK : (0.8932 : ℝ) ≤ R2bar xK xRK) (hV : (0.8603 : ℝ) ≤ R2bar xV xRV) :
    fstar (dev xK xRK) 0.3186 = 0 ∧ fstar (dev xV xRV) 0.4867 = 0 :=
  ⟨by rw [theorem1 hn hP]; linarith, by rw [theorem1 hn hP]; linarith⟩

end Theorem1

/-! ### Theorem 1 against the matched configuration comparison (mean `δ_K` medians) -/

section Matched

variable {n : ℕ}

/-- Scaled short cell: `μ = 0.0895` is the same number as `R̄²_K = 0.9105` (`μ = 1 - R̄²`). -/
theorem scaled_short_identity : (0.9105 : ℝ) = 1 - 0.0895 := by norm_num

/-- Native (`μ = 0.0682`) and scaled (`μ = 0.0895`) short cells pass `τ_K`: median `f*(τ_K)`
stays zero. -/
theorem matched_zero (hn : 0 < n) (δ : Fin n → ℝ) (hμ : mu δ ≤ 0.0895) : fstar δ 0.3186 = 0 :=
  (fstar_eq_zero_iff hn δ _).mpr (by linarith)

/-- Scaled short cell at `τ = 0.1`: `μ = 0.0895 ≤ 0.1`, so `f*(0.1) = 0`, matching the
Qwen3-1.7B short entry `0.0000` of Table `tab:additional-models`. -/
theorem scaled_short_mid_zero (hn : 0 < n) (δ : Fin n → ℝ) (hμ : mu δ ≤ 0.0895) :
    fstar δ 0.1 = 0 :=
  (fstar_eq_zero_iff hn δ _).mpr (by linarith)

/-- Both short cells at `τ = 0.03`: `μ ≥ 0.0682 > 0.03`, so `f*(0.03) > 0` (reported `0.1433`
native and `0.2930` scaled). -/
theorem short_low_pos (hn : 0 < n) (δ : Fin n → ℝ) (hμ : (0.0682 : ℝ) ≤ mu δ) :
    0 < fstar δ 0.03 :=
  (fstar_pos_iff hn δ _).mpr (by linarith)

end Matched

/-! ### Theorem 2 against the tables -/

/-- Monotonicity in `τ` (Theorem 2) holds for every handoff, hence for medians and percentiles:
every row of Table `tab:additional-models` is nondecreasing from `τ_K` to `0.1` to `0.03`
(short cohort, then long cohort). -/
theorem additional_models_monotone :
    -- Qwen3-1.7B
    ((0 : ℝ) ≤ 0 ∧ (0 : ℝ) ≤ 0.2930) ∧ ((0 : ℝ) ≤ 0.0119 ∧ (0.0119 : ℝ) ≤ 0.5255) ∧
    -- Qwen3-4B
    ((0 : ℝ) ≤ 0.0007 ∧ (0.0007 : ℝ) ≤ 0.2739) ∧ ((0 : ℝ) ≤ 0.0460 ∧ (0.0460 : ℝ) ≤ 0.4979) ∧
    -- SmolLM3-3B
    ((0 : ℝ) ≤ 0 ∧ (0 : ℝ) ≤ 0.1527) ∧ ((0 : ℝ) ≤ 0.0580 ∧ (0.0580 : ℝ) ≤ 0.4529) := by
  norm_num

/-- The same for Table `tab:tau-ladder-long`, at the p10, median and p90 of keys and values. -/
theorem tau_ladder_monotone :
    -- keys: p10, median, p90
    ((0 : ℝ) ≤ 0 ∧ (0 : ℝ) ≤ 0.0762) ∧ ((0 : ℝ) ≤ 0.0119 ∧ (0.0119 : ℝ) ≤ 0.5255) ∧
    ((0 : ℝ) ≤ 0.3876 ∧ (0.3876 : ℝ) ≤ 0.9037) ∧
    -- values: p10, median, p90
    ((0 : ℝ) ≤ 0 ∧ (0 : ℝ) ≤ 0.1829) ∧ ((0 : ℝ) ≤ 0.0254 ∧ (0.0254 : ℝ) ≤ 0.5837) ∧
    ((0 : ℝ) ≤ 0.4289 ∧ (0.4289 : ℝ) ≤ 0.9071) := by
  norm_num

/-- Theorem 2's upper chain `f*(τ) ≤ p(τ) ≤ μ/τ` carries over to medians. In the matched
configuration comparison the median above-`τ_K` fractions (`0.0437` native, `0.0527` scaled) lie
between the median `f*(τ_K) = 0` and the median `μ/τ_K`. -/
theorem matched_upper_chain :
    (0 : ℝ) ≤ 0.0437 ∧ (0.0437 : ℝ) ≤ 0.0682 / 0.3186 ∧
    (0 : ℝ) ≤ 0.0527 ∧ (0.0527 : ℝ) ≤ 0.0895 / 0.3186 := by
  norm_num

/-! ### Matched configuration shares and seam levels -/

/-- `(scaled - native)/(long - native)` at the `16+` seam bin rounds to `0.43`, and at
`f*(0.03)` to `0.39`. -/
theorem matched_shares :
    |(0.0381 - 0.0195 : ℝ) / (0.0629 - 0.0195) - 0.43| < 0.005 ∧
    |(0.2930 - 0.1433 : ℝ) / (0.5255 - 0.1433) - 0.39| < 0.005 := by
  constructor <;> rw [abs_lt] <;> constructor <;> norm_num

/-- The far-from-seam level `0.0629` lies above the strict tolerance `0.03` and below `τ_K`, and
the seam diagnostic's median remaining-token mean `0.1016` exceeds `0.03`. -/
theorem seam_levels : (0.03 : ℝ) < 0.0629 ∧ (0.0629 : ℝ) < 0.3186 ∧ (0.03 : ℝ) < 0.1016 := by
  norm_num

/-- Corollary `cor:seam` with no near-seam tokens (`m w = 0`): a handoff whose every matched token
is within the far level `0.0629` has `f*(τ_K) = 0`. -/
theorem far_level_zero (n : ℕ) (hn : 0 < n) (δ : Fin n → ℝ) (hfar : ∀ t, δ t ≤ 0.0629) :
    fstar δ 0.3186 = 0 :=
  seam_zero_floor hn δ ∅ 0 0 (by simp) (le_refl (0.0629 : ℝ)) (fun t ht => absurd ht (by simp))
    (fun t _ => hfar t) (by norm_num)

end Carryover

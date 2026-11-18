import Carryover.Pred

/-!
# The per-token KL divergence between the fresh and the reused next-token distribution

At one position the reader's next-token distribution under its fresh cache is `softmax z` and under
the reused cache `softmax (z + e)`, with `e` the shift of the logits. This file proves what the
per-token statistic `kl (softmax z) (softmax (z + e))` can and cannot be, as a function of `e`:

* it is a cumulant gap, `log ∑ p_i exp(e_i) - ∑ p_i e_i` (`kl_softmax`);
* it is nonnegative, zero only when the two distributions agree, and it dominates the squared
  Hellinger distance, which dominates a quarter of the squared `L¹` distance (`hell_le_kl`,
  `kl_pos_of_ne`, `l1_sq_le_four_hell`, `l1_sq_le_four_kl`);
* it is at most the oscillation `w` of the shift, and at most `w ^ 2 / 8` (Hoeffding's lemma;
  `kl_softmax_le_osc`, `kl_softmax_le_osc_sq`), hence at most `ε ^ 2 / 2` when every logit moves by
  at most `ε` (`kl_softmax_le_of_abs`);
* the numbers the paper reads off these bounds (`control_floor`, `holds_threshold_needs_osc`,
  `degrades_threshold_needs_osc`, `holds_at_most_two`);
* the chain rule over one generated token (`kl_prod`) and its consequence that the per-position
  reading depends on the text that was generated (`kl_prod_pos_of_ne`, `kl_branch_zero`,
  `kl_prod_eq_single`);
* the chain rule over `T` generated tokens for a tree of conditionals indexed by prefixes
  (`seqProb`, `kl_seqProb`), and the same rule as an expectation over whole texts of the sum of
  the per-position readings (`seqProb_marginal`, `kl_seqProb_expect`, `meanKL_expect`).
-/

namespace Carryover.Pred

open Finset

variable {ι : Type*} [Fintype ι]

/-! ## Softmax and the cumulant form of the KL divergence -/

/-- A softmax over a nonempty vocabulary is a next-token distribution. -/
theorem softmax_isDist [Nonempty ι] (z : ι → ℝ) : IsDist (softmax z) where
  pos i :=
    div_pos (Real.exp_pos _) (Finset.sum_pos (fun j _ => Real.exp_pos _) Finset.univ_nonempty)
  sum_one := by
    have hS : 0 < ∑ j, Real.exp (z j) :=
      Finset.sum_pos (fun j _ => Real.exp_pos _) Finset.univ_nonempty
    unfold softmax
    rw [← Finset.sum_div, div_self hS.ne']

/-- Shifting the logits by `e` reweights the distribution by `exp e` and renormalizes. -/
theorem softmax_shift (z e : ι → ℝ) (i : ι) :
    softmax (z + e) i = softmax z i * Real.exp (e i) / ∑ j, softmax z j * Real.exp (e j) := by
  have hS : 0 < ∑ j, Real.exp (z j) :=
    Finset.sum_pos (fun j _ => Real.exp_pos _) ⟨i, Finset.mem_univ i⟩
  have hsum : ∑ j, softmax z j * Real.exp (e j) =
      (∑ j, Real.exp (z j + e j)) / ∑ j, Real.exp (z j) := by
    rw [Finset.sum_div]
    refine Finset.sum_congr rfl fun j _ => ?_
    rw [softmax, Real.exp_add]
    ring
  rw [hsum]
  simp only [softmax, Pi.add_apply]
  rw [Real.exp_add, div_mul_eq_mul_div, div_div_div_cancel_right₀ hS.ne']

/-- **The KL divergence is a cumulant gap.** With `p = softmax z`, the divergence from `p` to the
shifted distribution is `log E_p[exp e] - E_p[e]`. -/
theorem kl_softmax (z e : ι → ℝ) :
    kl (softmax z) (softmax (z + e)) =
      Real.log (∑ i, softmax z i * Real.exp (e i)) - ∑ i, softmax z i * e i := by
  rcases isEmpty_or_nonempty ι with hι | hι
  · simp [kl]
  have hp := softmax_isDist z
  obtain ⟨M, hM⟩ : ∃ M, M = ∑ j, softmax z j * Real.exp (e j) := ⟨_, rfl⟩
  have hMpos : 0 < M := by
    rw [hM]
    exact Finset.sum_pos (fun j _ => mul_pos (hp.pos j) (Real.exp_pos _)) Finset.univ_nonempty
  have hterm : ∀ i, softmax z i * Real.log (softmax z i / softmax (z + e) i) =
      softmax z i * Real.log M - softmax z i * e i := by
    intro i
    have hq : softmax z i / softmax (z + e) i = M / Real.exp (e i) := by
      rw [softmax_shift, ← hM]
      have h1 := (hp.pos i).ne'
      have h2 := (Real.exp_pos (e i)).ne'
      field_simp
    rw [hq, Real.log_div hMpos.ne' (Real.exp_pos _).ne', Real.log_exp]
    ring
  unfold kl
  rw [Finset.sum_congr rfl fun i _ => hterm i, Finset.sum_sub_distrib, ← Finset.sum_mul,
    hp.sum_one, one_mul, hM]

/-! ## KL against the Hellinger and the `L¹` distance -/

private lemma sq_sub_le_mul_log {s t : ℝ} (hs : 0 < s) (ht : 0 < t) :
    (s - t) ^ 2 + (s ^ 2 - t ^ 2) ≤ s ^ 2 * Real.log (s ^ 2 / t ^ 2) := by
  have h1 : Real.log (t / s) ≤ t / s - 1 := Real.log_le_sub_one_of_pos (div_pos ht hs)
  have h2 : Real.log (s ^ 2 / t ^ 2) = -2 * Real.log (t / s) := by
    rw [← div_pow, Real.log_pow, Real.log_div hs.ne' ht.ne', Real.log_div ht.ne' hs.ne']
    push_cast
    ring
  have h3 : s ^ 2 * (t / s - 1) = s * t - s ^ 2 := by
    field_simp
  have h4 := mul_le_mul_of_nonneg_left h1 (sq_nonneg s)
  rw [h3] at h4
  rw [h2]
  nlinarith

/-- The one-token step of `hell_le_kl`: from `log x ≤ x - 1` at `x = √(b / a)`. -/
private lemma sqrt_sub_sq_le {a b : ℝ} (ha : 0 < a) (hb : 0 < b) :
    (Real.sqrt a - Real.sqrt b) ^ 2 + (a - b) ≤ a * Real.log (a / b) := by
  have h := sq_sub_le_mul_log (Real.sqrt_pos.mpr ha) (Real.sqrt_pos.mpr hb)
  rwa [Real.sq_sqrt ha.le, Real.sq_sqrt hb.le] at h

/-- **KL dominates the squared Hellinger distance:** `∑ (√p_i - √q_i)² ≤ KL(p ‖ q)`. -/
theorem hell_le_kl {p q : ι → ℝ} (hp : IsDist p) (hq : IsDist q) : hell p q ≤ kl p q := by
  have h0 : ∑ i, (p i - q i) = 0 := by
    rw [Finset.sum_sub_distrib, hp.sum_one, hq.sum_one, sub_self]
  have h1 : hell p q = ∑ i, ((Real.sqrt (p i) - Real.sqrt (q i)) ^ 2 + (p i - q i)) := by
    rw [Finset.sum_add_distrib, h0, add_zero, hell]
  rw [h1]
  exact Finset.sum_le_sum fun i _ => sqrt_sub_sq_le (hp.pos i) (hq.pos i)

lemma hell_nonneg (p q : ι → ℝ) : 0 ≤ hell p q :=
  Finset.sum_nonneg fun _ _ => sq_nonneg _

/-- The KL divergence between two next-token distributions is nonnegative. -/
theorem kl_nonneg {p q : ι → ℝ} (hp : IsDist p) (hq : IsDist q) : 0 ≤ kl p q :=
  (hell_nonneg p q).trans (hell_le_kl hp hq)

/-- The KL divergence is positive as soon as the two distributions differ at one token. -/
theorem kl_pos_of_ne {p q : ι → ℝ} (hp : IsDist p) (hq : IsDist q) (h : p ≠ q) : 0 < kl p q := by
  obtain ⟨i, hi⟩ := Function.ne_iff.mp h
  have hsq : Real.sqrt (p i) ≠ Real.sqrt (q i) := fun hs =>
    hi ((Real.sqrt_inj (hp.pos i).le (hq.pos i).le).mp hs)
  have hpos : 0 < hell p q :=
    Finset.sum_pos' (fun _ _ => sq_nonneg _)
      ⟨i, Finset.mem_univ i, sq_pos_iff.mpr (sub_ne_zero.mpr hsq)⟩
  exact hpos.trans_le (hell_le_kl hp hq)

/-- A distribution has zero KL divergence from itself. -/
theorem kl_self {p : ι → ℝ} (hp : IsDist p) : kl p p = 0 := by
  unfold kl
  refine Finset.sum_eq_zero fun i _ => ?_
  rw [div_self (hp.pos i).ne', Real.log_one, mul_zero]

/-- **The squared `L¹` distance is at most four times the squared Hellinger distance**
(Cauchy-Schwarz on `|p_i - q_i| = |√p_i - √q_i| (√p_i + √q_i)`, and `∑ (√p_i + √q_i)² ≤ 4`). -/
theorem l1_sq_le_four_hell {p q : ι → ℝ} (hp : IsDist p) (hq : IsDist q) :
    (∑ i, |p i - q i|) ^ 2 ≤ 4 * hell p q := by
  have habs : ∀ i, |p i - q i| =
      |Real.sqrt (p i) - Real.sqrt (q i)| * (Real.sqrt (p i) + Real.sqrt (q i)) := by
    intro i
    have h1 : p i - q i =
        (Real.sqrt (p i) - Real.sqrt (q i)) * (Real.sqrt (p i) + Real.sqrt (q i)) := by
      nlinarith [Real.sq_sqrt (hp.pos i).le, Real.sq_sqrt (hq.pos i).le]
    rw [← abs_of_nonneg (add_nonneg (Real.sqrt_nonneg (p i)) (Real.sqrt_nonneg (q i))), ← abs_mul,
      ← h1]
  have hf : ∑ i, |Real.sqrt (p i) - Real.sqrt (q i)| ^ 2 = hell p q := by
    unfold hell
    exact Finset.sum_congr rfl fun i _ => sq_abs _
  have hg : ∑ i, (Real.sqrt (p i) + Real.sqrt (q i)) ^ 2 ≤ 4 := by
    calc ∑ i, (Real.sqrt (p i) + Real.sqrt (q i)) ^ 2
        ≤ ∑ i, (2 * p i + 2 * q i) := Finset.sum_le_sum fun i _ => by
          nlinarith [Real.sq_sqrt (hp.pos i).le, Real.sq_sqrt (hq.pos i).le,
            sq_nonneg (Real.sqrt (p i) - Real.sqrt (q i))]
      _ = 4 := by
          rw [Finset.sum_add_distrib, ← Finset.mul_sum, ← Finset.mul_sum, hp.sum_one, hq.sum_one]
          norm_num
  have hh0 := hell_nonneg p q
  calc (∑ i, |p i - q i|) ^ 2
      = (∑ i, |Real.sqrt (p i) - Real.sqrt (q i)| * (Real.sqrt (p i) + Real.sqrt (q i))) ^ 2 := by
        rw [Finset.sum_congr rfl fun i _ => habs i]
    _ ≤ (∑ i, |Real.sqrt (p i) - Real.sqrt (q i)| ^ 2) *
          ∑ i, (Real.sqrt (p i) + Real.sqrt (q i)) ^ 2 := Finset.sum_mul_sq_le_sq_mul_sq _ _ _
    _ = hell p q * ∑ i, (Real.sqrt (p i) + Real.sqrt (q i)) ^ 2 := by rw [hf]
    _ ≤ hell p q * 4 := mul_le_mul_of_nonneg_left hg hh0
    _ = 4 * hell p q := mul_comm _ _

/-- **A Pinsker-type bound:** the squared `L¹` distance is at most four times the KL divergence
(`l1_sq_le_four_hell`, then `hell_le_kl`). -/
theorem l1_sq_le_four_kl {p q : ι → ℝ} (hp : IsDist p) (hq : IsDist q) :
    (∑ i, |p i - q i|) ^ 2 ≤ 4 * kl p q :=
  (l1_sq_le_four_hell hp hq).trans (by linarith [hell_le_kl hp hq])

/-! ## KL against the oscillation of the logit shift -/

/-- **The per-token KL is at most the oscillation of the logit shift.** -/
theorem kl_softmax_le_osc [Nonempty ι] {z e : ι → ℝ} {w : ℝ} (h : OscLe e w) :
    kl (softmax z) (softmax (z + e)) ≤ w := by
  have hp := softmax_isDist z
  rw [kl_softmax]
  obtain ⟨ebar, hebar⟩ : ∃ ebar, ebar = ∑ i, softmax z i * e i := ⟨_, rfl⟩
  rw [← hebar]
  have hle : ∀ i, e i ≤ ebar + w := by
    intro i
    have h1 : ∑ j, softmax z j * (e i - w) ≤ ∑ j, softmax z j * e j :=
      Finset.sum_le_sum fun j _ =>
        mul_le_mul_of_nonneg_left (by linarith [h i j]) (hp.pos j).le
    rw [← Finset.sum_mul, hp.sum_one, one_mul, ← hebar] at h1
    linarith
  have hM : ∑ i, softmax z i * Real.exp (e i) ≤ Real.exp (ebar + w) := by
    calc ∑ i, softmax z i * Real.exp (e i)
        ≤ ∑ i, softmax z i * Real.exp (ebar + w) := Finset.sum_le_sum fun i _ =>
          mul_le_mul_of_nonneg_left (Real.exp_le_exp.mpr (hle i)) (hp.pos i).le
      _ = Real.exp (ebar + w) := by rw [← Finset.sum_mul, hp.sum_one, one_mul]
  have hMpos : 0 < ∑ i, softmax z i * Real.exp (e i) :=
    Finset.sum_pos (fun j _ => mul_pos (hp.pos j) (Real.exp_pos _)) Finset.univ_nonempty
  have h2 := Real.log_le_log hMpos hM
  rw [Real.log_exp] at h2
  linarith

/-- Hoeffding's lemma on a finite vocabulary: for a distribution `p` and a shift `e` of oscillation
at most `w`, the cumulant gap `log E_p[exp e] - E_p[e]` is at most `w ^ 2 / 8`. The measure is the
one with mass `p i` at token `i`; the bound is Mathlib's
`ProbabilityTheory.mgf_le_of_mem_Icc_of_integral_eq_zero`. -/
theorem log_sum_exp_sub_le [Nonempty ι] {p e : ι → ℝ} {w : ℝ} (hp : IsDist p) (h : OscLe e w) :
    Real.log (∑ i, p i * Real.exp (e i)) - ∑ i, p i * e i ≤ w ^ 2 / 8 := by
  let _ : MeasurableSpace ι := ⊤
  have : MeasurableSingletonClass ι := ⟨fun _ => MeasurableSpace.measurableSet_top⟩
  obtain ⟨m, -, hm⟩ := Finset.exists_min_image Finset.univ e Finset.univ_nonempty
  have hw : 0 ≤ w := by linarith [h m m]
  have hsum : ∑ i, ENNReal.ofReal (p i) = 1 := by
    rw [← ENNReal.ofReal_sum_of_nonneg fun i _ => (hp.pos i).le, hp.sum_one, ENNReal.ofReal_one]
  obtain ⟨μ, hμ⟩ : ∃ μ : MeasureTheory.Measure ι,
      μ = (PMF.ofFintype (fun i => ENNReal.ofReal (p i)) hsum).toMeasure := ⟨_, rfl⟩
  have : MeasureTheory.IsProbabilityMeasure μ := by
    rw [hμ]
    infer_instance
  have hint : ∀ f : ι → ℝ, ∫ i, f i ∂μ = ∑ i, p i * f i := by
    intro f
    rw [hμ, PMF.integral_eq_sum]
    refine Finset.sum_congr rfl fun i _ => ?_
    rw [PMF.ofFintype_apply, ENNReal.toReal_ofReal (hp.pos i).le, smul_eq_mul]
  obtain ⟨ebar, hebar⟩ : ∃ ebar, ebar = ∑ i, p i * e i := ⟨_, rfl⟩
  rw [← hebar]
  have hb : ∀ᵐ i ∂μ, e i - ebar ∈ Set.Icc (e m - ebar) (e m + w - ebar) :=
    Filter.Eventually.of_forall fun i =>
      ⟨by linarith [hm i (Finset.mem_univ i)], by linarith [h i m]⟩
  have hc : ∫ i, (e i - ebar) ∂μ = 0 := by
    rw [hint]
    simp only [mul_sub]
    rw [Finset.sum_sub_distrib, ← Finset.sum_mul, hp.sum_one, one_mul, ← hebar, sub_self]
  have key := ProbabilityTheory.mgf_le_of_mem_Icc_of_integral_eq_zero
    (X := fun i => e i - ebar) (μ := μ) measurable_from_top.aemeasurable hb hc one_pos
  have hmgf : ProbabilityTheory.mgf (fun i => e i - ebar) μ 1 =
      (∑ i, p i * Real.exp (e i)) * Real.exp (-ebar) := by
    unfold ProbabilityTheory.mgf
    rw [hint, Finset.sum_mul]
    refine Finset.sum_congr rfl fun i _ => ?_
    beta_reduce
    rw [one_mul, sub_eq_add_neg, Real.exp_add]
    ring
  have hbound : (∑ i, p i * Real.exp (e i)) * Real.exp (-ebar) ≤ Real.exp (w ^ 2 / 8) := by
    rw [← hmgf]
    refine key.trans (le_of_eq ?_)
    congr 1
    rw [show e m + w - ebar - (e m - ebar) = w by ring, coe_nnnorm, Real.norm_of_nonneg hw]
    ring
  have hMpos : 0 < ∑ i, p i * Real.exp (e i) :=
    Finset.sum_pos (fun j _ => mul_pos (hp.pos j) (Real.exp_pos _)) Finset.univ_nonempty
  have h2 := Real.log_le_log (mul_pos hMpos (Real.exp_pos _)) hbound
  rw [Real.log_mul hMpos.ne' (Real.exp_pos _).ne', Real.log_exp, Real.log_exp] at h2
  linarith

/-- **The per-token KL is at most `w ^ 2 / 8`** for a logit shift of oscillation at most `w`
(Hoeffding's lemma applied to the cumulant gap of `kl_softmax`). -/
theorem kl_softmax_le_osc_sq {z e : ι → ℝ} {w : ℝ} (h : OscLe e w) :
    kl (softmax z) (softmax (z + e)) ≤ w ^ 2 / 8 := by
  rcases isEmpty_or_nonempty ι with hι | hι
  · have h0 : kl (softmax z) (softmax (z + e)) = 0 := by simp [kl]
    rw [h0]
    positivity
  rw [kl_softmax]
  exact log_sum_exp_sub_le (softmax_isDist z) h

/-- **If every logit moves by at most `ε`, the per-token KL is at most `ε ^ 2 / 2`.** -/
theorem kl_softmax_le_of_abs {z e : ι → ℝ} {ε : ℝ} (h : ∀ i, |e i| ≤ ε) :
    kl (softmax z) (softmax (z + e)) ≤ ε ^ 2 / 2 := by
  have hosc : OscLe e (2 * ε) := fun i j => by
    linarith [h i, h j, le_abs_self (e i), neg_abs_le (e j)]
  calc kl (softmax z) (softmax (z + e)) ≤ (2 * ε) ^ 2 / 8 := kl_softmax_le_osc_sq hosc
    _ = ε ^ 2 / 2 := by ring

/-! ## The numbers -/

/-- A logit perturbation of at most `5e-4` per token moves the per-token KL by at most `1.25e-7`. -/
theorem control_floor {z e : ι → ℝ} (h : ∀ i, |e i| ≤ (5e-4 : ℝ)) :
    kl (softmax z) (softmax (z + e)) ≤ 1.25e-7 := by
  calc kl (softmax z) (softmax (z + e)) ≤ (5e-4 : ℝ) ^ 2 / 2 := kl_softmax_le_of_abs h
    _ = 1.25e-7 := by norm_num

/-- A per-token KL above `1e-3` needs a logit shift whose oscillation exceeds `0.089`. -/
theorem holds_threshold_needs_osc {z e : ι → ℝ}
    (h : (1e-3 : ℝ) < kl (softmax z) (softmax (z + e))) : ¬ OscLe e 0.089 := by
  intro hosc
  have h1 := kl_softmax_le_osc_sq (z := z) hosc
  have h2 : (0.089 : ℝ) ^ 2 / 8 < 1e-3 := by norm_num
  linarith

/-- A per-token KL of at least `1e-1` needs a logit shift whose oscillation exceeds `0.894`. -/
theorem degrades_threshold_needs_osc {z e : ι → ℝ}
    (h : (1e-1 : ℝ) ≤ kl (softmax z) (softmax (z + e))) : ¬ OscLe e 0.894 := by
  intro hosc
  have h1 := kl_softmax_le_osc_sq (z := z) hosc
  have h2 : (0.894 : ℝ) ^ 2 / 8 < 1e-1 := by norm_num
  linarith

/-- Markov's inequality on the tokens of one sequence: the number of positions whose reading is at
least `d`, times `d`, is at most the sum of the readings. -/
theorem card_ge_mul_le {T : ℕ} (D : Fin T → ℝ) (hD : ∀ t, 0 ≤ D t) (d : ℝ) :
    ((Finset.univ.filter fun t => d ≤ D t).card : ℝ) * d ≤ ∑ t, D t := by
  calc ((Finset.univ.filter fun t => d ≤ D t).card : ℝ) * d
      = ∑ _t ∈ Finset.univ.filter (fun t => d ≤ D t), d := by
        rw [Finset.sum_const, nsmul_eq_mul]
    _ ≤ ∑ t ∈ Finset.univ.filter (fun t => d ≤ D t), D t :=
        Finset.sum_le_sum fun t ht => (Finset.mem_filter.mp ht).2
    _ ≤ ∑ t, D t :=
        Finset.sum_le_sum_of_subset_of_nonneg (Finset.filter_subset _ _) fun t _ _ => hD t

/-- On 256 tokens, a mean per-token KL of at most `1e-3` leaves at most two positions with a
reading of `1e-1` or more. -/
theorem holds_at_most_two (D : Fin 256 → ℝ) (hD : ∀ t, 0 ≤ D t)
    (h : (∑ t, D t) / 256 ≤ (1e-3 : ℝ)) :
    (Finset.univ.filter fun t => (1e-1 : ℝ) ≤ D t).card ≤ 2 := by
  have h1 := card_ge_mul_le D hD 1e-1
  have h2 : ∑ t, D t ≤ 1e-3 * 256 := (div_le_iff₀ (by norm_num)).mp h
  by_contra hc
  have h3 : (3 : ℝ) ≤ ((Finset.univ.filter fun t => (1e-1 : ℝ) ≤ D t).card : ℝ) := by
    exact_mod_cast Nat.lt_of_not_le hc
  norm_num at h1 h2
  linarith

/-! ## The chain rule over one generated token -/

/-- **One-step chain rule.** For a first token drawn from `p₁` (or `q₁`) and a second drawn from
the conditional `p₂ a` (or `q₂ a`), the KL divergence of the two-token distributions is the KL at
the first position plus the `p₁`-average of the KL at the second. -/
theorem kl_prod {α β : Type*} [Fintype α] [Fintype β] {p₁ q₁ : α → ℝ} {p₂ q₂ : α → β → ℝ}
    (hp₁ : IsDist p₁) (hq₁ : IsDist q₁) (hp₂ : ∀ a, IsDist (p₂ a)) (hq₂ : ∀ a, IsDist (q₂ a)) :
    kl (fun x : α × β => p₁ x.1 * p₂ x.1 x.2) (fun x => q₁ x.1 * q₂ x.1 x.2) =
      kl p₁ q₁ + ∑ a, p₁ a * kl (p₂ a) (q₂ a) := by
  unfold kl
  rw [Fintype.sum_prod_type, ← Finset.sum_add_distrib]
  refine Finset.sum_congr rfl fun a _ => ?_
  have hterm : ∀ b, p₁ a * p₂ a b * Real.log (p₁ a * p₂ a b / (q₁ a * q₂ a b)) =
      p₂ a b * (p₁ a * Real.log (p₁ a / q₁ a)) +
        p₁ a * (p₂ a b * Real.log (p₂ a b / q₂ a b)) := by
    intro b
    rw [mul_div_mul_comm, Real.log_mul (div_pos (hp₁.pos a) (hq₁.pos a)).ne'
      (div_pos ((hp₂ a).pos b) ((hq₂ a).pos b)).ne']
    ring
  refine (Finset.sum_congr rfl fun b _ => hterm b).trans ?_
  rw [Finset.sum_add_distrib, ← Finset.sum_mul, (hp₂ a).sum_one, one_mul, Finset.mul_sum]

/-- **The two-token KL is positive when one continuation distribution differs,** even if the two
first-token distributions are the same. -/
theorem kl_prod_pos_of_ne {α β : Type*} [Fintype α] [Fintype β] {p₁ q₁ : α → ℝ}
    {p₂ q₂ : α → β → ℝ} (hp₁ : IsDist p₁) (hq₁ : IsDist q₁) (hp₂ : ∀ a, IsDist (p₂ a))
    (hq₂ : ∀ a, IsDist (q₂ a)) (h₁ : p₁ = q₁) {a : α} (ha : p₂ a ≠ q₂ a) :
    0 < kl (fun x : α × β => p₁ x.1 * p₂ x.1 x.2) (fun x => q₁ x.1 * q₂ x.1 x.2) := by
  rw [kl_prod hp₁ hq₁ hp₂ hq₂, h₁, kl_self hq₁, zero_add, ← h₁]
  exact Finset.sum_pos' (fun a _ => mul_nonneg (hp₁.pos a).le (kl_nonneg (hp₂ a) (hq₂ a)))
    ⟨a, Finset.mem_univ a, mul_pos (hp₁.pos a) (kl_pos_of_ne (hp₂ a) (hq₂ a) ha)⟩

/-- **The reading depends on the text.** If the first-token distributions agree and the
continuation distributions agree after the token `b`, a text that starts with `b` reads zero at
both positions; by `kl_prod_pos_of_ne` the two-token distributions can still differ. -/
theorem kl_branch_zero {α β : Type*} [Fintype α] [Fintype β] {p₁ q₁ : α → ℝ}
    {p₂ q₂ : α → β → ℝ} (hp₁ : IsDist p₁) (hp₂ : ∀ a, IsDist (p₂ a)) (h₁ : p₁ = q₁) {b : α}
    (hb : p₂ b = q₂ b) : kl p₁ q₁ = 0 ∧ kl (p₂ b) (q₂ b) = 0 := by
  rw [← h₁, ← hb]
  exact ⟨kl_self hp₁, kl_self (hp₂ b)⟩

/-- **The paper's example.** If the first-token distributions agree and the continuation
distributions agree after every first token except `a`, the two-token KL is the probability of `a`
times the KL between the two continuation distributions after `a`. -/
theorem kl_prod_eq_single {α β : Type*} [Fintype α] [Fintype β] {p₁ q₁ : α → ℝ}
    {p₂ q₂ : α → β → ℝ} (hp₁ : IsDist p₁) (hq₁ : IsDist q₁) (hp₂ : ∀ a, IsDist (p₂ a))
    (hq₂ : ∀ a, IsDist (q₂ a)) (h₁ : p₁ = q₁) (a : α) (hb : ∀ b, b ≠ a → p₂ b = q₂ b) :
    kl (fun x : α × β => p₁ x.1 * p₂ x.1 x.2) (fun x => q₁ x.1 * q₂ x.1 x.2) =
      p₁ a * kl (p₂ a) (q₂ a) := by
  rw [kl_prod hp₁ hq₁ hp₂ hq₂, h₁, kl_self hq₁, zero_add]
  exact Finset.sum_eq_single a
    (fun b _ hba => by rw [hb b hba, kl_self (hq₂ b), mul_zero])
    (fun ha => absurd (Finset.mem_univ a) ha)

/-! ## The chain rule over `T` generated tokens -/

/-- The probability of the token sequence `x` of length `T` under a tree of conditionals
`P : prefix ↦ next-token distribution`: the first token is drawn from `P []`, and the rest from the
tree below it, `pre ↦ P (x 0 :: pre)`. Unfolded, `seqProb P T x = ∏_t P [x_0, …, x_{t-1}] (x_t)`. -/
noncomputable def seqProb (P : List ι → ι → ℝ) : (T : ℕ) → (Fin T → ι) → ℝ
  | 0, _ => 1
  | T + 1, x => P [] (x 0) * seqProb (fun pre => P (x 0 :: pre)) T (Fin.tail x)

omit [Fintype ι] in
lemma seqProb_cons (P : List ι → ι → ℝ) {T : ℕ} (a : ι) (y : Fin T → ι) :
    seqProb P (T + 1) (Fin.cons a y) = P [] a * seqProb (fun pre => P (a :: pre)) T y := by
  rw [seqProb, Fin.cons_zero, Fin.tail_cons]

/-- A sum over sequences of length `T + 1` is a sum over the first token and the rest. -/
private lemma sum_fin_succ_fun {T : ℕ} (F : (Fin (T + 1) → ι) → ℝ) :
    ∑ x, F x = ∑ a, ∑ y : Fin T → ι, F (Fin.cons a y) :=
  calc ∑ x, F x = ∑ ay : ι × (Fin T → ι), F (Fin.cons ay.1 ay.2) :=
        (Fintype.sum_equiv (Fin.consEquiv fun _ => ι) _ _ fun _ => rfl).symm
    _ = ∑ a, ∑ y : Fin T → ι, F (Fin.cons a y) := Fintype.sum_prod_type _

/-- The sequence probabilities of a tree of next-token distributions form a distribution. -/
theorem seqProb_isDist {P : List ι → ι → ℝ} (hP : ∀ pre, IsDist (P pre)) (T : ℕ) :
    IsDist (seqProb P T) := by
  induction T generalizing P with
  | zero => exact ⟨fun _ => by simp [seqProb], by simp [seqProb]⟩
  | succ T ih =>
    refine ⟨fun x => ?_, ?_⟩
    · rw [seqProb]
      exact mul_pos ((hP []).pos _) ((ih fun pre => hP (x 0 :: pre)).pos _)
    · have h : ∀ a, ∑ y : Fin T → ι, seqProb P (T + 1) (Fin.cons a y) = P [] a := by
        intro a
        rw [Finset.sum_congr rfl fun y _ => seqProb_cons P a y, ← Finset.mul_sum,
          (ih fun pre => hP (a :: pre)).sum_one, mul_one]
      rw [sum_fin_succ_fun, Finset.sum_congr rfl fun a _ => h a, (hP []).sum_one]

/-- The chain rule at the first of `T + 1` tokens: `kl_prod` with the rest of the sequence as the
second coordinate. -/
theorem kl_seqProb_succ {P Q : List ι → ι → ℝ} (hP : ∀ pre, IsDist (P pre))
    (hQ : ∀ pre, IsDist (Q pre)) (T : ℕ) :
    kl (seqProb P (T + 1)) (seqProb Q (T + 1)) =
      kl (P []) (Q []) + ∑ a, P [] a *
        kl (seqProb (fun pre => P (a :: pre)) T) (seqProb (fun pre => Q (a :: pre)) T) := by
  rw [← kl_prod (hP []) (hQ []) (fun a => seqProb_isDist (fun pre => hP (a :: pre)) T)
    (fun a => seqProb_isDist (fun pre => hQ (a :: pre)) T)]
  unfold kl
  refine (Fintype.sum_equiv (Fin.consEquiv fun _ => ι) _ _ fun ay => ?_).symm
  change _ = seqProb P (T + 1) (Fin.cons ay.1 ay.2) *
    Real.log (seqProb P (T + 1) (Fin.cons ay.1 ay.2) / seqProb Q (T + 1) (Fin.cons ay.1 ay.2))
  rw [seqProb_cons, seqProb_cons]

/-- **The `T`-step chain rule.** For two trees of next-token distributions `P` and `Q` (the reader
under its fresh and under the reused cache, as functions of the generated prefix), the KL
divergence between the two distributions over length-`T` continuations is the sum over positions
`t < T` of the per-token KL at the prefix `x`, averaged over prefixes `x` of length `t` drawn from
`P`. The per-token reading on one generated text is one term of the inner sum. -/
theorem kl_seqProb {P Q : List ι → ι → ℝ} (hP : ∀ pre, IsDist (P pre))
    (hQ : ∀ pre, IsDist (Q pre)) (T : ℕ) :
    kl (seqProb P T) (seqProb Q T) =
      ∑ t ∈ Finset.range T, ∑ x : Fin t → ι,
        seqProb P t x * kl (P (List.ofFn x)) (Q (List.ofFn x)) := by
  induction T generalizing P Q with
  | zero => simp [kl, seqProb]
  | succ T ih =>
    have h0 : ∑ x : Fin 0 → ι, seqProb P 0 x * kl (P (List.ofFn x)) (Q (List.ofFn x)) =
        kl (P []) (Q []) := by
      simp [seqProb]
    have hstep : ∀ t, ∑ x : Fin (t + 1) → ι,
        seqProb P (t + 1) x * kl (P (List.ofFn x)) (Q (List.ofFn x)) =
        ∑ a, P [] a * ∑ y : Fin t → ι, seqProb (fun pre => P (a :: pre)) t y *
          kl (P (a :: List.ofFn y)) (Q (a :: List.ofFn y)) := by
      intro t
      rw [sum_fin_succ_fun]
      refine Finset.sum_congr rfl fun a _ => ?_
      rw [Finset.mul_sum]
      refine Finset.sum_congr rfl fun y _ => ?_
      rw [seqProb_cons, List.ofFn_cons, mul_assoc]
    rw [kl_seqProb_succ hP hQ, Finset.sum_range_succ', h0, add_comm (kl (P []) (Q []))]
    congr 1
    calc ∑ a, P [] a *
          kl (seqProb (fun pre => P (a :: pre)) T) (seqProb (fun pre => Q (a :: pre)) T)
        = ∑ a, ∑ t ∈ Finset.range T, P [] a * ∑ y : Fin t → ι,
            seqProb (fun pre => P (a :: pre)) t y *
              kl (P (a :: List.ofFn y)) (Q (a :: List.ofFn y)) := by
          refine Finset.sum_congr rfl fun a _ => ?_
          rw [ih (fun pre => hP (a :: pre)) (fun pre => hQ (a :: pre)), Finset.mul_sum]
      _ = ∑ t ∈ Finset.range T, ∑ a, P [] a * ∑ y : Fin t → ι,
            seqProb (fun pre => P (a :: pre)) t y *
              kl (P (a :: List.ofFn y)) (Q (a :: List.ofFn y)) := Finset.sum_comm
      _ = ∑ t ∈ Finset.range T, ∑ x : Fin (t + 1) → ι,
            seqProb P (t + 1) x * kl (P (List.ofFn x)) (Q (List.ofFn x)) :=
          Finset.sum_congr rfl fun t _ => (hstep t).symm

/-! ## The chain rule as an expectation over whole texts -/

/-- **The first `t` tokens of a length-`T` text are distributed as a length-`t` text.** In
test-function form: for `t ≤ T` and any function `g` of a prefix, the `seqProb P T`-average of `g`
at the first `t` tokens of the text equals the `seqProb P t`-average of `g`. (Summing
`seqProb P T` over the tokens after position `t` gives `seqProb P t` of the prefix.) -/
theorem seqProb_marginal {P : List ι → ι → ℝ} (hP : ∀ pre, IsDist (P pre)) {t T : ℕ} (h : t ≤ T)
    (g : List ι → ℝ) :
    ∑ y : Fin T → ι, seqProb P T y * g ((List.ofFn y).take t) =
      ∑ x : Fin t → ι, seqProb P t x * g (List.ofFn x) := by
  induction t generalizing P T g with
  | zero =>
    simp only [List.take_zero]
    rw [← Finset.sum_mul, (seqProb_isDist hP T).sum_one]
    simp [seqProb]
  | succ t ih =>
    obtain ⟨T', rfl⟩ : ∃ T', T = T' + 1 := ⟨T - 1, by omega⟩
    rw [sum_fin_succ_fun, sum_fin_succ_fun]
    refine Finset.sum_congr rfl fun a _ => ?_
    have hL : ∀ y : Fin T' → ι, seqProb P (T' + 1) (Fin.cons a y) *
        g ((List.ofFn (Fin.cons a y : Fin (T' + 1) → ι)).take (t + 1)) =
        P [] a * (seqProb (fun pre => P (a :: pre)) T' y * g (a :: (List.ofFn y).take t)) := by
      intro y
      rw [seqProb_cons, List.ofFn_cons, List.take_succ_cons, mul_assoc]
    have hR : ∀ x : Fin t → ι, seqProb P (t + 1) (Fin.cons a x) *
        g (List.ofFn (Fin.cons a x : Fin (t + 1) → ι)) =
        P [] a * (seqProb (fun pre => P (a :: pre)) t x * g (a :: List.ofFn x)) := by
      intro x
      rw [seqProb_cons, List.ofFn_cons, mul_assoc]
    rw [Finset.sum_congr rfl fun y _ => hL y, Finset.sum_congr rfl fun x _ => hR x,
      ← Finset.mul_sum, ← Finset.mul_sum]
    congr 1
    exact ih (fun pre => hP (a :: pre)) (Nat.le_of_succ_le_succ h) fun l => g (a :: l)

/-- **The chain rule as the paper states it.** The KL divergence between the two distributions
over length-`T` texts is the expectation, over a text `y` drawn from `P`, of the sum over the
positions `t < T` of the per-token KL read on that text, i.e. at the prefix
`(List.ofFn y).take t` of `y` before position `t`. -/
theorem kl_seqProb_expect {P Q : List ι → ι → ℝ} (hP : ∀ pre, IsDist (P pre))
    (hQ : ∀ pre, IsDist (Q pre)) (T : ℕ) :
    kl (seqProb P T) (seqProb Q T) =
      ∑ y : Fin T → ι, seqProb P T y *
        ∑ t : Fin T, kl (P ((List.ofFn y).take t)) (Q ((List.ofFn y).take t)) := by
  rw [kl_seqProb hP hQ]
  calc ∑ t ∈ Finset.range T, ∑ x : Fin t → ι,
        seqProb P t x * kl (P (List.ofFn x)) (Q (List.ofFn x))
      = ∑ t ∈ Finset.range T, ∑ y : Fin T → ι,
          seqProb P T y * kl (P ((List.ofFn y).take t)) (Q ((List.ofFn y).take t)) :=
        Finset.sum_congr rfl fun t ht =>
          (seqProb_marginal hP (Finset.mem_range.mp ht).le fun l => kl (P l) (Q l)).symm
    _ = ∑ y : Fin T → ι, ∑ t ∈ Finset.range T,
          seqProb P T y * kl (P ((List.ofFn y).take t)) (Q ((List.ofFn y).take t)) :=
        Finset.sum_comm
    _ = ∑ y : Fin T → ι, seqProb P T y *
          ∑ t : Fin T, kl (P ((List.ofFn y).take t)) (Q ((List.ofFn y).take t)) := by
        refine Finset.sum_congr rfl fun y _ => ?_
        rw [← Finset.mul_sum]
        congr 1
        exact (Fin.sum_univ_eq_sum_range
          (fun t => kl (P ((List.ofFn y).take t)) (Q ((List.ofFn y).take t))) T).symm

/-- **The mean per-token KL.** The expectation over texts of the mean over positions of the
per-token reading is the KL divergence between the two text distributions divided by `T`. -/
theorem meanKL_expect {P Q : List ι → ι → ℝ} (hP : ∀ pre, IsDist (P pre))
    (hQ : ∀ pre, IsDist (Q pre)) (T : ℕ) :
    ∑ y : Fin T → ι, seqProb P T y *
        ((∑ t : Fin T, kl (P ((List.ofFn y).take t)) (Q ((List.ofFn y).take t))) / T) =
      kl (seqProb P T) (seqProb Q T) / T := by
  rw [kl_seqProb_expect hP hQ T, Finset.sum_div]
  exact Finset.sum_congr rfl fun y _ => (mul_div_assoc _ _ _).symm

end Carryover.Pred

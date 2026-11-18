import Carryover.Pred

/-!
# Greedy tokens and answer flips under a fresh and a reused cache

At one position the reader's next-token distribution is `p` under its fresh cache and `q` under the
reused cache; the greedy token is a token of largest probability. Under greedy decoding a generated
sequence is `gen dec T` for a next-token rule `dec`, and an answer is a function `A` of the sequence.
An answer flip is `A (gen dec T) ≠ A (gen dec' T)` for the fresh rule `dec` and the reused rule `dec'`.

What this file states, in that order:

* the greedy token is the argmax of the logits (`softmax_lt_iff`, `softmax_le_iff`);
* a logit shift whose oscillation is under the fresh logit margin leaves the greedy token unchanged
  (`argmax_stable`, `argmax_stable_of_abs`);
* a change of greedy token at one position forces a lower bound on `hell p q` at that position
  (`flip_forces_hell`), while no bound on `kl p q` alone excludes one (`near_tie_flip`);
* two greedy runs that differ share a prefix up to a first position where the two rules, given the
  same prefix, choose different tokens (`first_divergence`), so an answer flip forces such a position
  (`answer_flip_first_divergence`) and the `hell` lower bound there (`answer_flip_forces_hell`);
* over a set of problems, the number of answer flips is at most the number of problems whose two
  sequences differ (`flips_le_divergences`);
* one numeric inequality, the value of the Hoeffding tail expression at `n = 1319`, `t = 0.0375`
  (`hoeffding_tail_1319`).
-/

namespace Carryover.Pred

open Finset

variable {ι : Type*} [Fintype ι]

/-! ## The greedy token is the argmax of the logits -/

lemma sum_exp_pos [Nonempty ι] (z : ι → ℝ) : 0 < ∑ j, Real.exp (z j) :=
  Finset.sum_pos (fun j _ => Real.exp_pos (z j)) Finset.univ_nonempty

/-- Softmax preserves strict order: token `a` has strictly larger probability than token `b` exactly
when it has the strictly larger logit. -/
theorem softmax_lt_iff (z : ι → ℝ) (a b : ι) : softmax z b < softmax z a ↔ z b < z a := by
  have : Nonempty ι := ⟨a⟩
  unfold softmax
  rw [div_lt_div_iff_of_pos_right (sum_exp_pos z), Real.exp_lt_exp]

/-- Softmax preserves order: `softmax z b ≤ softmax z a` exactly when `z b ≤ z a`. With
`softmax_lt_iff`, the greedy token of `softmax z` is the argmax of the logits `z`. -/
theorem softmax_le_iff (z : ι → ℝ) (a b : ι) : softmax z b ≤ softmax z a ↔ z b ≤ z a := by
  have : Nonempty ι := ⟨a⟩
  unfold softmax
  rw [div_le_div_iff_of_pos_right (sum_exp_pos z), Real.exp_le_exp]

/-! ## A shift under the margin cannot change the greedy token -/

omit [Fintype ι] in
/-- If token `a` leads every other token by at least `g` in the fresh logits `z`, and the reused
logits are `z + e` with the oscillation of the shift `e` at most `w < g`, then `a` is still the
strict argmax of the reused logits: the greedy token does not change. -/
theorem argmax_stable {z e : ι → ℝ} {a : ι} {g w : ℝ} (hmargin : ∀ b, b ≠ a → g ≤ z a - z b)
    (hosc : OscLe e w) (hw : w < g) : ∀ b, b ≠ a → (z + e) b < (z + e) a := by
  intro b hb
  have h1 := hmargin b hb
  have h2 := hosc b a
  simp only [Pi.add_apply]
  linarith

omit [Fintype ι] in
/-- A shift bounded by `ε` in absolute value on every token has oscillation at most `2 ε`. -/
lemma oscLe_of_abs {e : ι → ℝ} {ε : ℝ} (habs : ∀ i, |e i| ≤ ε) : OscLe e (2 * ε) := by
  intro i j
  have hi := (abs_le.mp (habs i)).2
  have hj := (abs_le.mp (habs j)).1
  linarith

omit [Fintype ι] in
/-- The same conclusion from a sup-norm bound: if every logit moves by at most `ε` and `2 ε` is under
the fresh logit margin `g`, the greedy token does not change. -/
theorem argmax_stable_of_abs {z e : ι → ℝ} {a : ι} {g ε : ℝ}
    (hmargin : ∀ b, b ≠ a → g ≤ z a - z b) (habs : ∀ i, |e i| ≤ ε) (hε : 2 * ε < g) :
    ∀ b, b ≠ a → (z + e) b < (z + e) a :=
  argmax_stable hmargin (oscLe_of_abs habs) hε

/-! ## A flip at one position: forced `hell`, but no forced `kl` -/

/-- If the greedy token is `a` under the fresh distribution `p` (`p b ≤ p a`) and a different token
`b` under the reused distribution `q` (`q a ≤ q b`), then `hell p q`, twice the squared Hellinger
distance, is at least half the squared gap `(√p_a - √p_b)²` between the two tokens under `p`.

The terms `i = a` and `i = b` of the sum are `x²` and `y²` with `x = √p_a - √q_a`,
`y = √p_b - √q_b`; `x² + y² ≥ (x - y)² / 2` and `x - y = (√p_a - √p_b) + (√q_b - √q_a)`, a sum of two
nonnegative brackets. The proof uses only the two order hypotheses; `_hp` and `_hq` are not
used and are kept so that the statement reads on distributions. -/
theorem flip_forces_hell {p q : ι → ℝ} (_hp : IsDist p) (_hq : IsDist q) {a b : ι} (hab : a ≠ b)
    (hpa : p b ≤ p a) (hqb : q a ≤ q b) :
    (Real.sqrt (p a) - Real.sqrt (p b)) ^ 2 / 2 ≤ hell p q := by
  classical
  have hu : 0 ≤ Real.sqrt (p a) - Real.sqrt (p b) := sub_nonneg.mpr (Real.sqrt_le_sqrt hpa)
  have hv : 0 ≤ Real.sqrt (q b) - Real.sqrt (q a) := sub_nonneg.mpr (Real.sqrt_le_sqrt hqb)
  have hsub : ∑ i ∈ ({a, b} : Finset ι), (Real.sqrt (p i) - Real.sqrt (q i)) ^ 2 ≤ hell p q :=
    Finset.sum_le_univ_sum_of_nonneg fun i => sq_nonneg _
  rw [Finset.sum_pair hab] at hsub
  nlinarith [sq_nonneg (Real.sqrt (p a) - Real.sqrt (q a) + (Real.sqrt (p b) - Real.sqrt (q b))),
    mul_nonneg hu hv, sq_nonneg (Real.sqrt (q b) - Real.sqrt (q a))]

/-- No bound on the KL divergence alone excludes a flip: for every `η > 0` there are two
distributions on a two-token vocabulary with `kl p q ≤ η` whose greedy tokens differ. The pair is
`p = (1/2 - γ, 1/2 + γ)` and its mirror image `q`, with
`kl p q = 2 γ log ((1/2 + γ) / (1/2 - γ)) ≤ 16 γ²` for `γ ≤ 1/4`. -/
theorem near_tie_flip (η : ℝ) (hη : 0 < η) :
    ∃ p q : Bool → ℝ, IsDist p ∧ IsDist q ∧ kl p q ≤ η ∧ p false < p true ∧ q true < q false := by
  obtain ⟨γ, hγ0, hγ4, hγη⟩ : ∃ γ : ℝ, 0 < γ ∧ γ ≤ 1 / 4 ∧ 16 * γ ^ 2 ≤ η := by
    have h0 : 0 < min (1 / 4 : ℝ) (η / 4) := lt_min (by norm_num) (by positivity)
    have h1 : min (1 / 4 : ℝ) (η / 4) ≤ 1 / 4 := min_le_left _ _
    have h2 : min (1 / 4 : ℝ) (η / 4) ≤ η / 4 := min_le_right _ _
    refine ⟨min (1 / 4 : ℝ) (η / 4), h0, h1, ?_⟩
    nlinarith [mul_le_mul h1 h2 h0.le (by norm_num : (0 : ℝ) ≤ 1 / 4)]
  have ha : 0 < 1 / 2 - γ := by linarith
  have hb : 0 < 1 / 2 + γ := by linarith
  refine ⟨fun i => if i then 1 / 2 + γ else 1 / 2 - γ, fun i => if i then 1 / 2 - γ else 1 / 2 + γ,
    ⟨?_, ?_⟩, ⟨?_, ?_⟩, ?_, ?_, ?_⟩
  · intro i
    cases i
    · simpa using ha
    · simpa using hb
  · rw [Fintype.sum_bool]
    simp only [ite_true, Bool.false_eq_true, ite_false]
    ring
  · intro i
    cases i
    · simpa using hb
    · simpa using ha
  · rw [Fintype.sum_bool]
    simp only [ite_true, Bool.false_eq_true, ite_false]
    ring
  · have hlog : Real.log (1 / 2 + γ) - Real.log (1 / 2 - γ) ≤ 8 * γ := by
      rw [← Real.log_div hb.ne' ha.ne']
      have h1 := Real.log_le_sub_one_of_pos (div_pos hb ha)
      have h2 : (1 / 2 + γ) / (1 / 2 - γ) ≤ 1 + 8 * γ := by
        rw [div_le_iff₀ ha]
        nlinarith [mul_nonneg hγ0.le (by linarith : (0 : ℝ) ≤ 1 / 4 - γ)]
      linarith
    unfold kl
    rw [Fintype.sum_bool]
    simp only [ite_true, Bool.false_eq_true, ite_false]
    rw [Real.log_div hb.ne' ha.ne', Real.log_div ha.ne' hb.ne']
    nlinarith [mul_le_mul_of_nonneg_left hlog hγ0.le]
  · simp only [ite_true, Bool.false_eq_true, ite_false]
    linarith
  · simp only [ite_true, Bool.false_eq_true, ite_false]
    linarith

/-! ## Greedy generation: the first divergence -/

/-- After `t` greedy steps the generated sequence has `t` tokens. -/
theorem gen_length {α : Type*} (dec : List α → α) (t : ℕ) : (gen dec t).length = t := by
  induction t with
  | zero => rfl
  | succ t ih => simp [gen, ih]

/-- Two greedy runs of length `T` that differ share a prefix up to a first position `t < T` at which
the two next-token rules, given the same prefix, choose different tokens. -/
theorem first_divergence {α : Type*} {dec dec' : List α → α} {T : ℕ}
    (h : gen dec T ≠ gen dec' T) :
    ∃ t, t < T ∧ gen dec t = gen dec' t ∧ dec (gen dec t) ≠ dec' (gen dec t) := by
  induction T with
  | zero => exact (h rfl).elim
  | succ T ih =>
    by_cases hT : gen dec T = gen dec' T
    · refine ⟨T, Nat.lt_succ_self T, hT, fun hd => h ?_⟩
      show gen dec T ++ [dec (gen dec T)] = gen dec' T ++ [dec' (gen dec' T)]
      rw [← hT, hd]
    · obtain ⟨t, ht, h1, h2⟩ := ih hT
      exact ⟨t, Nat.lt_succ_of_lt ht, h1, h2⟩

/-- An answer flip forces a first divergence: if the answer `A` read off the fresh run differs from
the answer read off the reused run, the two runs share a prefix up to a position where the two rules,
given the same prefix, choose different tokens. -/
theorem answer_flip_first_divergence {α γ : Type*} {dec dec' : List α → α} {T : ℕ}
    (A : List α → γ) (h : A (gen dec T) ≠ A (gen dec' T)) :
    ∃ t, t < T ∧ gen dec t = gen dec' t ∧ dec (gen dec t) ≠ dec' (gen dec t) :=
  first_divergence fun heq => h (congrArg A heq)

/-- An answer flip under greedy decoding forces a `hell` lower bound at one position. `P s` and `Q s`
are the fresh and the reused next-token distributions after the prefix `s`, and `dec`, `dec'` are
greedy for them. If the two answers differ there is a position `t < T` with a common prefix
`s = gen dec t` at which the greedy tokens differ and
`(√P_s(dec s) - √P_s(dec' s))² / 2 ≤ hell (P s) (Q s)`: both distributions are taken on the fresh
run's own prefix. -/
theorem answer_flip_forces_hell {α γ : Type*} [Fintype α] {P Q : List α → α → ℝ}
    (hP : ∀ s, IsDist (P s)) (hQ : ∀ s, IsDist (Q s)) {dec dec' : List α → α}
    (hdec : ∀ s b, P s b ≤ P s (dec s)) (hdec' : ∀ s b, Q s b ≤ Q s (dec' s)) {T : ℕ}
    (A : List α → γ) (h : A (gen dec T) ≠ A (gen dec' T)) :
    ∃ t, t < T ∧ gen dec t = gen dec' t ∧ dec (gen dec t) ≠ dec' (gen dec t) ∧
      (Real.sqrt (P (gen dec t) (dec (gen dec t))) -
        Real.sqrt (P (gen dec t) (dec' (gen dec t)))) ^ 2 / 2 ≤
        hell (P (gen dec t)) (Q (gen dec t)) := by
  obtain ⟨t, ht, hpre, hne⟩ := answer_flip_first_divergence A h
  exact ⟨t, ht, hpre, hne, flip_forces_hell (hP _) (hQ _) hne (hdec _ _) (hdec' _ _)⟩

/-! ## Counting over problems -/

/-- Over `n` problems with fresh sequences `x i` and reused sequences `x' i`, the number of problems
whose answer flips is at most the number of problems whose two sequences differ: the answer flip rate
is at most the share of problems with a divergence. -/
theorem flips_le_divergences {n : ℕ} {α γ : Type*} [DecidableEq γ] [DecidableEq α]
    (x x' : Fin n → List α) (A : List α → γ) :
    (Finset.univ.filter fun i => A (x i) ≠ A (x' i)).card ≤
      (Finset.univ.filter fun i => x i ≠ x' i).card := by
  apply Finset.card_le_card
  intro i hi
  simp only [Finset.mem_filter, Finset.mem_univ, true_and] at hi ⊢
  exact fun heq => hi (congrArg A heq)

/-! ## One numeric value -/

/-- The expression `2 exp (-2 n t²)` at `n = 1319`, `t = 0.0375` is at most `0.05`. This is the
right-hand side of Hoeffding's two-sided tail bound for the mean of `n` independent variables with
values in `[0, 1]`; the bound itself is not proved here, only this value of its right-hand side. -/
theorem hoeffding_tail_1319 : 2 * Real.exp (-2 * 1319 * (0.0375 : ℝ) ^ 2) ≤ 0.05 := by
  have hx : (-2 * 1319 * (0.0375 : ℝ) ^ 2) = -(11871 / 3200) := by norm_num
  rw [hx, Real.exp_neg]
  have h40 : (40 : ℝ) ≤ Real.exp (11871 / 3200) := by
    have h := Real.sum_le_exp_of_nonneg (x := (11871 / 3200 : ℝ)) (by norm_num) 12
    refine le_trans ?_ h
    simp only [Finset.sum_range_succ, Finset.sum_range_zero, Nat.factorial]
    norm_num
  have hinv : (Real.exp (11871 / 3200))⁻¹ ≤ (40 : ℝ)⁻¹ := inv_anti₀ (by norm_num) h40
  norm_num at hinv ⊢
  linarith

end Carryover.Pred

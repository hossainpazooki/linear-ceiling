import Carryover.PredMain

/-!
# Runs and texts that end early

`PredFlip.lean` and `PredMain.lean` state the facts about greedy runs for runs of a fixed length, and
`PredKL.lean` states the chain rule for texts of a fixed length. A run can end before its token limit
(an end token, a stop string). This file states the same facts with a stopping rule.

Greedy runs. `genStop dec stop T` is the greedy run of at most `T` tokens under a rule `stop` that
reads only the tokens generated so far; once `stop` holds the run is not extended.

* a run that has not ended after `t` steps is the fixed-length run `gen dec t`
  (`genStop_eq_gen_of_live`), so it has `t` tokens (`genStop_length_of_live`);
* the run after `t` steps is a prefix of the run after `T ≥ t` steps (`genStop_prefix`);
* two runs that differ share a prefix up to a first position at which neither has ended and the two
  rules, given the same prefix, choose different tokens (`first_divergence_stop`);
* two runs are equal exactly when the second rule chooses the first rule's token at every prefix of
  the first run that has not ended (`genStop_eq_iff`);
* an answer flip forces such a position (`answer_flip_first_divergence_stop`), with the `hell` and
  the KL lower bound there (`answer_flip_forces_hell_stop`, `answer_flip_forces_kl_stop`) and a logit
  shift that reaches the fresh margin there (`answer_flip_needs_osc_stop`);
* all of that in one statement on the two final runs, for a reader given by its logits
  (`answer_flip_stop`).

Sampled texts. `ended pre` says that a text has ended once it reads `pre`. `padTree ended P R` follows
the tree of conditionals `P` while the text has not ended and a tree `R` afterwards; with the same `R`
for the fresh and the reused reader, what comes after the end is drawn from one law under both.

* the KL divergence between the two distributions over texts is the expectation, over a text drawn
  from the fresh reader, of the sum of the per-token KL over the positions before the text's end
  (`kl_seqProb_stop`);
* the expectation of the mean per-token KL over the text's own length lies between that KL
  divergence divided by `T` and the KL divergence itself (`meanKL_stop_bounds`); that length is at
  least one and at most `T` (`liveCount_pos`, `liveCount_le`), and is `T` for a text none of whose
  prefixes has ended (`liveCount_of_live`).
-/

namespace Carryover.Pred

open Finset

/-! ## Greedy runs with a stopping rule -/

/-- Greedy generation of at most `t` tokens with a stopping rule. `stop s = true` says that the run
has ended once it has generated `s`; a run that has ended is not extended. -/
def genStop {α : Type*} (dec : List α → α) (stop : List α → Bool) : ℕ → List α
  | 0 => []
  | t + 1 => if stop (genStop dec stop t) then genStop dec stop t
      else genStop dec stop t ++ [dec (genStop dec stop t)]

lemma genStop_succ {α : Type*} (dec : List α → α) (stop : List α → Bool) (t : ℕ) :
    genStop dec stop (t + 1) = if stop (genStop dec stop t) then genStop dec stop t
      else genStop dec stop t ++ [dec (genStop dec stop t)] := rfl

lemma genStop_succ_of_stop {α : Type*} {dec : List α → α} {stop : List α → Bool} {t : ℕ}
    (h : stop (genStop dec stop t) = true) : genStop dec stop (t + 1) = genStop dec stop t := by
  rw [genStop_succ]
  simp [h]

lemma genStop_succ_of_live {α : Type*} {dec : List α → α} {stop : List α → Bool} {t : ℕ}
    (h : stop (genStop dec stop t) = false) :
    genStop dec stop (t + 1) = genStop dec stop t ++ [dec (genStop dec stop t)] := by
  rw [genStop_succ]
  simp [h]

/-- A run that has not ended after `t + 1` steps had not ended after `t` steps. -/
lemma genStop_live_pred {α : Type*} {dec : List α → α} {stop : List α → Bool} {t : ℕ}
    (h : stop (genStop dec stop (t + 1)) = false) : stop (genStop dec stop t) = false := by
  rcases Bool.eq_false_or_eq_true (stop (genStop dec stop t)) with hs | hs
  · rw [genStop_succ_of_stop hs, hs] at h
    exact absurd h (by decide)
  · exact hs

/-- A run that has not ended after `t` steps is the fixed-length greedy run of `t` tokens. -/
theorem genStop_eq_gen_of_live {α : Type*} {dec : List α → α} {stop : List α → Bool} {t : ℕ}
    (h : stop (genStop dec stop t) = false) : genStop dec stop t = gen dec t := by
  induction t with
  | zero => rfl
  | succ t ih =>
    have hl := genStop_live_pred h
    rw [genStop_succ_of_live hl, ih hl, gen_succ]

/-- A run that has not ended after `t` steps has `t` tokens. -/
theorem genStop_length_of_live {α : Type*} {dec : List α → α} {stop : List α → Bool} {t : ℕ}
    (h : stop (genStop dec stop t) = false) : (genStop dec stop t).length = t := by
  rw [genStop_eq_gen_of_live h, gen_length]

/-- After `t` steps a run has at most `t` tokens. -/
lemma genStop_length_le {α : Type*} (dec : List α → α) (stop : List α → Bool) (t : ℕ) :
    (genStop dec stop t).length ≤ t := by
  induction t with
  | zero => simp [genStop]
  | succ t ih =>
    rcases Bool.eq_false_or_eq_true (stop (genStop dec stop t)) with hs | hs
    · rw [genStop_succ_of_stop hs]; omega
    · rw [genStop_succ_of_live hs, List.length_append, List.length_singleton]; omega

/-- The run after `t` steps is a prefix of the run after any `T ≥ t` steps: tokens once generated
stay, and a run that has ended stays as it is. -/
theorem genStop_prefix {α : Type*} (dec : List α → α) (stop : List α → Bool) {t T : ℕ}
    (h : t ≤ T) : genStop dec stop t <+: genStop dec stop T := by
  induction T with
  | zero =>
    have ht : t = 0 := Nat.le_zero.mp h
    subst ht
    exact List.prefix_refl _
  | succ m ih =>
    rcases Nat.lt_or_ge t (m + 1) with hlt | hge
    · have hstep : genStop dec stop m <+: genStop dec stop (m + 1) := by
        rcases Bool.eq_false_or_eq_true (stop (genStop dec stop m)) with hs | hs
        · simp [genStop_succ_of_stop hs]
        · rw [genStop_succ_of_live hs]
          exact List.prefix_append _ _
      exact (ih (Nat.lt_succ_iff.mp hlt)).trans hstep
    · have ht : t = m + 1 := Nat.le_antisymm h hge
      subst ht
      exact List.prefix_refl _

/-- Two runs with a stopping rule that differ share a prefix up to a first position `t < T` at which
the common prefix has not ended and the two next-token rules, given that prefix, choose different
tokens. -/
theorem first_divergence_stop {α : Type*} {dec dec' : List α → α} {stop : List α → Bool} {T : ℕ}
    (h : genStop dec stop T ≠ genStop dec' stop T) :
    ∃ t, t < T ∧ genStop dec stop t = genStop dec' stop t ∧ stop (genStop dec stop t) = false ∧
      dec (genStop dec stop t) ≠ dec' (genStop dec stop t) := by
  induction T with
  | zero => exact (h rfl).elim
  | succ T ih =>
    by_cases hT : genStop dec stop T = genStop dec' stop T
    · rcases Bool.eq_false_or_eq_true (stop (genStop dec stop T)) with hs | hs
      · have hs' : stop (genStop dec' stop T) = true := by rw [← hT]; exact hs
        exfalso
        apply h
        rw [genStop_succ_of_stop hs, genStop_succ_of_stop hs']
        exact hT
      · have hs' : stop (genStop dec' stop T) = false := by rw [← hT]; exact hs
        refine ⟨T, Nat.lt_succ_self T, hT, hs, fun hd => h ?_⟩
        rw [genStop_succ_of_live hs, genStop_succ_of_live hs', ← hT, hd]
    · obtain ⟨t, ht, h1, h2, h3⟩ := ih hT
      exact ⟨t, Nat.lt_succ_of_lt ht, h1, h2, h3⟩

/-- Two runs that agree after `m + 1` steps agree after `m` steps. -/
lemma genStop_eq_of_succ {α : Type*} {dec dec' : List α → α} {stop : List α → Bool} {m : ℕ}
    (h : genStop dec stop (m + 1) = genStop dec' stop (m + 1)) :
    genStop dec stop m = genStop dec' stop m := by
  rcases Bool.eq_false_or_eq_true (stop (genStop dec stop m)) with hs | hs <;>
    rcases Bool.eq_false_or_eq_true (stop (genStop dec' stop m)) with hs' | hs'
  · rwa [genStop_succ_of_stop hs, genStop_succ_of_stop hs'] at h
  · exfalso
    rw [genStop_succ_of_stop hs, genStop_succ_of_live hs'] at h
    have h1 := genStop_length_le dec stop m
    have h2 := genStop_length_of_live hs'
    have h3 := congrArg List.length h
    rw [List.length_append, List.length_singleton, h2] at h3
    omega
  · exfalso
    rw [genStop_succ_of_live hs, genStop_succ_of_stop hs'] at h
    have h1 := genStop_length_le dec' stop m
    have h2 := genStop_length_of_live hs
    have h3 := congrArg List.length h
    rw [List.length_append, List.length_singleton, h2] at h3
    omega
  · rw [genStop_succ_of_live hs, genStop_succ_of_live hs'] at h
    have hl : (genStop dec stop m).length = (genStop dec' stop m).length := by
      rw [genStop_length_of_live hs, genStop_length_of_live hs']
    exact (List.append_inj h hl).1

/-- Two runs that agree after `T` steps agree after every `k ≤ T` steps. -/
lemma genStop_eq_of_le {α : Type*} {dec dec' : List α → α} {stop : List α → Bool} {T : ℕ}
    (h : genStop dec stop T = genStop dec' stop T) :
    ∀ k, k ≤ T → genStop dec stop k = genStop dec' stop k := by
  induction T with
  | zero => intro k hk; rw [Nat.le_zero.mp hk]; exact h
  | succ m ih =>
    intro k hk
    rcases Nat.lt_or_ge k (m + 1) with hlt | hge
    · exact ih (genStop_eq_of_succ h) k (Nat.lt_succ_iff.mp hlt)
    · rw [Nat.le_antisymm hk hge]; exact h

/-- Two greedy runs with a stopping rule are equal exactly when the second rule chooses the first
rule's token at every prefix of the first run that has not ended: whether the runs differ is decided
on the first run alone, up to its end. -/
theorem genStop_eq_iff {α : Type*} {dec dec' : List α → α} {stop : List α → Bool} {T : ℕ} :
    genStop dec stop T = genStop dec' stop T ↔
      ∀ t, t < T → stop (genStop dec stop t) = false →
        dec (genStop dec stop t) = dec' (genStop dec stop t) := by
  constructor
  · intro h t ht hlive
    have h1 := genStop_eq_of_le h (t + 1) ht
    have h0 := genStop_eq_of_succ h1
    have hlive' : stop (genStop dec' stop t) = false := by rw [← h0]; exact hlive
    rw [genStop_succ_of_live hlive, genStop_succ_of_live hlive'] at h1
    have hl : (genStop dec stop t).length = (genStop dec' stop t).length := by rw [h0]
    have h2 := (List.append_inj h1 hl).2
    rw [← h0] at h2
    simpa using h2
  · intro h
    by_contra hne
    obtain ⟨t, ht, _, hlive, hd⟩ := first_divergence_stop hne
    exact hd (h t ht hlive)

/-- An answer flip between two runs with a stopping rule forces a first divergence before either run
has ended. -/
theorem answer_flip_first_divergence_stop {α γ : Type*} {dec dec' : List α → α}
    {stop : List α → Bool} {T : ℕ} (A : List α → γ)
    (h : A (genStop dec stop T) ≠ A (genStop dec' stop T)) :
    ∃ t, t < T ∧ genStop dec stop t = genStop dec' stop t ∧ stop (genStop dec stop t) = false ∧
      dec (genStop dec stop t) ≠ dec' (genStop dec stop t) :=
  first_divergence_stop fun heq => h (congrArg A heq)

/-- `answer_flip_forces_hell` for runs with a stopping rule: the position lies before the end of
both runs, and both distributions are taken on the fresh run's own prefix. -/
theorem answer_flip_forces_hell_stop {α γ : Type*} [Fintype α] {P Q : List α → α → ℝ}
    (hP : ∀ s, IsDist (P s)) (hQ : ∀ s, IsDist (Q s)) {dec dec' : List α → α}
    (hdec : ∀ s b, P s b ≤ P s (dec s)) (hdec' : ∀ s b, Q s b ≤ Q s (dec' s))
    {stop : List α → Bool} {T : ℕ} (A : List α → γ)
    (h : A (genStop dec stop T) ≠ A (genStop dec' stop T)) :
    ∃ t, t < T ∧ genStop dec stop t = genStop dec' stop t ∧ stop (genStop dec stop t) = false ∧
      dec (genStop dec stop t) ≠ dec' (genStop dec stop t) ∧
      (Real.sqrt (P (genStop dec stop t) (dec (genStop dec stop t))) -
        Real.sqrt (P (genStop dec stop t) (dec' (genStop dec stop t)))) ^ 2 / 2 ≤
        hell (P (genStop dec stop t)) (Q (genStop dec stop t)) := by
  obtain ⟨t, ht, hpre, hlive, hne⟩ := answer_flip_first_divergence_stop A h
  exact ⟨t, ht, hpre, hlive, hne, flip_forces_hell (hP _) (hQ _) hne (hdec _ _) (hdec' _ _)⟩

/-- `answer_flip_forces_kl` for runs with a stopping rule. -/
theorem answer_flip_forces_kl_stop {α γ : Type*} [Fintype α] {P Q : List α → α → ℝ}
    (hP : ∀ s, IsDist (P s)) (hQ : ∀ s, IsDist (Q s)) {dec dec' : List α → α}
    (hdec : ∀ s b, P s b ≤ P s (dec s)) (hdec' : ∀ s b, Q s b ≤ Q s (dec' s))
    {stop : List α → Bool} {T : ℕ} (A : List α → γ)
    (h : A (genStop dec stop T) ≠ A (genStop dec' stop T)) :
    ∃ t, t < T ∧ genStop dec stop t = genStop dec' stop t ∧ stop (genStop dec stop t) = false ∧
      dec (genStop dec stop t) ≠ dec' (genStop dec stop t) ∧
      (Real.sqrt (P (genStop dec stop t) (dec (genStop dec stop t))) -
        Real.sqrt (P (genStop dec stop t) (dec' (genStop dec stop t)))) ^ 2 / 2 ≤
        kl (P (genStop dec stop t)) (Q (genStop dec stop t)) := by
  obtain ⟨t, ht, hpre, hlive, hne, hh⟩ := answer_flip_forces_hell_stop hP hQ hdec hdec' A h
  exact ⟨t, ht, hpre, hlive, hne, hh.trans (hell_le_kl (hP _) (hQ _))⟩

/-- `answer_flip_needs_osc` for runs with a stopping rule. -/
theorem answer_flip_needs_osc_stop {α γ : Type*} [Fintype α] {Z E : List α → α → ℝ}
    {dec dec' : List α → α}
    (hdec' : ∀ s b, softmax (Z s + E s) b ≤ softmax (Z s + E s) (dec' s))
    {stop : List α → Bool} {T : ℕ} (A : List α → γ)
    (h : A (genStop dec stop T) ≠ A (genStop dec' stop T)) :
    ∃ t, t < T ∧ genStop dec stop t = genStop dec' stop t ∧ stop (genStop dec stop t) = false ∧
      dec (genStop dec stop t) ≠ dec' (genStop dec stop t) ∧
      ∀ g w : ℝ,
        (∀ c, c ≠ dec (genStop dec stop t) →
          g ≤ Z (genStop dec stop t) (dec (genStop dec stop t)) - Z (genStop dec stop t) c) →
        OscLe (E (genStop dec stop t)) w → g ≤ w := by
  obtain ⟨t, ht, hpre, hlive, hne⟩ := answer_flip_first_divergence_stop A h
  refine ⟨t, ht, hpre, hlive, hne, fun g w hm ho => ?_⟩
  exact flip_needs_osc hm ho (Ne.symm hne) ((softmax_le_iff _ _ _).mp (hdec' _ _))

/-- **An answer flip between two runs with one stopping rule, in one statement.** The reader has fresh
logits `Z s` and reused logits `Z s + E s` after the text `s`; `dec` and `dec'` are greedy for them.
If the answers read off the two runs differ, there is a number of steps `t < T` after which the two
runs hold one common text `s = genStop dec stop t` that has not ended and has `t` tokens; `s`
followed by the fresh greedy token is a prefix of the fresh run and `s` followed by the reused
greedy token is a prefix of the reused run; the two tokens differ; the KL divergence at `s` is at
least `(√π_a - √π_b)² / 2` for the two tokens' fresh probabilities; and any bound `w` on the
oscillation of the shift `E s` is at least any margin `g` by which the fresh token leads. -/
theorem answer_flip_stop {α γ : Type*} [Fintype α] {Z E : List α → α → ℝ} {dec dec' : List α → α}
    (hdec : ∀ s b, softmax (Z s) b ≤ softmax (Z s) (dec s))
    (hdec' : ∀ s b, softmax (Z s + E s) b ≤ softmax (Z s + E s) (dec' s))
    {stop : List α → Bool} {T : ℕ} (A : List α → γ)
    (h : A (genStop dec stop T) ≠ A (genStop dec' stop T)) :
    ∃ t, t < T ∧ genStop dec stop t = genStop dec' stop t ∧ stop (genStop dec stop t) = false ∧
      (genStop dec stop t).length = t ∧
      genStop dec stop t ++ [dec (genStop dec stop t)] <+: genStop dec stop T ∧
      genStop dec stop t ++ [dec' (genStop dec stop t)] <+: genStop dec' stop T ∧
      dec (genStop dec stop t) ≠ dec' (genStop dec stop t) ∧
      (Real.sqrt (softmax (Z (genStop dec stop t)) (dec (genStop dec stop t))) -
        Real.sqrt (softmax (Z (genStop dec stop t)) (dec' (genStop dec stop t)))) ^ 2 / 2 ≤
        kl (softmax (Z (genStop dec stop t)))
          (softmax (Z (genStop dec stop t) + E (genStop dec stop t))) ∧
      ∀ g w : ℝ,
        (∀ c, c ≠ dec (genStop dec stop t) →
          g ≤ Z (genStop dec stop t) (dec (genStop dec stop t)) - Z (genStop dec stop t) c) →
        OscLe (E (genStop dec stop t)) w → g ≤ w := by
  have : Nonempty α := ⟨dec []⟩
  obtain ⟨t, ht, hpre, hlive, hne⟩ := answer_flip_first_divergence_stop A h
  have hlive' : stop (genStop dec' stop t) = false := by rw [← hpre]; exact hlive
  have h1 : genStop dec stop t ++ [dec (genStop dec stop t)] <+: genStop dec stop T := by
    rw [← genStop_succ_of_live hlive]
    exact genStop_prefix dec stop (t := t + 1) (T := T) ht
  have h2 : genStop dec stop t ++ [dec' (genStop dec stop t)] <+: genStop dec' stop T := by
    have h3 := genStop_prefix dec' stop (t := t + 1) (T := T) ht
    rw [genStop_succ_of_live hlive', ← hpre] at h3
    exact h3
  refine ⟨t, ht, hpre, hlive, genStop_length_of_live hlive, h1, h2, hne, ?_, fun g w hm ho => ?_⟩
  · exact flip_forces_kl (softmax_isDist _) (softmax_isDist _) hne (hdec _ _) (hdec' _ _)
  · exact flip_needs_osc hm ho (Ne.symm hne) ((softmax_le_iff _ _ _).mp (hdec' _ _))

/-! ## Sampled texts that end early -/

/-- A tree of conditionals that follows `P` while the text has not ended and `R` once it has. -/
def padTree {ι : Type*} (ended : List ι → Bool) (P R : List ι → ι → ℝ) (pre : List ι) : ι → ℝ :=
  if ended pre then R pre else P pre

/-- The number of positions of the text `y` before its end: the positions `t` whose prefix
`y_{<t}` has not ended. These are the positions at which a token is generated and scored. -/
def liveCount {ι : Type*} (ended : List ι → Bool) {T : ℕ} (y : Fin T → ι) : ℕ :=
  ((Finset.univ : Finset (Fin T)).filter
    fun t : Fin T => ended ((List.ofFn y).take (t : ℕ)) = false).card

variable {ι : Type*} [Fintype ι]

/-- The sum of the per-token KL over the positions of the text `y` before its end. -/
noncomputable def liveSum (ended : List ι → Bool) (P Q : List ι → ι → ℝ) {T : ℕ}
    (y : Fin T → ι) : ℝ :=
  ∑ t : Fin T, if ended ((List.ofFn y).take t) then 0
    else kl (P ((List.ofFn y).take t)) (Q ((List.ofFn y).take t))

omit [Fintype ι] in
lemma padTree_of_ended {ended : List ι → Bool} {P R : List ι → ι → ℝ} {pre : List ι}
    (h : ended pre = true) : padTree ended P R pre = R pre := by
  simp [padTree, h]

omit [Fintype ι] in
lemma padTree_of_live {ended : List ι → Bool} {P R : List ι → ι → ℝ} {pre : List ι}
    (h : ended pre = false) : padTree ended P R pre = P pre := by
  simp [padTree, h]

omit [Fintype ι] in
/-- With the empty text not ended and `T ≥ 1`, at least one position of a text is before its end. -/
theorem liveCount_pos {ended : List ι → Bool} (h0 : ended [] = false) {T : ℕ} (hT : 0 < T)
    (y : Fin T → ι) : 1 ≤ liveCount ended y := by
  unfold liveCount
  refine Finset.card_pos.mpr ⟨⟨0, hT⟩, ?_⟩
  simp [h0]

omit [Fintype ι] in
/-- At most `T` positions of a text are before its end. -/
theorem liveCount_le (ended : List ι → Bool) {T : ℕ} (y : Fin T → ι) : liveCount ended y ≤ T := by
  unfold liveCount
  exact (Finset.card_filter_le _ _).trans (by simp)

omit [Fintype ι] in
/-- A text none of whose prefixes has ended has all `T` positions before its end. -/
theorem liveCount_of_live {ended : List ι → Bool} {T : ℕ} (y : Fin T → ι)
    (h : ∀ t : Fin T, ended ((List.ofFn y).take (t : ℕ)) = false) : liveCount ended y = T := by
  unfold liveCount
  rw [Finset.filter_true_of_mem fun t _ => h t]
  simp

lemma padTree_isDist {P R : List ι → ι → ℝ} (hP : ∀ pre, IsDist (P pre))
    (hR : ∀ pre, IsDist (R pre)) (ended : List ι → Bool) (pre : List ι) :
    IsDist (padTree ended P R pre) := by
  rcases Bool.eq_false_or_eq_true (ended pre) with he | he
  · rw [padTree_of_ended he]; exact hR pre
  · rw [padTree_of_live he]; exact hP pre

/-- **The chain rule for texts that end early.** `P` and `Q` are the fresh and the reused reader as
trees of next-token distributions, and after a text has ended both continue with the same tree `R`.
The KL divergence between the two distributions over texts is the expectation, over a text drawn
from the fresh reader, of the sum of the per-token KL over the positions before the text's end. -/
theorem kl_seqProb_stop {P Q R : List ι → ι → ℝ} (hP : ∀ pre, IsDist (P pre))
    (hQ : ∀ pre, IsDist (Q pre)) (hR : ∀ pre, IsDist (R pre)) (ended : List ι → Bool) (T : ℕ) :
    kl (seqProb (padTree ended P R) T) (seqProb (padTree ended Q R) T) =
      ∑ y : Fin T → ι, seqProb (padTree ended P R) T y * liveSum ended P Q y := by
  rw [kl_seqProb_expect (padTree_isDist hP hR ended) (padTree_isDist hQ hR ended) T]
  refine Finset.sum_congr rfl fun y _ => ?_
  congr 1
  unfold liveSum
  refine Finset.sum_congr rfl fun t _ => ?_
  rcases Bool.eq_false_or_eq_true (ended ((List.ofFn y).take t)) with he | he
  · rw [padTree_of_ended he, padTree_of_ended he, kl_self (hR _)]
    simp [he]
  · rw [padTree_of_live he, padTree_of_live he]
    simp [he]

/-- **The mean over a text's own length.** With `ended [] = false` and `T ≥ 1`, the expectation over a
text drawn from the fresh reader of the per-token KL averaged over the positions before the text's
end lies between the KL divergence of the two text distributions divided by `T` and that KL
divergence. It equals the first when no text ends early. -/
theorem meanKL_stop_bounds {P Q R : List ι → ι → ℝ} (hP : ∀ pre, IsDist (P pre))
    (hQ : ∀ pre, IsDist (Q pre)) (hR : ∀ pre, IsDist (R pre)) (ended : List ι → Bool)
    (h0 : ended [] = false) {T : ℕ} (hT : 0 < T) :
    kl (seqProb (padTree ended P R) T) (seqProb (padTree ended Q R) T) / T ≤
        ∑ y : Fin T → ι, seqProb (padTree ended P R) T y *
          (liveSum ended P Q y / liveCount ended y) ∧
      ∑ y : Fin T → ι, seqProb (padTree ended P R) T y *
          (liveSum ended P Q y / liveCount ended y) ≤
        kl (seqProb (padTree ended P R) T) (seqProb (padTree ended Q R) T) := by
  have hw : ∀ y : Fin T → ι, 0 < seqProb (padTree ended P R) T y :=
    fun y => (seqProb_isDist (padTree_isDist hP hR ended) T).pos y
  have hS : ∀ y : Fin T → ι, 0 ≤ liveSum ended P Q y := by
    intro y
    unfold liveSum
    refine Finset.sum_nonneg fun t _ => ?_
    split_ifs
    · exact le_refl 0
    · exact kl_nonneg (hP _) (hQ _)
  have hn1 : ∀ y : Fin T → ι, 1 ≤ liveCount ended y := liveCount_pos h0 hT
  have hnT : ∀ y : Fin T → ι, liveCount ended y ≤ T := liveCount_le ended
  rw [kl_seqProb_stop hP hQ hR ended T]
  constructor
  · rw [Finset.sum_div]
    refine Finset.sum_le_sum fun y _ => ?_
    rw [mul_div_assoc]
    refine mul_le_mul_of_nonneg_left ?_ (hw y).le
    have h1 : (0 : ℝ) < liveCount ended y := by exact_mod_cast hn1 y
    have h2 : (liveCount ended y : ℝ) ≤ T := by exact_mod_cast hnT y
    exact div_le_div_of_nonneg_left (hS y) h1 h2
  · refine Finset.sum_le_sum fun y _ => ?_
    refine mul_le_mul_of_nonneg_left ?_ (hw y).le
    have h1 : (1 : ℝ) ≤ liveCount ended y := by exact_mod_cast hn1 y
    exact div_le_self (hS y) h1

omit [Fintype ι] in
/-- When no text ends early, every position is before the end. -/
theorem liveCount_of_never_ended {ended : List ι → Bool} (h : ∀ pre, ended pre = false) {T : ℕ}
    (y : Fin T → ι) : liveCount ended y = T :=
  liveCount_of_live y fun _ => h _

end Carryover.Pred

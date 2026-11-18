import Carryover.PredKL
import Carryover.PredFlip

/-!
# The KL divergence and greedy flips, joined

`PredKL.lean` bounds the per-token KL divergence from below by `hell`, and `PredFlip.lean` bounds `hell`
from below at a position where the greedy token changes. This file states the consequences in terms of
the KL divergence, the form in which the paper reads them, and two facts about greedy runs:

* a change of greedy token at one position forces `kl p q ≥ (√p_a - √p_b)² / 2` (`flip_forces_kl`) and
  needs a logit shift whose oscillation reaches the fresh logit margin (`flip_needs_osc`);
* two greedy runs are equal exactly when the reused rule agrees with the fresh rule at every prefix of
  the fresh run (`gen_eq_iff`): whether the runs differ is decided on the fresh path alone;
* an answer flip forces a position on the fresh path with a common prefix, different greedy tokens and
  the KL lower bound there (`answer_flip_forces_kl`).
-/

namespace Carryover.Pred

open Finset

variable {ι : Type*} [Fintype ι]

/-- If the greedy token is `a` under the fresh distribution `p` and a different token `b` under the
reused distribution `q`, the KL divergence at that position is at least `(√p_a - √p_b)² / 2`. -/
theorem flip_forces_kl {p q : ι → ℝ} (hp : IsDist p) (hq : IsDist q) {a b : ι} (hab : a ≠ b)
    (hpa : p b ≤ p a) (hqb : q a ≤ q b) :
    (Real.sqrt (p a) - Real.sqrt (p b)) ^ 2 / 2 ≤ kl p q :=
  (flip_forces_hell hp hq hab hpa hqb).trans (hell_le_kl hp hq)

omit [Fintype ι] in
/-- If token `a` leads every other token by at least `g` in the fresh logits and some other token `b`
is at least as large as `a` in the reused logits `z + e`, then the oscillation of the shift is at least
the margin: `g ≤ w` for every bound `w` on the oscillation. -/
theorem flip_needs_osc {z e : ι → ℝ} {a b : ι} {g w : ℝ} (hmargin : ∀ c, c ≠ a → g ≤ z a - z c)
    (hosc : OscLe e w) (hb : b ≠ a) (hflip : (z + e) a ≤ (z + e) b) : g ≤ w := by
  by_contra hlt
  exact absurd (argmax_stable hmargin hosc (not_le.mp hlt) b hb) (not_lt.mpr hflip)

lemma gen_succ {α : Type*} (dec : List α → α) (t : ℕ) :
    gen dec (t + 1) = gen dec t ++ [dec (gen dec t)] := rfl

/-- Two runs that agree after `m + 1` steps agree after `m` steps and chose the same token at step
`m + 1`. -/
lemma gen_eq_of_succ {α : Type*} {dec dec' : List α → α} {m : ℕ}
    (h : gen dec (m + 1) = gen dec' (m + 1)) :
    gen dec m = gen dec' m ∧ dec (gen dec m) = dec' (gen dec' m) := by
  rw [gen_succ, gen_succ] at h
  have hl : (gen dec m).length = (gen dec' m).length := by rw [gen_length, gen_length]
  obtain ⟨h1, h2⟩ := List.append_inj h hl
  exact ⟨h1, by simpa using h2⟩

/-- Two runs that agree after `T` steps agree after every `k ≤ T` steps. -/
lemma gen_eq_of_le {α : Type*} {dec dec' : List α → α} {T : ℕ} (h : gen dec T = gen dec' T) :
    ∀ k, k ≤ T → gen dec k = gen dec' k := by
  induction T with
  | zero => intro k hk; rw [Nat.le_zero.mp hk]; exact h
  | succ m ih =>
    intro k hk
    rcases Nat.lt_or_ge k (m + 1) with hlt | hge
    · exact ih (gen_eq_of_succ h).1 k (Nat.lt_succ_iff.mp hlt)
    · rw [Nat.le_antisymm hk hge]; exact h

/-- Two greedy runs of length `T` are equal exactly when the second rule chooses the first rule's token
at every prefix of the first run. -/
theorem gen_eq_iff {α : Type*} {dec dec' : List α → α} {T : ℕ} :
    gen dec T = gen dec' T ↔ ∀ t, t < T → dec (gen dec t) = dec' (gen dec t) := by
  constructor
  · intro h t ht
    have h2 := gen_eq_of_succ (gen_eq_of_le h (t + 1) ht)
    have h3 := h2.2
    rw [← h2.1] at h3
    exact h3
  · intro h
    by_contra hne
    obtain ⟨t, ht, _, hd⟩ := first_divergence hne
    exact hd (h t ht)

/-- An answer flip under greedy decoding forces a KL lower bound at one position of the fresh run.
`P s` and `Q s` are the fresh and the reused next-token distributions after the prefix `s`, and `dec`,
`dec'` are greedy for them. If the two answers differ there is a position `t < T` with a common prefix
`s = gen dec t` at which the greedy tokens differ and
`(√P_s(dec s) - √P_s(dec' s))² / 2 ≤ kl (P s) (Q s)`. -/
theorem answer_flip_forces_kl {α γ : Type*} [Fintype α] {P Q : List α → α → ℝ}
    (hP : ∀ s, IsDist (P s)) (hQ : ∀ s, IsDist (Q s)) {dec dec' : List α → α}
    (hdec : ∀ s b, P s b ≤ P s (dec s)) (hdec' : ∀ s b, Q s b ≤ Q s (dec' s)) {T : ℕ}
    (A : List α → γ) (h : A (gen dec T) ≠ A (gen dec' T)) :
    ∃ t, t < T ∧ gen dec t = gen dec' t ∧ dec (gen dec t) ≠ dec' (gen dec t) ∧
      (Real.sqrt (P (gen dec t) (dec (gen dec t))) -
        Real.sqrt (P (gen dec t) (dec' (gen dec t)))) ^ 2 / 2 ≤
        kl (P (gen dec t)) (Q (gen dec t)) := by
  obtain ⟨t, ht, hpre, hne, hh⟩ := answer_flip_forces_hell hP hQ hdec hdec' A h
  exact ⟨t, ht, hpre, hne, hh.trans (hell_le_kl (hP _) (hQ _))⟩

/-- An answer flip under greedy decoding needs a logit shift that reaches the fresh logit margin at one
position of the fresh run. `Z s` are the fresh logits after the prefix `s` and `Z s + E s` the reused
logits; `dec'` is greedy for the reused distribution `softmax (Z s + E s)`. If the two answers differ
there is a position `t < T` with a common prefix `s = gen dec t` at which the greedy tokens differ and,
whenever the fresh token `dec s` leads every other token by at least `g` in the fresh logits and `w`
bounds the oscillation of the shift `E s`, `g ≤ w`. -/
theorem answer_flip_needs_osc {α γ : Type*} [Fintype α] {Z E : List α → α → ℝ}
    {dec dec' : List α → α}
    (hdec' : ∀ s b, softmax (Z s + E s) b ≤ softmax (Z s + E s) (dec' s)) {T : ℕ}
    (A : List α → γ) (h : A (gen dec T) ≠ A (gen dec' T)) :
    ∃ t, t < T ∧ gen dec t = gen dec' t ∧ dec (gen dec t) ≠ dec' (gen dec t) ∧
      ∀ g w : ℝ,
        (∀ c, c ≠ dec (gen dec t) → g ≤ Z (gen dec t) (dec (gen dec t)) - Z (gen dec t) c) →
        OscLe (E (gen dec t)) w → g ≤ w := by
  obtain ⟨t, ht, hpre, hne⟩ := answer_flip_first_divergence A h
  refine ⟨t, ht, hpre, hne, fun g w hm ho => ?_⟩
  exact flip_needs_osc hm ho (Ne.symm hne) ((softmax_le_iff _ _ _).mp (hdec' _ _))

end Carryover.Pred

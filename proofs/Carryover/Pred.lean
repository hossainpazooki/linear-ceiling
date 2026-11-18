import Mathlib

/-!
# Next-token predictions under a fresh and a reused cache: shared definitions

The paper's second and third statistics are read on the reader's next-token distribution, not on its
keys. At one position the vocabulary is a finite type `ι`, the reader's distribution under its fresh
cache is `p : ι → ℝ` and under the reused cache `q : ι → ℝ`; both come from logit vectors through
`softmax`, and the reused logits are the fresh ones plus a shift `e`.

This file holds only the definitions that `PredKL.lean` (the per-token KL divergence) and
`PredFlip.lean` (greedy tokens and answer flips) share. It lives in the namespace `Carryover.Pred`
because `Carryover.softmax` is the masked attention softmax of `Attention.lean`.
-/

namespace Carryover.Pred

open Finset

variable {ι : Type*} [Fintype ι]

/-- A next-token distribution on a finite vocabulary: every probability positive, total one. -/
structure IsDist (p : ι → ℝ) : Prop where
  pos : ∀ i, 0 < p i
  sum_one : ∑ i, p i = 1

/-- `KL(p ‖ q) = ∑_i p_i log (p_i / q_i)`, in nats. -/
noncomputable def kl (p q : ι → ℝ) : ℝ := ∑ i, p i * Real.log (p i / q i)

/-- `∑_i (√p_i - √q_i)²`, twice the squared Hellinger distance. -/
noncomputable def hell (p q : ι → ℝ) : ℝ := ∑ i, (Real.sqrt (p i) - Real.sqrt (q i)) ^ 2

/-- Softmax of a logit vector over the whole vocabulary. -/
noncomputable def softmax (z : ι → ℝ) (i : ι) : ℝ := Real.exp (z i) / ∑ j, Real.exp (z j)

/-- `w` bounds the oscillation of the logit shift `e`: `e_i - e_j ≤ w` for all `i`, `j`. A shift that
is the same on every token has oscillation zero and leaves the softmax unchanged. -/
def OscLe (e : ι → ℝ) (w : ℝ) : Prop := ∀ i j, e i - e j ≤ w

/-- Greedy generation with a deterministic next-token rule `dec` (prefix to next token): the list of
the first `t` generated tokens. -/
def gen {α : Type*} (dec : List α → α) : ℕ → List α
  | 0 => []
  | t + 1 => gen dec t ++ [dec (gen dec t)]

end Carryover.Pred

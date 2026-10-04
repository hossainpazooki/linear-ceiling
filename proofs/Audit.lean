import Carryover

/-!
Axiom audit of the headline results. Run with `lake env lean Audit.lean` (or `./check.sh`).
Every result should depend only on `propext`, `Classical.choice`, `Quot.sound`.
-/

open Carryover

-- Theorem thm:identity
#print axioms fstar_eq_zero_iff
#print axioms mean_devLH
#print axioms mu_dev
#print axioms theorem1
#print axioms theorem1_verdict
#print axioms thm_identity
-- Theorem thm:sandwich
#print axioms fstar_antitone
#print axioms fstar_le_p
#print axioms p_le_mu_div
#print axioms lower_bound_max
#print axioms lower_bound_deltaMax
#print axioms lower_bound_beta
#print axioms lower_bound_beta_iSup
#print axioms theorem2_sandwich
-- Subset characterisation of the statistic
#print axioms fstar_le_of_subset
#print axioms exists_retained_set
#print axioms retained_mean_le
-- Corollary cor:seam
#print axioms seam_mean_le
#print axioms seam_zero_floor
#print axioms seam_mean_ge
#print axioms seam_pos_floor
#print axioms card_nearSet_le
#print axioms card_posWindow_le
#print axioms cor_seam
#print axioms cor_seam_converse
#print axioms cor_seam_large_n
#print axioms cor_seam_positions
-- Assumption ass:rope and Proposition prop:attn
#print axioms logit_shift_le
#print axioms hasDerivAt_softmax_path
#print axioms softmax_l1_shift
#print axioms softmax_l1_shift_iSup
#print axioms abs_deltaZ_le
#print axioms prop_attn_weights
#print axioms prop_attn_weights_iSup
#print axioms prop_attn_diffuse
#print axioms prop_attn_diffuse_causal
#print axioms prop_attn_tail
#print axioms prop_attn_tail_ret
#print axioms prop_attn_concentrated
#print axioms prop_attn_concentrated_ret
#print axioms value_shift_le
-- Numbers reported beside the theorems
#print axioms arms_same_K
#print axioms arms_cross_K
#print axioms ladder_mid_K_pos
#print axioms bridge_zero
#print axioms scaled_short_mid_zero
#print axioms short_low_pos
#print axioms additional_models_monotone
#print axioms tau_ladder_monotone
#print axioms matched_upper_chain
#print axioms matched_shares
#print axioms far_level_zero

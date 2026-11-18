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
-- Theorem thm:kl (per-token KL: cumulant gap, two-sided bounds, the numbers)
#print axioms Carryover.Pred.softmax_isDist
#print axioms Carryover.Pred.softmax_shift
#print axioms Carryover.Pred.kl_softmax
#print axioms Carryover.Pred.kl_softmax_le_osc
#print axioms Carryover.Pred.log_sum_exp_sub_le
#print axioms Carryover.Pred.kl_softmax_le_osc_sq
#print axioms Carryover.Pred.kl_softmax_le_of_abs
#print axioms Carryover.Pred.hell_le_kl
#print axioms Carryover.Pred.kl_nonneg
#print axioms Carryover.Pred.kl_pos_of_ne
#print axioms Carryover.Pred.kl_self
#print axioms Carryover.Pred.l1_sq_le_four_kl
#print axioms Carryover.Pred.l1_sq_le_four_hell
#print axioms Carryover.Pred.control_floor
#print axioms Carryover.Pred.holds_threshold_needs_osc
#print axioms Carryover.Pred.degrades_threshold_needs_osc
-- Theorem thm:text (what the mean per-token KL of a text measures)
#print axioms Carryover.Pred.kl_prod
#print axioms Carryover.Pred.seqProb_isDist
#print axioms Carryover.Pred.kl_seqProb_succ
#print axioms Carryover.Pred.kl_seqProb
#print axioms Carryover.Pred.seqProb_marginal
#print axioms Carryover.Pred.kl_seqProb_expect
#print axioms Carryover.Pred.meanKL_expect
#print axioms Carryover.Pred.kl_prod_pos_of_ne
#print axioms Carryover.Pred.kl_branch_zero
#print axioms Carryover.Pred.kl_prod_eq_single
-- The remark on what a low mean can still hold (after Theorem thm:text)
#print axioms Carryover.Pred.card_ge_mul_le
#print axioms Carryover.Pred.holds_at_most_two
-- Proposition prop:greedy
#print axioms Carryover.Pred.softmax_lt_iff
#print axioms Carryover.Pred.softmax_le_iff
#print axioms Carryover.Pred.argmax_stable
#print axioms Carryover.Pred.argmax_stable_of_abs
#print axioms Carryover.Pred.flip_forces_hell
#print axioms Carryover.Pred.flip_forces_kl
#print axioms Carryover.Pred.flip_needs_osc
#print axioms Carryover.Pred.near_tie_flip
-- Proposition prop:flip
#print axioms Carryover.Pred.gen_length
#print axioms Carryover.Pred.first_divergence
#print axioms Carryover.Pred.gen_eq_iff
#print axioms Carryover.Pred.answer_flip_first_divergence
#print axioms Carryover.Pred.answer_flip_forces_hell
#print axioms Carryover.Pred.answer_flip_forces_kl
#print axioms Carryover.Pred.answer_flip_needs_osc
#print axioms Carryover.Pred.flips_le_divergences
-- One numeric value (the Hoeffding tail expression at n = 1319; the inequality itself is not proved)
#print axioms Carryover.Pred.hoeffding_tail_1319
-- Runs and texts that end early (thm:text (c), and prop:flip with a stopping rule)
#print axioms Carryover.Pred.padTree_isDist
#print axioms Carryover.Pred.kl_seqProb_stop
#print axioms Carryover.Pred.meanKL_stop_bounds
#print axioms Carryover.Pred.liveCount_pos
#print axioms Carryover.Pred.liveCount_le
#print axioms Carryover.Pred.liveCount_of_live
#print axioms Carryover.Pred.liveCount_of_never_ended
#print axioms Carryover.Pred.genStop_eq_gen_of_live
#print axioms Carryover.Pred.genStop_length_of_live
#print axioms Carryover.Pred.genStop_prefix
#print axioms Carryover.Pred.first_divergence_stop
#print axioms Carryover.Pred.genStop_eq_iff
#print axioms Carryover.Pred.answer_flip_first_divergence_stop
#print axioms Carryover.Pred.answer_flip_forces_hell_stop
#print axioms Carryover.Pred.answer_flip_forces_kl_stop
#print axioms Carryover.Pred.answer_flip_needs_osc_stop
#print axioms Carryover.Pred.answer_flip_stop

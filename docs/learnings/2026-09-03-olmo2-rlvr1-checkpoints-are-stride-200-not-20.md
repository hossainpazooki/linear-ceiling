# OLMo-2-0425-1B-RLVR1's card says checkpoints every 20 steps; the repo holds 13 at stride 200, and `main` is none of them

kills: (nothing)
ts: 2026-09-03T04:04:06Z
commit: 5960c20
session: linear-ceiling-rl-design (session_01DksT5fTgXwHmKFfgLSXmnT)
status: verified
fact: The HF model card for `allenai/OLMo-2-0425-1B-RLVR1` reads "The model weights are saved every
20 training steps, and can be accessible in the revisions" (template text shared with the SFT/DPO
cards). The repository's branch list is `step_200 … step_2600`, thirteen revisions at stride 200,
plus `main`. `main`'s `model.safetensors` has a different sha256 from `step_2600`'s, so `main` is a
fourteenth set of weights whose step is not on the branch list. Consequence for the E-RL design:
the finest realizable public lag is 200 optimizer-or-training steps (unit still unpinned), "lag 20"
cannot be written for this source, and `main` is not a lag point. The base is
`allenai/OLMo-2-0425-1B-DPO` per the card's `base_model` frontmatter.
basis: `list_repo_refs('allenai/OLMo-2-0425-1B-RLVR1')` -> `14 ['main', 'step_1000', 'step_1200',
'step_1400', 'step_1600', 'step_1800', 'step_200', 'step_2000', 'step_2200', 'step_2400',
'step_2600', 'step_400', 'step_600', 'step_800']`; `model_info(..., files_metadata=True)` ->
`{'main': ['c556b74da82a'], 'step_2600': ['03ddb334ad4a']}` (sha256 prefixes of model.safetensors).
re-verify: `python -c "from huggingface_hub import list_repo_refs as r, HfApi; print(sorted(b.name for b in r('allenai/OLMo-2-0425-1B-RLVR1').branches)); a=HfApi(); print({v:[s.lfs.sha256[:12] for s in a.model_info('allenai/OLMo-2-0425-1B-RLVR1',revision=v,files_metadata=True).siblings if s.rfilename=='model.safetensors'] for v in ('main','step_2600')})"` (network, read-only).

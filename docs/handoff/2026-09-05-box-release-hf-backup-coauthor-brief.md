# Handoff — E9 box released, mirror backed up to HF, co-author pickup brief published

2026-09-05 02:30 UTC. Newest commit this brief describes: linear-ceiling `31a5f69` (H-E9 HELD landed,
pushed by the other 09-04 session at 20:47 UTC). This session wrote no ledger text. Its files are all
untracked additions listed under Current state; the working tree ALSO carries another session's
uncommitted E8 amendment (entry 0030 staging, see `2026-09-05-e8-amendment-0030.md`), which this brief
does not describe. Pick-up measures drift from `31a5f69` and from the HF dataset commit `a45e9ee8`.

## Current state

- **built / verified** — Algoverse box released 2026-09-04 18:30:48 UTC. Before release: mirror
  `results/e9/` complete (`report.json` `complete: true`, 25/68 scored), 8 kept dumps = 720 files
  re-hashed at home against `report.json` `kept_dumps` (0 mismatches), every box-side small record
  diffed by sha256 against the mirror (identical except 68 `align/*.npz`, arrays identical), box
  scratch empty, HF cache removed, no token/credential on the box, kernel deleted, Hub server
  DELETE → 204, user record `servers: {}`, `/user/…` route 302, hub home "Start My Server".
  re-verify: `sha256sum results/e9/report.json` prints `1b2153e31245eebb6d4a7f2709450ba84c2a29e30081fc98e9d304208cfeda29`
  (home mirror); the box itself is gone (grant expiry 04:20 UTC 09-05).
- **built / verified** — HF backup: private dataset `hossainpazooki/linear-ceiling-e9-2026-09-04`,
  commit `a45e9ee8`, holding `results/e9/` at the repo root (919 files) plus
  `mappers/qwen3-0.6b-to-1.7b/k1.{json,safetensors}` (upstream layout). Every file verified:
  `lfs.sha256` vs fingerprint/mirror, non-LFS files re-downloaded and hashed; subset `hf download`
  round-trip 32/32 identical.
  re-verify: with a read token in `$HF_TOKEN`, `.venv/Scripts/python.exe -c "from huggingface_hub import HfApi;i=HfApi().dataset_info('hossainpazooki/linear-ceiling-e9-2026-09-04',files_metadata=True);print(i.sha[:8],len(i.siblings),next(s.lfs.sha256[:8] for s in i.siblings if s.rfilename.endswith('k1.safetensors')))"`
  prints `a45e9ee8 923 cd6a8d93`.
- **built** — box-side logs pulled and hashed into `results/e9/logs/box/` (e9.log, setup.log,
  setup2.log, probe.log, probe2.log, ipython_history.sqlite); the two refused attempts' halt logs
  reconstructed partially from the prior session's transcript into `results/e9/logs/halt-reconstructed/`
  with a README stating the capture commands. Home-only, not on HF.
  re-verify: `cat results/e9/logs/halt-reconstructed/README.md`.
- **built** — co-author pickup brief, published as a private artifact
  (claude.ai/code/artifact/f548d982-26b4-4fe9-a791-c7b0bb983997): download commands, the refutation
  owed on 0025–0029 with two leads (τ-ladder sensitivity; the exactly-zero prefix control), his two
  flags answered from 0029's figures. Shared only when Hossain shares it.
- **built (this commit set, untracked)** — `docs/gpu-experiment-protocol.md` (rules R1–R12),
  `tools/jupyterhub/{jh.py,pull.py,README.md}` (the box driver and puller, configured from env; the
  puller re-pulls on size or mtime change), five learnings entries dated 09-04/09-05,
  `docs/probes/2026-09-04-hf-upload-large-folder-4workers.{out,err}`, this brief, a CLAUDE.md
  "GPU runs" section.
  re-verify: `git status --short tools docs/gpu-experiment-protocol.md docs/learnings docs/probes docs/handoff CLAUDE.md`.
- **planned / not started** — org transfer of the HF dataset if more than one collaborator needs it;
  the `[STRETCH]` partial-prefill experiment on the retained dumps; E8 amendment (other session).

## Locked decisions

- **The release proceeded although the halt logs were gone.** Reason: nothing on the box could
  recover a file overwritten by `> e9.log`; waiting forfeited nothing and held a shared slot.
  Consequence recorded in learnings 2026-09-04 and protocol R4.
- **HF is transport and backup only; the summarizer reads the local mirror.** Reason: CLAUDE.md rule
  "never write a number into the ledger that was not recomputed from `results/` by a summarizer";
  a Hub copy is one more place a number could be read from. Protocol R8.
- **The mapper artifact lives in the same dataset under upstream's own path, not under
  `results/e9/`.** Reason: `hf download --local-dir results/e9 --exclude "mappers/**"` keeps the
  mirror layout exact, and `--local-dir ../kv-transfer-replication --include "mappers/**"` drops
  the artifact where `summarize_e9` and `--calibrate-tau` look. Decided by Hossain 09-04 evening.
- **A collaborator gets a scoped read-only token, not the write token.** Reason: the write token
  was pasted in chat and can delete the backup; the Hub has no per-user sharing on a user
  namespace (learnings 2026-09-05). The write token used this session is to be revoked.
- **The co-author's refutation is not done.** Reason: his pass was at `13b8128`, where the ledger
  ended at 0024; 0025–0029 did not exist there. "Already caught and fixed in 0025–0027" is a reading,
  not a refutation. The artifact brief carries the per-entry targets.

## Reuse map

- `tools/jupyterhub/jh.py` / `pull.py` — drive and drain a JupyterHub-only box; env-configured.
- `docs/gpu-experiment-protocol.md` — the rules; each runbook inherits it.
- `docs/2026-09-02-e9-gpu-runbook.md` §3b/§5 — the E9-specific steps, amended 09-04.
- HF verifier pattern: `dataset_info(files_metadata=True)` → `lfs.sha256` vs fingerprint, in-memory
  GET + sha256 for non-LFS files (Windows MAX_PATH breaks `hf_hub_download` into a nested cache);
  the script is in this session's scratch (`hf/verify_hf.py`), shape described in protocol R8.
- `docs/probes/2026-09-04-hf-upload-large-folder-4workers.*` — what a wedged multi-worker upload
  looks like; restart with one worker.
- Memory notes: `jupyterhub-box-driving`, `relaunch-redirect-destroys-halt-logs`,
  `hf-upload-large-folder-windows-stall`.

## Invariants

- `results/` never enters git history; the HF dataset is the only off-machine copy of the kept dumps.
- The verdict figures travel only through `summarize_e9` and a numbered entry; nothing on the
  artifact page, on HF, or in this brief is a source for a ledger number.
- Entries 0025–0029 are immutable; refutation is recomputation, never edit.
- `config/e9.toml` `[e9.rule]` is 0023's; the 0028 tolerance is not changed without a new entry.
- Tokens: env-only, scoped, expiring, revoked once pasted anywhere (protocol R9).

## Open / next

1. **Hossain:** revoke the write token used this session; mint the co-author's read token
   (`e9-backup-read-<handle>-exp-<date>`); share the artifact from its menu.
2. **Co-author:** the refutation of 0025–0029 per the artifact brief; first the τ-ladder lead and the
   prefix-control lead. Needs the HF download (both commands) and the repo at `31a5f69`.
3. Commit this session's files (list in Current state); the other session's 0030 work is a separate
   commit set and must not be mixed in.
4. `check-learnings` was red on pre-existing entries before this session; the five new entries were
   run through it at write time (result in the session report), not re-run after the other session's
   pending edits land.

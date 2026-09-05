# GPU experiments — how we run them and the rules that bind them

Standing protocol, written 2026-09-05 from the E9 GPU day (2026-09-04; entries 0026–0029; runbook
`docs/2026-09-02-e9-gpu-runbook.md`; closing brief `docs/handoff/2026-09-04-e9-gpu-day-and-verdict.md`).
Each experiment still gets its own dated runbook; this page is what every runbook inherits. The ledger
entries cited here are the authority where they overlap; this page adds the box, transport and backup
discipline the ledger does not carry.

## The shape of a GPU day

A GPU run is a batch job that exists for one reason: to write `results/<exp>/` records that a CPU
summarizer at home turns into figures. Nothing decided on the box is a result; the box produces bytes,
the summarizer produces numbers, a numbered entry produces the verdict. Everything below follows from
the fact that the box is temporary, shared, and not ours.

```
register (before any request)  ->  request  ->  set up + gate on the box  ->  launch detached
   ->  pull-verify-delete per handoff  ->  release checklist  ->  backup  ->  summarize at home  ->  entry
```

## Rules

Numbered so a runbook or an entry can cite them.

**R1 — Registered before requested.** The experiment's rule, thresholds, seeds, coverage rule, keep
subset and every control are on the ledger and `config/<exp>.toml` is committed unmodified before the
hardware request is sent. `<exp> --check` prints ready on a clean checkout. After the first score file
exists, no rule, τ, band, cap, dtype or handoff-set change is legitimate (0023's precondition; 0025,
0026, 0027 each open by proving no score file existed). A change forced by the hardware (an OOM) is a
new entry appended *before any score*, with its measurement (0026's probe table), never a silent edit.

**R2 — Budget the forward, not the parameters.** A memory budget is not complete until the attention
backend is known. In float32 with grouped-query heads, transformers' SDPA takes the math kernel and
materializes `[heads, T, T]` scores: 16 × 29,391² × 4 B = 51.49 GiB on the E9 handoff that OOMed a
39.5 GiB slice (learnings 2026-09-04, entry 0026). Measure `torch.cuda.max_memory_allocated` at the
real sequence length on the real path before requesting a card; state the measured peak in the request.

**R3 — Everything the run needs is either in git, in the manifest, or listed by sha in the runbook.**
Traces come from the committed manifest (`e7_manifest fetch`). Gitignored artifacts the driver reads
(the fitted mapper under `../kv-transfer-replication/mappers/`) are listed in the runbook with their
sha256 and uploaded before the gate runs; the gate refuses when one is absent (`3ef9044`). The 17:16 UTC
E9 launch died on exactly this.

**R4 — Launch detached, never self-match, rotate the log.** `setsid nohup <driver> > <exp>.log 2>&1 < /dev/null &`.
Never `pkill -f <pattern>` from a shell whose own command line matches the pattern (0027). Before any
relaunch, `mv <exp>.log "<exp>.$(date -u +%Y%m%dT%H%M%SZ).halt.log"` and pull it home first; a
`> <exp>.log` redirect on relaunch is a silent delete of the halt log the verdict entry will cite
(learnings 2026-09-04). Delete a refused attempt's transients and record the deletion with a listing
(0027 does).

**R5 — Pull, verify, then delete; the driver's fingerprint is the oracle.** The driver writes a sha256
per kept file into `report.json` under each score's `kept_dumps`. Per handoff, in this order: download
the kept `scratch/<stem>/`, verify every file against that fingerprint, and only then delete it on the
box (0027). Small records (`report.json`, `align/`, `controls/`, `scores/`, `tokens/`, the log) are
mirrored every round; a mirror must re-pull on size *or* modification-time change, since a same-size
skip is blind to a rewritten binary of equal length (learnings 2026-09-04). `tools/jupyterhub/pull.py`
is this loop for a JupyterHub-only box; `rsync`/tar-over-ssh in the runbook §5 is the ssh form.

**R6 — Nothing may exist only on the box, and nothing leaves the box unverified.** Before release, the
home mirror holds `report.json` with `complete: true`, every record directory, and every kept dump with
its fingerprint re-verified at home from the raw bytes, not from the puller's log. Then the box-side
hashes of every small record are diffed against the mirror by path.

**R7 — Release checklist, in order, stop at the first failure.**
1. Mirror complete and re-verified (R6); print the mirror's `report.json` sha256.
2. Box listing: no tensor directory remains under `results/<exp>/`; if one does, pull and verify it
   first, delete nothing unverified.
3. Pull every box-side log the entry will cite that the puller did not: the run log, the rotated halt
   logs, setup and probe logs; hash each after download.
4. Sensitive-data sweep: no `~/.cache/huggingface/token`, no `HF_TOKEN` or `hf_…` string in any
   history, rc file, script or log, no git credential store or `.netrc`, plain HTTPS remotes only.
   Then `rm -rf ~/.cache/huggingface`: model weights are someone else's disk quota until the wipe.
5. Stop every process of ours; `ps -u $(whoami)` shows only the hub's own server (and the kernel
   used to look, which is deleted next). GPU processes that belong to other users' slices are not ours.
6. Stop the user server through the Hub API and verify the effect, not the response: the user record
   shows no server, the `/user/<u>/` route no longer answers 200, the Hub home page offers "Start My
   Server". Record the UTC time.
7. Report: box vs mirror report sha256 (must match), what step 3 pulled with sizes, what step 4 found,
   the stop response, the release time. No run numbers in the release report; the summarizer is where
   numbers are read.

**R8 — Backup is transport, not evidence.** The verified home mirror of `results/<exp>/` is pushed to
a private Hugging Face dataset laid out so `hf download --repo-type dataset --local-dir results/<exp>`
reconstructs it with no translation, plus any gitignored upstream artifact the summarizer needs, in
upstream's own layout under its own top-level directory (E9: `mappers/qwen3-0.6b-to-1.7b/k1.*`). Push
only from the home mirror after verification, never from the box; small records first, kept dumps by
a single resumable `upload-large-folder` (one worker on Windows; learnings 2026-09-04), the
`complete: true` report last. After every push, `dataset_info(files_metadata=True)` and compare each
LFS file's `lfs.sha256` to the driver's fingerprint or the mirror's sha256; re-download and hash files
without an LFS entry; re-upload on mismatch, delete nothing. Nothing on the Hub is a ledger figure; the
summarizer reads the local mirror only. E9's dataset: `hossainpazooki/linear-ceiling-e9-2026-09-04`.

**R9 — Token hygiene.** Hub tokens are fine-grained, scoped to the one repo, and expiring; write tokens
for the pusher, read-only tokens for collaborators, named `<exp>-backup-<role>-<holder>-exp-<date>`.
A token lives in a process environment variable for the duration of the command, never in a `--token`
flag (shell history), never in a file inside a checkout, never in a chat message or a transcript; one
that has been pasted anywhere is revoked. A private user-namespace repo cannot be shared per user
(learnings 2026-09-05): a collaborator gets a read token, or the repo moves to an organization.

**R10 — What goes where.**

| artifact | git | HF backup | home mirror only | never |
|---|---|---|---|---|
| rule, thresholds, seeds, manifest, runbook, probes, entries | yes | | | |
| `results/<exp>/` records and kept dumps | | yes | yes (source of truth) | in history |
| gitignored upstream artifacts the summarizer needs (mappers) | | yes | yes | in history |
| summarizer outputs (`summary.json`, `recheck/`) | | | yes (regenerable) | |
| run and halt logs | | | yes | overwritten |
| model weights, pip caches | | | | on the box after release |
| tokens, credentials | | | | anywhere written |

**R11 — The summarizer is the only reader, and a refusal is a finding.** Every figure enters the
ledger through `summarize_<exp>` run at home; a refusal is pasted verbatim and investigated, not
worked around. Loosening a check after seeing the data is post hoc by construction: reproduce the
disagreement on a matching platform, vary the one suspected cause, and register the tolerance as its
own entry with the measurement (0028; learnings 2026-09-04). A summarizer tolerance is not tightened
or loosened afterwards without a new entry and a new measurement.

**R12 — Everything is re-verifiable by someone who was not there.** The closing brief, the learnings
entries and the probes under `docs/probes/` carry the commands and the outputs; a co-author's
refutation of the run's entries is recomputation from the git repo plus the backup, and if that is not
possible from a clean checkout, something is missing from R3 or R8.

## The box, concretely (Algoverse TLJH, JupyterHub only)

No ssh or scp. Everything goes over the Hub API: a browser login mints a token
(`POST /hub/api/users/<u>/tokens`); commands run through a python3 kernel's websocket with the token
in the `Authorization` header; uploads go through `/api/contents` as base64 (split above 60 MB);
downloads stream from `/user/<u>/files/<path>`, which does not serve dotfiles. Keep each remote command
under about 40 s or the socket drops and the next poll reads a stale log; grep the whole log for
`Traceback`, not its tail. The grant assigns a MIG slice by `CUDA_VISIBLE_DEVICES`; the server has been
observed to receive an unexplained SIGTERM that kills its whole cgroup, so the driver's per-handoff
checkpoint is the only protection. PyPI `torch` is a cu130 build; a CUDA 12.8 driver needs the
`whl/cu128` index. `tools/jupyterhub/` holds the two scripts; the memory note `jupyterhub-box-driving`
holds the trap list.

## Where the E9 instance of each rule lives

| rule | E9 record |
|---|---|
| R1 | 0019, 0023, 0025, 0026, 0027 (each opens with the no-score-file precondition) |
| R2 | 0026 probe table; learnings 2026-09-04 f32 SDPA |
| R3 | runbook §3b; gate commit `3ef9044` |
| R4, R5 | 0027 "Box discipline"; runbook §5 |
| R6, R7 | this session's release report (handoff 2026-09-05) |
| R8, R9 | HF dataset at commit `a45e9ee8`; learnings 2026-09-04 upload, 2026-09-05 sharing |
| R11 | 0028; learnings 2026-09-04 relative check |

# GPU experiments — how we run them and the rules that bind them

Standing protocol, written 2026-09-05 from the E9 GPU day (2026-09-04; entries 0026–0029; runbook
`docs/2026-09-02-e9-gpu-runbook.md`; closing brief `docs/handoff/2026-09-04-e9-gpu-day-and-verdict.md`).
Each experiment still gets its own dated runbook; this page is what every runbook inherits. The ledger
entries cited here are the authority where they overlap; this page adds the box, transport and backup
discipline the ledger does not carry.

## Quick reference — HF backups and tokens (team)

The backup of a run is a Hugging Face dataset, public or private (R8), laid out so `hf download` reconstructs the mirror with no
translation (R8). Tokens never touch a file inside a checkout, a `--token` flag, shell history, or a chat (R9). The
commands below are Git Bash / MINGW64 on Windows and plain bash on Linux; the interpreter is `.venv/Scripts/python.exe`
on Windows and `.venv/bin/python` on Linux.

**Token, once per role, per dataset.** In the Hub UI: Settings → Access Tokens → Create new → *Fine-grained*.
Name `<exp>-backup-<role>-<holder>-exp-<yyyy-mm-dd>`; Repository permissions on the ONE dataset only; Write for the
pusher, Read for a collaborator; expiry a week or less. Create the dataset first (New dataset; public or private, R8) so the token
can name it. Then, in the shell you will run the commands from, and nowhere else:

```bash
read -s HF_TOKEN && export HF_TOKEN      # paste at the silent prompt: nothing lands in history or on disk
# ^ RUN THIS LINE ALONE and paste nothing after it (added 2026-09-10). `read` consumes the next line of standard
#   input, so in a pasted block it eats the following command instead of the secret: the token is never set, the
#   push runs unauthenticated, and the failure surfaces as a 401 out of `create_repo` that reads like a scope
#   problem. `hf auth whoami` printing the username is the confirmation to require before the long command.
hf auth whoami                           # must print `user: <you>`; `Not logged in` means the read above was eaten
# ... run the commands below in this same shell ...
unset HF_TOKEN                           # then revoke the token in the UI; one that was pasted anywhere is revoked
```

**Push, in R8 order, from the verified home mirror only** (stage a copy in the upstream's own layout and re-hash it
against the manifests first; never push from the box):

```bash
HF=.venv/Scripts/hf.exe; REPO=hossainpazooki/linear-ceiling-<exp>-<yyyy-mm-dd>; ST=<staging dir>
cd "$ST"
$HF upload "$REPO" <small-records-dir> <same path in repo> --repo-type dataset --quiet    # 1. small records first (manifests, logs, json)
$HF upload-large-folder "$REPO" "$ST" --repo-type dataset --num-workers 1                 # 2. the tensors: ONE resumable run, ONE worker on Windows
$HF upload "$REPO" README.md README.md --repo-type dataset --quiet                        # 3. the card last: it is the "complete" marker
```

Gotchas that cost real time: `upload-large-folder` takes the whole tree — do not pass `--include` patterns (`hf.exe`
globs them itself and the extra matches become stray arguments); more than one worker wedges at 0 bytes on Windows
(learnings 2026-09-04); rerunning the same command resumes. A tree of many files will not finish in one sitting:
the repository accepts 128 commits per hour and the uploader commits in batches, so plan on re-running across
several windows and let the R8 verifier, not the last command's exit, decide when it is done (added 2026-09-10).

**Verify from the Hub's own hashes, never from the uploader's log:**

```bash
.venv/Scripts/python.exe tools/hf_verify_backup.py "$REPO" "$ST" --exclude README.md    # must end in: BACKUP VERIFIED
```

It compares every LFS file's `lfs.sha256` to the local sha256, downloads and hashes every non-LFS file, and checks
both directions for missing files (the Hub's own `.gitattributes` is ignored). The dataset name and the card's
revision go into the runbook and the handoff; the local mirror stays the summarizer's only input.

**Collaborators:** a public dataset needs no token to download. A private user-namespace dataset cannot be shared
per user (learnings 2026-09-05); give a read token, or move the dataset to an organization. A collaborator reconstructs a mirror with
`hf download "$REPO" --repo-type dataset --local-dir <checkout>` and verifies it the same way.

**Datasets on the record:** E9 `hossainpazooki/linear-ceiling-e9-2026-09-04` (card `a45e9ee8`); n = 420 calibration
pair + `n420` mapper `hossainpazooki/linear-ceiling-n420-2026-09-08` (card `8675b719`).

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
**An extrapolated peak is a bound to be replaced, not a budget** (added 2026-09-10). E9-long's request carried
29.2 GiB extrapolated from a slope measured on a smaller slice; the probe on the granted card measured
**31.56 GiB** at T = 80,111, 8% higher. Re-run the probe on the granted card, under the run's own config —
including any rope scaling — before the launch, and let that number, not the estimate, gate the sitting.
Static YaRN cost no extra memory at equal T: 16.70 GiB at 32,768 scaled on an L40S against 16.72 GiB native
on an H100 MIG slice, so the window extension is free and only the longer sequence is not.

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
(0027 does). **Run the driver unbuffered** (added 2026-09-10): CPython block-buffers stdout when it is a file,
so a detached `python -m …` without `-u` writes nothing to the log until it exits. E9-long's log held no
`[i/N]` line for 80 minutes while the run was healthy and checkpointing normally. Liveness and progress come
from the checkpointed `report.json` and the `.rc` file the launcher writes, never from the log's length; a
wait keyed on the log reads a working run as hung (learnings 2026-09-10).

**R5 — Pull, verify, then delete; the driver's fingerprint is the oracle.** The driver writes a sha256
per kept file into `report.json` under each score's `kept_dumps`. Per handoff, in this order: download
the kept `scratch/<stem>/`, verify every file against that fingerprint, and only then delete it on the
box (0027). Small records (`report.json`, `align/`, `controls/`, `scores/`, `tokens/`, the log) are
mirrored every round; a mirror must re-pull on size *or* modification-time change, since a same-size
skip is blind to a rewritten binary of equal length (learnings 2026-09-04). `tools/jupyterhub/pull.py`
is this loop for a JupyterHub-only box; `tools/ec2/pull.py` is the same loop over ssh, streaming each kept
directory with tar and deleting it on the box only after every fingerprint matches (added 2026-09-10).

**R6 — Nothing may exist only on the box, and nothing leaves the box unverified.** Before release, the
home mirror holds `report.json` with `complete: true`, every record directory, and every kept dump with
its fingerprint re-verified at home from the raw bytes, not from the puller's log. Then the box-side
hashes of every small record are diffed against the mirror by path. `tools/ec2/verify_mirror.py <exp>` does the
home half independently of the puller's own bookkeeping — it re-hashes every file `report.json` fingerprints
and refuses an incomplete report — and prints the report sha256 that step 1 of R7 wants (added 2026-09-10).

**R7 — Release checklist, in order, stop at the first failure.**
0. The account is shared until proven otherwise (added 2026-09-09; learnings entry of that date). Before any deletion
   or stop: `ls -la ~` and `ps -u $(whoami)`, and compare against the runbook's own list of files and processes. Anything
   not ours — a directory, a notebook, a shell, a python — aborts the release: delete nothing, stop nothing, leave the
   server up, tell the operator. A one-liner that deletes before it lists cannot honor "ours" in step 5.
   **On a rented single-tenant instance the rule stands and the allowlist changes** (added 2026-09-10): an
   allowlist written for a shared hub login aborted three times on an AWS Deep Learning AMI — on the image's own
   license files, `.aws`, `.gnupg`, `gds-nvidia-fs`, on artifacts our own tooling created (`.nv`, `.zshrc`), and
   on the sweep's own redirected log. Classify by mtime against the instance launch time: anything older is
   image baseline and is listed for the record, anything newer must be on the run's own list. Each abort is the
   checklist working; resolve it by read-only inspection and never by loosening the abort.
1. Mirror complete and re-verified (R6); print the mirror's `report.json` sha256.
2. Box listing: no tensor directory remains under `results/<exp>/`; if one does, pull and verify it
   first, delete nothing unverified.
3. Pull every box-side log the entry will cite that the puller did not: the run log, the rotated halt
   logs, setup and probe logs; hash each after download.
4. Sensitive-data sweep: no `~/.cache/huggingface/token`, no `HF_TOKEN` or `hf_…` string in any
   history, rc file, script or log, no git credential store or `.netrc`, plain HTTPS remotes only.
   Then `rm -rf ~/.cache/huggingface`: model weights are someone else's disk quota until the wipe.
   **Count matches; never read grep's exit status as the verdict** (added 2026-09-10). `grep -rl PATTERN <files> && hits=1`
   is fail-open: one missing file in the list makes grep exit 2 even after it printed a match, so the sweep
   reports zero hits with the match visible above it. Use `grep -rls … | awk 'END{print NR}'` and compare the
   count. The E9-long sweep did exactly this, on a false positive, with no real secret on the box (learnings 2026-09-10).
5. Stop every process of ours; `ps -u $(whoami)` shows only the hub's own server (and the kernel
   used to look, which is deleted next). GPU processes that belong to other users' slices are not ours.
6. Stop the user server through the Hub API and verify the effect, not the response: the user record
   shows no server, the `/user/<u>/` route no longer answers 200, the Hub home page offers "Start My
   Server". Record the UTC time.
   **On a rented instance the effect is termination, and the proof expires** (added 2026-09-10): terminate, wait,
   and read the state back — not the API's acknowledgement — then record the UTC time, because the provider drops
   terminated instances from its listing within hours and the read-back stops being reproducible. Afterwards the
   durable form is the negative that persists: query by instance-id filter and require zero reservations, a check
   whose positive control is a live instance returning one. Also confirm no unattached volume survived the
   instance, and hold the termination until the summarizer has passed, so a refusal can still be re-scored on the
   same platform.
7. Report: box vs mirror report sha256 (must match), what step 3 pulled with sizes, what step 4 found,
   the stop response, the release time. No run numbers in the release report; the summarizer is where
   numbers are read.

**R8 — Backup is transport, not evidence.** The verified home mirror of `results/<exp>/` is pushed to
a Hugging Face dataset laid out so `hf download --repo-type dataset --local-dir results/<exp>`
reconstructs it with no translation, plus any gitignored upstream artifact the summarizer needs, in
upstream's own layout under its own top-level directory (E9: `mappers/qwen3-0.6b-to-1.7b/k1.*`). Push
only from the home mirror after verification, never from the box; small records first, kept dumps by
a single resumable `upload-large-folder` (one worker on Windows; learnings 2026-09-04), the
`complete: true` report last. After every push, `dataset_info(files_metadata=True)` and compare each
LFS file's `lfs.sha256` to the driver's fingerprint or the mirror's sha256; re-download and hash files
without an LFS entry; re-upload on mismatch, delete nothing. Nothing on the Hub is a ledger figure; the
summarizer reads the local mirror only. E9's dataset: `hossainpazooki/linear-ceiling-e9-2026-09-04`.
**Public is fine** (operator ruling; added 2026-09-11). The datasets hold KV tensors of public models over public
benchmark traces, so visibility is a storage choice: a public dataset downloads with no token and does not count
against the private storage allowance. Public raises the cost of a wrong push, so two things hold either way. Push
only from the staging tree: on 2026-09-10 an upload run from the repository root put 18,986 stray files, including
`.venv` and gitignored `results/`, into E9-long's dataset, which on a public dataset is immediate publication. And
sweep the staging tree's text files for credential shapes, with a planted positive control, before the first push,
as E9-long did. Dataset names stay out of double-blind paper material: a public name identifies its owner.
**A push is rate-limited by COMMITS, and backups compound in BYTES; both are budgeted before the sitting**
(added 2026-09-10). What first stopped E9-long's push was neither bytes nor scope: `429 … exceeded the rate
limit for repository commits (128 per hour)` at 247 of 724 files. A large mirror therefore needs several hourly
windows, and `hf_xet` batches commits inside the Python API too, so calling `upload_folder` instead of the CLI is
not a way around it; re-running the same command after the window resumes rather than restarts. Separately, the
bytes limit did bite later that day: a private dataset counts against the account's private storage allowance, and
E9-long's push stopped on `Private repository storage limit reached` at 482 of 724 files and again at 595, beside
~48 GB + 27.7 GB of earlier private backups; it finished only after the dataset was made public (E9-long runbook
section 6). Read the plan and the used storage while the run is still being planned, and do not infer either
failure from a stopped uploader: read the server's message. A finished upload command is not a finished backup — only the R8 verifier is.
**Never run a summarizer against a staging tree that is hardlinked and in flight** (added 2026-09-10): a
hardlinked stage shares inodes with `results/<exp>/`, so a re-run rewrote 17 summary and recheck files under a
live uploader. Copy the tree, or finish and verify the push first.

**R9 — Token hygiene.** Hub tokens are fine-grained, scoped to the one repo, and expiring; write tokens
for the pusher, read-only tokens for collaborators, named `<exp>-backup-<role>-<holder>-exp-<date>`.
A token lives in a process environment variable for the duration of the command, never in a `--token`
flag (shell history), never in a file inside a checkout, never in a chat message or a transcript; one
that has been pasted anywhere is revoked. A public dataset needs no read token. A private user-namespace repo
cannot be shared per user (learnings 2026-09-05): a collaborator gets a read token, or the repo moves to an
organization.

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
possible from a clean checkout, something is missing from R3 or R8. **Anchor every `re-verify:` line on something
we control** (added 2026-09-10): a brief proved a box release with a provider query that returned the instance's
`terminated` state, and three hours later the same command returned nothing, because the provider had forgotten
the record. A line that cannot tell 'false' from 'no longer knowable' verifies nothing. Point at a committed
file, a pulled log or a hash; where the fact really is a third party's state, use the form whose answer survives
the record's expiry and can still be distinguished by a positive control.

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

## The box, concretely (a rented cloud instance, ssh)

Added 2026-09-10 from the E9-long sitting. An hourly instance removes the transport traps of a hub-only grant —
ssh, scp and tar streams replace a kernel websocket and base64 uploads, there is no 40 s command ceiling and no
shared login — and replaces them with a meter and a delete. The instance bills until it is terminated, so arm a
self-halt at setup and terminate through the release checklist, never by walking away; the root volume dies with
the instance, so nothing may live only there. Pin the image by id, restrict ssh to the home address, and size the
disk for the kept dumps plus the transients. Capacity is not quota: a launch can be refused in one availability
zone and succeed in the next, so the launcher retries across zones. The stack pins stay the run's own, not the
image's defaults. `tools/ec2/` holds the lifecycle, setup, probe, launcher, puller, mirror verifier and release
sweep; the E9-long runbook is the worked example.

## Where the E9 instance of each rule lives

| rule | E9 record |
|---|---|
| R1 | 0019, 0023, 0025, 0026, 0027 (each opens with the no-score-file precondition) |
| R2 | 0026 probe table; learnings 2026-09-04 f32 SDPA |
| R3 | runbook §3b; gate commit `3ef9044` |
| R4, R5 | 0027 "Box discipline"; runbook §5 |
| R6, R7 | this session's release report (handoff 2026-09-05); step 0: the n = 420 runbook's 00:40Z incident (2026-09-09) |
| R8, R9 | HF dataset at commit `a45e9ee8`; learnings 2026-09-04 upload, 2026-09-05 sharing |
| R11 | 0028; learnings 2026-09-04 relative check |

The E9-long sitting (2026-09-10) is the rented-instance instance of the same rules: entries 0035 and 0036,
runbook `docs/2026-09-10-e9l-gpu-runbook.md` §§1–6, tooling `tools/ec2/`, and the 2026-09-10 learnings entries.

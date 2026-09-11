# A 401 that surfaces out of `hf upload` proves no credential reached the process, because `create_repo(exist_ok=True)` already swallows 401/402/403

kills: (nothing)
ts: 2026-09-10T03:38:00Z
commit: 50bc439b29b3f126b2f6a2f4b4a4b19bd994ef84
session: lcfm-sprint-e9l-review (9c42735d)
status: verified
fact: `hf upload` calls `api.create_repo(..., exist_ok=True)` before uploading anything, so a failed push
reports `401 Unauthorized for url .../api/repos/create` and reads as if the tool were trying to create a repo
that already exists, or as if the token lacked a create scope. Neither inference is safe. `create_repo`'s
`exist_ok` branch catches 409 AND 401, 402 and 403 — its own comment names the case, "401 -> if JWT token
without create repo scope" — and then calls `repo_info` to confirm the repo is there, re-raising only if that
ALSO fails. So a fine-grained token scoped to a single dataset with no create permission works fine, and a
401 that reaches the terminal means the request carried no usable credential at all. In this sitting the
credential was missing because `read -s HF_TOKEN && export HF_TOKEN` was the first line of a pasted block:
`read` consumes the next line of standard input, which in a paste is the block's next command, so the token
was never entered and `hf auth whoami` printed `Not logged in`. Run a `read` for a secret on its own, with
nothing pasted after it, and confirm with `auth whoami` before the long command.
basis: `sed -n '4836,4856p' .venv/Lib/site-packages/huggingface_hub/hf_api.py` at HEAD `50bc439` ->
  `elif exist_ok and err.response.status_code in (401, 402, 403):` followed by the three-case comment and
  `self.repo_info(repo_id=repo_id, repo_type=repo_type, token=token)`; `grep -n "create_repo"
  huggingface_hub/cli/upload.py` -> `211:        created = api.create_repo(`; observed in the operator's
  terminal at 03:30–03:38Z: `hf auth whoami` -> `Error: Not logged in` alongside
  `401 Unauthorized ... /api/repos/create` from the same binary.
re-verify: .venv/Scripts/python.exe -c "import inspect, huggingface_hub as h; print('(401, 402, 403)' in inspect.getsource(h.HfApi.create_repo))"   # True -> exist_ok swallows 401, so a surfaced 401 is a missing credential

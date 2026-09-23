# `hf upload` does not read the local .gitignore: a repo-root upload pushed .venv and the ignored results tree into the backup dataset

ts: 2026-09-10T14:55:05Z
commit: 50bc439b29b3f126b2f6a2f4b4a4b19bd994ef84
session: lcfm-sprint-e9l-review (9c42735d)
status: verified
fact: `hf upload <repo> .`, and the `HfApi.upload_folder` it calls, skips only `.git/` and `.cache/huggingface/`; the
local `.gitignore` is not consulted. Run from the linear-ceiling root instead of the staging tree on 2026-09-10, it
pushed 18,986 repository files into the private E9-long backup dataset, including 17,626 under `.venv/` and 1,121
under `results/`, both of which the repo's `.gitignore` ignores. An upload's scope is its path argument plus
`--include`/`--exclude`, nothing else, so the absolute staging path is the whole protection. `tools/hf_backup.sh`
passes it and never uploads `.`.
basis: the operator's pasted `tools/hf_prune_backup.py` dry run at 2026-09-10T14:55Z printed `extraneous 18,986`,
  by top-level path `.venv 17,626` and `results 1,121`, the remainder in `src/`, `tests/`, `docs/`, `traces/` and root
  files. `.gitignore` lines `1:.venv/` and `8:results/*`. The installed library's docstring, read
  2026-09-14T09:24:45Z at a5053b2 (huggingface_hub 1.28.0, the version the upload ran; post-dates this anchor):
  `HfApi.upload_folder` — "Any `.git/` folder present in any subdirectory will be ignored. However, please be aware
  that the `.gitignore` file is not taken into account."; `DEFAULT_IGNORE_PATTERNS` = `['.git', '.git/*', '*/.git',
  '**/.git/**', '.cache/huggingface', '.cache/huggingface/*', '*/.cache/huggingface', '**/.cache/huggingface/**']`. The
  `gitignore_content` argument of `preupload_lfs_files` applies a `.gitignore` committed to or hosted on the Hub, not
  the local file.
re-verify: .venv/Scripts/python.exe -c "import huggingface_hub as h; print(h.__version__, 'file is not taken into account' in (h.HfApi.upload_folder.__doc__ or ''))"   # expect: 1.28.0 True

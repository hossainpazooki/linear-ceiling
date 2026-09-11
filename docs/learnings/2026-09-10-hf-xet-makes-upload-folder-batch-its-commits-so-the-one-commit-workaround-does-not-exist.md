# With hf_xet installed, `HfApi.upload_folder` batches its commits exactly like the CLI, so "call the Python API for one commit" is not a fix

kills: (nothing)
ts: 2026-09-10T04:48:00Z
commit: 50bc439b29b3f126b2f6a2f4b4a4b19bd994ef84
session: lcfm-sprint-e9l-review (9c42735d)
status: verified
fact: After the R8 push hit the 128-commits-per-hour limit, I recommended replacing the CLI with
`HfApi().upload_folder(...)` on the strength of Hugging Face's own error text, which advises "upload entire
folders at once using the Hub Python library". Reading the installed source refutes the premise. In
huggingface_hub 1.28.0 `upload_folder` routes to the streamed pipeline of `_upload_pipeline.py` whenever
`hf_xet` is installed, and its own docstring says so: "large folders are automatically committed in several
batches to stay below server limits", with "If `hf_xet` is not installed, falls back to a single commit
created with `create_commit`". `hf_xet` IS installed in this venv, so the Python API takes the same batched
path the CLI took and cannot produce one commit. The only in-library lever is `HF_HUB_DISABLE_XET=1`, which
buys a genuine single commit at the cost of xet deduplication and resumability across 62 GB — a bad trade
when most blobs are already uploaded. The correct retry is therefore the same command after the window
clears: the pipeline starts at 250 files per commit and scales up, so 724 files need single-digit commits,
far under the limit. Rule: an error message's own remediation advice is a claim like any other, and the
library in the venv is the authority on what a call actually does.
basis: `.venv/Scripts/python.exe -c "import inspect, huggingface_hub as h;
  s=inspect.getsource(h.HfApi.upload_folder); [print(l.strip()) for l in s.splitlines() if 'large' in l]"` at
  HEAD `50bc439` -> the two docstring lines quoted above plus `return pipelined_upload(`; `import hf_xet`
  succeeds; `import huggingface_hub._upload_pipeline as p; print(p.INITIAL_COMMIT_SIZE_INDEX,
  p.COMMIT_SIZE_SCALE[p.INITIAL_COMMIT_SIZE_INDEX], p.MAX_COMMIT_INTERVAL)` -> `6 250 300.0`;
  `grep -n "HF_HUB_DISABLE_XET" huggingface_hub/constants.py` -> line 340.
re-verify: .venv/Scripts/python.exe -c "import huggingface_hub._upload_pipeline as p, hf_xet; print(p.INITIAL_COMMIT_SIZE_INDEX, p.COMMIT_SIZE_SCALE[p.INITIAL_COMMIT_SIZE_INDEX], p.MAX_COMMIT_INTERVAL)"   # 6 250 300.0 -> batched commits, and hf_xet imports, so upload_folder is not a single commit

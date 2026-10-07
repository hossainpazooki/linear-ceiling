# A staged figures script that never ran against a real report carried two fatal bugs — render every draft on a real or fabricated report before its sitting

ts: 2026-10-07T06:46:00Z
commit: d4d48a1
session: cache-behavior-0047-sitting (03ca9159; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\03ca9159-156a-4d71-9250-b553c1b73da3.jsonl)
status: verified
fact: `docs/drafts/append_0049.py` as staged on 2026-10-04 would have failed on ANY 0047 run, independent of the manifest
question: it read `report["code_sha256"]`, `["config_sha256"]`, `["manifest_sha256"]` and the GPU/runtime fields at the
top level, while `tools/cache_behavior/run.py` writes them under `report["identity"]` (KeyError on the first assertion);
and it loaded `run.py` with `importlib.util.spec_from_file_location`, which cannot execute that module's
`from .core import …` (ImportError). Neither was caught by its ordering guard, which fails first and so hides everything
behind it. The `append_0057.py` practice — render from a fabricated comparator output before any run exists — is the
test that would have found both; a staged figures script is not done until it has rendered against a report shaped like
the driver's.
basis: 2026-10-07 ~06:20Z: `git show d4d48a1:docs/drafts/append_0049.py | grep -c 'report\["code_sha256"\]'` → 1 and
  `grep -c spec_from_file_location` → 1; the real report's keys: top-level `['attention_scaling','complete','excluded',
  'git_commit','identity','inv_freq_sha256','model','model_revision','rope','run_order','scores']`, identity
  `['code_sha256','config_sha256','cublas_workspace_config','cuda','gpu','manifest_sha256','torch','transformers']`; first
  scratch render: `ImportError: attempted relative import with no known parent package`; after both fixes the scratch
  render (ordering guard pointed at 0050) produced the 631-word entry with rc 0.
re-verify: git show d4d48a1:docs/drafts/append_0049.py | grep -c -E 'report\["code_sha256"\]|spec_from_file_location'   # 2 (the staged version's two bugs; the working-tree copy has 0)

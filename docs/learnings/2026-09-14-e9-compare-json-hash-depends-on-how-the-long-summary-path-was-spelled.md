# `results/e9s/compare.json`'s sha256 depends on how `--long` was spelled: the path is recorded verbatim, so a standalone run and the append script's in-process run disagree by hash with every figure identical

kills: (nothing)
ts: 2026-09-14T03:28:28Z
commit: 12c113c2f9b0e32e6e74e340e266ff9e2a5f5acd
session: e9l-aws-run (transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\49de63b8-0b5e-4c48-bc32-84f1858c4ada.jsonl)
status: verified
fact: `e9_compare._long_cell` stores `"path": str(path)` for the `--long` summary, and `main` writes `compare.json` with
`write_text` and no `newline=`, i.e. CRLF on Windows. The standalone reader run with `--long results/e9l/summary.json`
wrote `compare.json` sha256 `a7aa6c32…`; `append_0038.py` passes `REPO_ROOT / "results" / "e9l" / "summary.json"` and its
in-process run wrote `a0699a82…`. Shown, not assumed: re-serializing the new file with CRLF reproduces `a0699a82` exactly,
and the same bytes with only `long_cell.path` set back to `results\e9l\summary.json` reproduce `a7aa6c32` exactly (with
LF, or with a forward-slash path, neither matches). A hash of `compare.json` is therefore a property of the invocation
form and the platform, not only of the figures: compare figures by field, or cite the hash with the exact command that
wrote it. The in-process form is deterministic (the same `a0699a82` on three runs).
basis: the test script's output at 03:28Z: `file on disk: a0699a82 CRLF` / `control, unmodified re-serialized CRLF: a0699a82`
  / `'results\\e9l\\summary.json' a7aa6c32` / `'results/e9l/summary.json' 9fac707e`; logs
  `results/e9s/logs/e9_compare.20260914T031959Z.log` (standalone, `a7aa6c32`) and
  `results/e9s/logs/append_0038.preview.20260914T032828Z.log` (in-process, `a0699a82`). Re-captured at a5053b2:
  `long_cell.path` reads `C:\Users\hossa\dev\linear-ceiling\results\e9l\summary.json`; `e9_compare.py:89` `"path": str(path)`.
re-verify: .venv/Scripts/python.exe -c "import json;print(json.load(open('results/e9s/compare.json'))['long_cell']['path'])" && grep -n '"path": str(path)' src/linear_ceiling/e9_compare.py   # an absolute path, then line 89

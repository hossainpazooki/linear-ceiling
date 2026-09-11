# A hardlinked HF staging tree is live: a summarizer re-run rewrites `recheck/` and `summary.*` under the uploader

kills: (nothing)
ts: 2026-09-10T03:20:00Z
commit: 3f67e4e + uncommitted (0036 appended; this session's outline fill)
session: dev-47 (9c42735d)
status: verified
fact: The R8 staging tree for E9-long was built by HARDLINK from `results/e9l/` (same NTFS volume; the box
session's brief says so). I re-ran `summarize_e9 --config config/e9l.toml` at home as an independent
re-verification while `hf.exe` was uploading that tree. The summarizer rewrites its own outputs in place
(`summary.json`, `summary.md`, `recheck/*.json`, `recheck/*.tokens.npz`, `recheck/bridge/*`,
`recheck/calibration/*`: 17 files, mtimes 23:03–23:12 local, link count 2), so the staging tree's copies
changed mid-upload. Every figure reproduced to the digit (cross 0.9639764831640834, ladder 0.1 → 0.011865…,
seam 16+ 0.0629, bridge CARRIED, HOLDS), but the per-token recheck arrays can differ bitwise between runs on
Windows (0028's thread-order jitter), so the Hub may carry either run's bytes for those 17 files depending on
upload order. The RECORD files — `report.json`, `scores/`, `tokens/`, `controls/`, `bridge/`, `align/`, the kept
dumps under `scratch/` — were not touched (newest mtime 21:13 local, before the re-run). Rule: never run a
summarizer on a mirror whose staging tree is hardlinked and in flight; either copy the staging tree (cp, not
ln) or wait for the R8 verifier to pass first. Regardless, the R8 verifier decides: run it after `hf.exe` exits,
and re-upload only the files it names.
basis: `find results/e9l -type f -newermt "2026-09-09 23:01" -printf '%n %TH:%TM %p\n'` → 18 files (17 + the
  re-run's own log), every one with link count 2; `ls -li` shows one inode for `results/e9l/summary.json` and
  `~/dev/hf-staging/linear-ceiling-e9l-2026-09-10/results/e9l/summary.json`; `tasklist | grep hf.exe` → pid 36596
  running at the time.
re-verify: find results/e9l -type f -newermt "2026-09-09 23:01" -not -path "*/logs/*" | wc -l   # 17; all under recheck/ or summary.*

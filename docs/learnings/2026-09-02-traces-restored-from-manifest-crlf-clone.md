# The manifest restores the corpus byte-for-byte, but a Windows clone hands back CRLF copies of the tau files

kills: (nothing)
ts: 2026-09-02T03:35:11Z
commit: 0732a31568fa5e0a5c286e241654002872d3729d
session: linear-ceiling-e9-amendment (018sSvHMwUtHXJF8EdMM5E8J)
status: verified
fact: The committed `config/e7-manifest.json` (entry 0024) carries sha256 and byte count for all
188 trace files and the S3 key for the 180 SWE-bench ones, so the emptied corpus was rebuilt
and proven identical: `e7_manifest fetch` (new) re-downloaded the 180 by anonymous HTTPS GET in
27 s, refusing any file whose bytes or sha differ from the manifest. The 8 tau-bench / tau2-bench
files have no S3 record; their sources are `sierra-research/tau-bench` `historical_trajectories/`
and `sierra-research/tau2-bench` `data/tau2/results/final/`, and a fresh clone of each under
`core.autocrlf=true` produced files 1.3% LARGER than the manifest with different hashes -- git
checked them out with CRLF. Normalizing CRLF to LF made all 8 match the manifest sha and size
exactly. `e7_manifest check` then reported 188/188. Corollary: a gitignored corpus is only as
restorable as its manifest; and a hash mismatch on a text file pulled from a Windows clone is a
line-ending question before it is a provenance question.
basis: `e7_manifest fetch` -> `fetch: restored 180, already present 0, without an S3 source 8`;
  clone copies: `tau-bench/gpt-4o-airline.json 97abc24223ce vs manifest e9e6c0297660 4167051
  4114038` (all 8 mismatched); after `.replace(b"\r\n", b"\n")`: `restored (LF-normalized, sha
  ok) tau-bench/gpt-4o-airline.json 4114038` (all 8); `e7_manifest check` -> `manifest ok: 188
  files match disk; sha256 371fb4bf3cb0...`.
re-verify: .venv/Scripts/python.exe -m linear_ceiling.e7_manifest check

# The Llama cell's R8 backups exist under a co-author's Hub account and verify against every 0040–0044 pin

ts: 2026-10-01T04:47:31Z
commit: 0a51275
session: Carryover: MLSys NeurIPS Sprint (701ace2c; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\701ace2c-47a9-4419-b1e3-4011d7fc7e7f.jsonl)
status: verified
fact: The 09-28 note found no backup under the project account. The backups exist under `emmmy/`:
`linear-ceiling-e8f-2026-09-18` (159 files, 9.8 GB) and `linear-ceiling-e9f-2026-09-19` (1,054 files, 55.4 GB),
public, pushed 2026-09-30 05:58Z and 08:00Z. Every sha the entries pin matches the Hub copy (E8 report 4682508afd35,
r2.json 8498e977785e, k1.json 6cbfad42b6b0, coverage 6a8dc1242300, agent tokens 4e02d14af008, both config pins
as git stores them); all 28 score files, 28 token records, the three controls and 784 of 784 kept-dump files match
the report's fingerprints; `tools/hf_verify_backup.py` printed `BACKUP VERIFIED` on a full local mirror of each
(e8f: 135 LFS compared, 23 hashed, 0 problems; e9f: 888 LFS, 165 hashed, 0 problems). The e8f dataset keeps the
generic dumps in the upstream's `data/kv` layout rather than under `results/`; the fingerprints match, so it is a
layout note. The two empty `hossainpazooki/…-e8f/-e9f` datasets created 09-30 are superseded. R12 on 0040/0044 still
needs one summarizer run on the mirror with the clone at 06f8d55.
basis: at 0a51275, 2026-10-01T04:47:31Z, the Hub API printed `emmmy/linear-ceiling-e8f-2026-09-18 private False
  files 159 2026-09-30T05:58:10.000Z` and `emmmy/linear-ceiling-e9f-2026-09-19 private False files 1054
  2026-09-30T08:00:30.000Z`. The verifier outputs (`lfs-compared 135, downloaded+hashed 23, problems 0 / BACKUP
  VERIFIED`; `repo emmmy/linear-ceiling-e9f-2026-09-19 @ ab7d0fd0 | remote 1053 files | local 1053 files /
  lfs-compared 888, downloaded+hashed 165, problems 0 / BACKUP VERIFIED`) were captured earlier in the session at
  5a71df6 against mirrors at `~/dev/lc-mirror/e8f` and `C:\m\e9f` (pre-date this entry's anchor; the mirrors are
  unchanged since).
re-verify: curl -s https://huggingface.co/api/datasets/emmmy/linear-ceiling-e9f-2026-09-19 | grep -o '"private":[a-z]*\|"lastModified":"[^"]*"'   # expect "private":false and 2026-09-30T08:00:30

# A mirror that skips files of equal size is blind to a rewritten binary of the same length; 68 align npz files differed byte-wise with identical arrays

kills: (nothing)
ts: 2026-09-04T18:24:54Z
commit: 0a19b56ee3bd4b45eca28f84a20cf6ded4dcd436
session: algoverse-gpu-run-session (8a0fb97e-0020-43aa-a9b2-9ae67eec2fe3)
status: verified
fact: The E9 puller's mirror() skipped any remote file whose size matched the local copy. The box
regenerated results/e9/align/ at 16:42 UTC (e9 --align-only on the box), while the home copies dated
from 09-02, so at release every one of the 68 align/*.npz files had a different sha256 on the box
than at home and had never been re-pulled; all 68 align/*.json files were byte-identical. Hashing
the arrays inside the npz (name, dtype, shape, bytes) gave identical digests on both sides for all
68, so the run read the same alignments the summarizer reads and the difference was container
bytes (numpy zip writer), not content. The check that caught it was a full sha256 listing of both
sides diffed by path, not the puller's own log. tools/jupyterhub/pull.py now records remote size
AND last_modified per file and re-pulls on either changing.
basis: box `find . -path ./scratch -prune -o -type f -print0 | xargs -0 sha256sum` (195 files) vs
  the same over the mirror (196: + align/coverage.json, home-made): 68 paths differ, all
  `align/*.npz`, 0 non-align; array-content hashes (np.load, per key: name+dtype+shape+tobytes)
  computed on both sides: `diff` empty, 68/68 identical; the two npz zip entries carry a fixed
  1980-01-01 mtime, so the byte difference is not timestamps.
re-verify: grep -n "last_modified" tools/jupyterhub/pull.py

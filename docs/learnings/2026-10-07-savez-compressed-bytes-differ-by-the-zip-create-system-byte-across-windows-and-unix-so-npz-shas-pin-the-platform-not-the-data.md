# `np.savez_compressed` bytes differ across Windows and Unix by one zip header byte (`create_system` 0 vs 3), so an `.npz` sha pins the platform, not the data

ts: 2026-10-07T01:36:11Z
commit: 580f73c
session: cache-behavior-0047-sitting (03ca9159; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\03ca9159-156a-4d71-9250-b553c1b73da3.jsonl)
status: verified
fact: The same `tools/cache_behavior/run.py --prepare` on the same inputs, same numpy 2.5.3 and same zlib output, gave
35 `.npz` files whose `.npy` members were byte-identical on Windows and WSL but whose file shas agreed on 0 of 35. The
only difference is the zip entry header's `create_system` field, which Python's `zipfile` sets to 0 on Windows and 3
elsewhere (numpy already pins the timestamp to 1980-01-01). So a manifest that records `.npz` shas (0047's input
manifest, 0046's `consolidation-manifest.json`) can be reproduced only on the platform family that wrote it; both pilots
were prepared on Unix. Prepare on Linux (WSL here), never on Windows.
basis: 2026-10-07 ~00:30Z, Windows `.venv-cb` vs WSL `~/lc-venv`: `records equal windows vs linux: 0 of 35`; member
  comparison `all .npy members byte-identical: 35`; zip header tuple `(create_system win, linux) = (0, 3)`, compressed
  sizes equal. Fixed-buffer `zlib.compress(level 6)` sha `c184b3715ea82d47` identical on both. The WSL run of
  `tools/consolidation/prepare.py` reproduced the frozen `config/consolidation-manifest.json` byte-for-byte (clean
  `git status`), the Windows run differed on all 126 record shas.
re-verify: .venv-cb/Scripts/python.exe -c "import io,zipfile,numpy as np;b=io.BytesIO();np.savez_compressed(b,a=np.arange(3));print(zipfile.ZipFile(b).infolist()[0].create_system)"   # 0 on Windows; the same line prints 3 under WSL/Linux

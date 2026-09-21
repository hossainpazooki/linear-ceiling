# The k = 1 map behind τ_K was fit on 40 of the 50 archived sequences; τ_K comes from the other 10, so "fit on 50 sequences" beside "held-out on its calibration corpus" reads as a contradiction

kills: (nothing)
ts: 2026-09-14T09:27:47.740Z
commit: a5053b2f1d453235c87ce07e9f30f95524a2a590
session: model-context-window-comparison (transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\2f2c397b-6f7c-4aee-84c4-1509767d1a1b.jsonl)
status: verified
fact: The upstream mapper report records 10,240 training tokens and 2,560 held-out tokens. Entry 0023 takes τ from the
held-out sequences, "the last 10 of the 50" archived dumps, so each sequence contributes 256 tokens and the fit used 40
sequences. Entry 0033 (line 1962) says the map was "fit upstream on 50 calibration sequences (10,240 training tokens)",
and the 2026-09-14 manuscript copies "fit on 50 generic sequences" while also saying τ_K is the map's held-out error on
its calibration corpus. A reader cannot hold both. Write "fit on 40 of 50 generic sequences, 10 held out".
basis: `python -c "...r2.json..."` printed `n_train_tokens 10240 n_heldout_tokens 2560 k1 K heldout 0.6814`;
  `grep -n "50 calibration sequences (10,240 training tokens)" ledger/ledger.md` printed line `1962`;
  `grep -n "last 10 of the 50" ledger/ledger.md` printed line `1283`.
re-verify: .venv/Scripts/python.exe -c "import json;d=json.load(open('../kv-transfer-replication/results/mapper/qwen3-0.6b-to-1.7b/r2.json'));print(d['n_train_tokens'],d['n_heldout_tokens'])" && grep -n "last 10 of the 50" ledger/ledger.md   # 10240 2560, then line 1283

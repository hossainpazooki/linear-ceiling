# The E9 context-cap ladder has a knee at 81,920: the last four excluded handoffs need 147K–358K

kills: (nothing)
ts: 2026-09-09T03:57:39.005Z
commit: 4eafe40290a1b6525fe747532a768e15a0ca73c3
session: linear-ceiling-lcfm (018R4BNzaMfGpTZaCSocf8Sc)
status: verified
fact: H-E9 (0029) was decided on the 25 of 68 handoffs whose sender prompt fits the registered 32,768-token
cap; 39 are excluded for length and 4 for an empty receiver prompt. Raising the cap does not admit the
excluded handoffs smoothly: 40,960 (Qwen3's native `max_position_embeddings`) admits 8; 65,536 admits 31;
81,920 admits 35; 131,072 admits no more than 81,920 (still 35); the last four need 147,218 to 357,623
tokens. Every excluded RECEIVER prompt fits the native window (max |R| 25,073), so only the sender side
needs a longer context. A long-half experiment should therefore be planned at cap 81,920, not 131,072:
doubling the memory budget past 81,920 buys zero handoffs. The seed `docs/2026-09-08-seed-e9-long-half.md`
§1 carries the full ladder and names the eight that stay excluded.
basis: `.venv/Scripts/python.exe -c` over `results/e9/align/2024*.json` (68 records, local mirror) at HEAD 4eafe40:
  `excluded_long 39 le_65536 31 le_81920 35 le_131072 35 maxR 25073`. Coverage record
  `results/e9/align/coverage.json`: `"observed": 68, "included": 25, "excluded": 43`, exclusion reasons
  `S exceeds context cap 32768` (39) and `receiver prompt is empty in the trace` (4).
re-verify: cd ~/dev/linear-ceiling && .venv/Scripts/python.exe -c "import json,glob; r=[json.load(open(p,encoding='utf-8')) for p in glob.glob('results/e9/align/2024*.json')]; ex=[x for x in r if x['excluded'] and 'cap' in (x['reason'] or '')]; print(len(ex), sum(x['n_sender']<=81920 for x in ex), sum(x['n_sender']<=131072 for x in ex))"   # 39 35 35; needs the local results/e9 mirror (HF backup linear-ceiling-e9-2026-09-04)

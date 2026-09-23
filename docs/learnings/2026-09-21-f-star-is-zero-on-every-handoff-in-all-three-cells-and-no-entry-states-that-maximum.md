# f*(τ_K) is zero on every handoff in all three cells, and no ledger entry states that maximum

ts: 2026-09-21T02:38:04Z
commit: 3d2fbb14d3919cd2e798f4ffbe5132506cef1c7b
session: carryover-iclr-pickup-drift-wrapup (e7805827; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\e7805827-47f9-400a-a107-71d2eeb94fb2.jsonl)
status: verified
fact: The handoff-level universal "same-model f*(τ_K) = 0 on every handoff" is supported by the summarizer's own
per-handoff values in all three cells: the maximum is 0.0 and no handoff is nonzero over 25 (0029), 35 (0036) and 25
(0038) handoffs. An outside review on 2026-09-14 could not verify it, because 0029 / 0036 / 0038 state only a median, a
p10, a p90 and a bootstrap interval, and none of those bounds a maximum. The token-level universal ("at every matched
token") is a different claim and is false (learning 2026-09-14, f-star-zero-says-the-mean-is-within-tau-k). A paper
sentence may say "on every handoff" only once a numbered entry states the maximum; this entry is not that.
basis: at 3d2fbb1, 2026-09-21T02:38:04Z, the re-verify line below printed `e9 25 0.0 0`, `e9l 35 0.0 0`, `e9s 25 0.0 0`
  (cell, handoffs, max, count nonzero). `awk '/^### 0029/,/^### 0030/' ledger/ledger.md | grep -c -i "maximum\|max f\*"`
  printed `0`. First read at a5053b2 on 2026-09-20 with the same three lines; re-captured here against this anchor.
re-verify: .venv/Scripts/python.exe -c "import json;[print(e,len(v),max(v.values()),sum(x>0 for x in v.values())) for e in ('e9','e9l','e9s') for v in [json.load(open(f'results/{e}/summary.json'))['fstar_per_handoff']['same_K']]]"   # expect: e9 25 0.0 0 / e9l 35 0.0 0 / e9s 25 0.0 0

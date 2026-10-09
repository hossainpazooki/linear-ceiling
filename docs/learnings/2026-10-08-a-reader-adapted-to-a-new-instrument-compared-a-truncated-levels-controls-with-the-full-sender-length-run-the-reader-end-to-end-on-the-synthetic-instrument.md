# A reader adapted to a new instrument compared a truncated level's controls with the FULL sender length; run the reader end to end on the synthetic instrument before the card time

ts: 2026-10-08T23:43:00Z
commit: b33c6ce
session: e-trunc-0057-sitting (03ca9159; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\03ca9159-156a-4d71-9250-b553c1b73da3.jsonl)
status: verified
fact: E-TRUNC (0055) keeps the FULL |S| in every level's alignment record on purpose — inclusion and run order are decided
on the full sender — while a truncated level prefills S′ = S[−L:]. Its identity and bridge controls therefore cover
min(|S|, L) positions. `summarize_e9` compared the identity control's pair count with the record's `n_sender` and refused
L65 ("identity control did not cover every sender position") on a correct control: 65,536 pairs, every square exactly
zero, R² 1.0, against `n_sender` 80,111. The 0055 build had tested the truncated ALIGNMENT and the run order
(`tests/test_e9_trunc.py`) but never ran `summarize` on a truncated synthetic level, which is the one test that would
have caught it a week before the card time. Fix: the reader expects `_dumped_sender_len` (|S| without truncation,
min(|S|, L) with); a test now runs driver + summarizer on a truncated synthetic level. Rules: (1) when an instrument
gains a new mode, add the end-to-end reader test on that mode in the same change — adapting the alignment is not
adapting the reader; (2) a refusal on a control whose own record says "zero squares, full coverage of what was dumped" is
a reader question first; (3) say the correction in the figures entry from the records, as 0057 does.
basis: `results/e9t-l65/report.json` (`controls.identity.n_pairs` 65536, `max_abs_square` 0.0; alignment `n_sender`
  80111; `sender_head_truncate` 65536); runbook `docs/2026-10-04-e-trunc-gpu-runbook.md` §6 20:46:59–20:48:38 and
  20:50:56–20:53:00; `tests/test_e9_trunc.py::test_summarizer_reads_a_truncated_level_whose_controls_cover_the_dumped_sender`.
re-verify: .venv/Scripts/python.exe -c "import json;r=json.load(open('results/e9t-l65/report.json'));c=r['controls'];a={x['handoff_id']:x for x in r['alignments']}[c['handoff_id']];print(c['identity']['n_pairs'],a['n_sender'],r['sender_head_truncate'],c['identity']['max_abs_square'])"   # 65536 80111 65536 0.0

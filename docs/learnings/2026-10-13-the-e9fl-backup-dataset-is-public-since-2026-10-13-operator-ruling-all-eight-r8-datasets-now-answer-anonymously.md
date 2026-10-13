# The e9fl backup dataset is public since 2026-10-13 (operator ruling); all eight R8 datasets now answer anonymously

ts: 2026-10-13T16:41:07Z
commit: 23c391d
session: lc-0060-pr19-agents-md-tables (03ca9159; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\03ca9159-156a-4d71-9250-b553c1b73da3.jsonl)
status: verified
fact: The operator made `hossainpazooki/linear-ceiling-e9fl-2026-10-07` public on 2026-10-13. The 2026-10-12 learning that
recorded it as private (401) described the state at that date and is not wrong; this entry closes the ruling it left open.
The dataset revision is unchanged (`cd76559344d5`, the one T04 recomputed from), so T04's "private; downloaded with read
access" is a true statement about 2026-10-11 and stays as approved. README and `docs/paper-to-record.md` now say public.
basis: `curl -s -o /dev/null -w '%{http_code}\n' https://huggingface.co/api/datasets/hossainpazooki/linear-ceiling-e9fl-2026-10-07`
  = `200`; the JSON body gives `private False gated False sha cd76559344d5` (captured 2026-10-13T16:41:07Z at 23c391d).
re-verify: curl -s https://huggingface.co/api/datasets/hossainpazooki/linear-ceiling-e9fl-2026-10-07 | grep -o '"private":[a-z]*'   # "private":false

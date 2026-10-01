# The E9 report names score and token files by bare filename; a verifier must prefix results/<cell>/scores and tokens

ts: 2026-10-01T04:47:34Z
commit: 0a51275
session: Carryover: MLSys NeurIPS Sprint (701ace2c; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\701ace2c-47a9-4419-b1e3-4011d7fc7e7f.jsonl)
status: verified
fact: `report.json` `scores[<hid>].score_file` and `.tokens_file` are bare names (`<stem>.json`, `<stem>.tokens.npz`),
and `controls.<name>.score_file` likewise; the directories (`scores/`, `tokens/`, `controls/`) are implied by
`summarize_e9`, which joins them itself. A fingerprint check that uses the recorded strings as repository paths
reports every score and token file MISSING (59 of them on the e9f backup today) while the files are present and
match by hash once the directory is prefixed. Kept-dump fingerprints, by contrast, are keyed by arm and filename under
`scratch/<stem>/<arm>/`.
basis: at 0a51275, 2026-10-01T04:47:34Z, a read of `results/e9l/report.json` printed
  `'20241016_composio_swekit__astropy__astropy-7671_traj_sw85.json'
  '20241016_composio_swekit__astropy__astropy-7671_traj_sw85.tokens.npz'` for the first score entry. Earlier in the
  session the first pass of the e9f backup check reported `28 ('score_file', 'MISSING-ON-HUB')`, `28 ('tokens_file',
  'MISSING-ON-HUB')`, `3 ('control_score', 'MISSING-ON-HUB')`; with the directories prefixed the same pass printed
  `28 ('score_file', 'OK')`, `28 ('tokens_file', 'OK')`, `3 ('ctrl_score', 'OK')`, `3 ('ctrl_tokens', 'OK')`.
re-verify: .venv/Scripts/python.exe -c "import json; e=next(iter(json.load(open('results/e9l/report.json'))['scores'].values())); print(e['score_file'], '/' in e['score_file'])"   # expect a bare filename and False

# A retire step in a commit block ran after the append it was written to follow had refused

kills: (nothing)
ts: 2026-09-02T20:15:00Z
commit: cb80ad0
session: linear-ceiling-e-rl-design (session_01DksT5fTgXwHmKFfgLSXmnT)
status: established
fact: `f8cecf7` staged `docs/drafts/append_0025.py` together with the instrument it registers
(`config/e9.toml` keep n 3 → 8 and `tau_ladder`). The script's "nothing to register" guard read
the PRIOR keep n from `HEAD:config/e9.toml` -- but the emitted commit block committed the config
BEFORE running the append, so HEAD already said 8, the guard saw 8 == 8 and REFUSED (exit 2). The
block's next lines (`git add ledger/ledger.md` on an unchanged ledger, `git rm` the script,
commit "retire after append") ran regardless: `cb80ad0` deleted the only script that could append
0025 while the ledger carried no 0025, and `e9.REQUIRED_ENTRIES` (also in `f8cecf7`) named an
entry that did not exist, so `e9 --check` refused on origin. Two defects: a guard that contradicted
the commit order its own author emitted, and a sequential commit block with no `&&` / exit-code
gate between a step that can refuse and the destructive step after it.
Rule: (1) a draft script's "prior value" comes from a PINNED revision or the ledger, never from
HEAD; (2) every emitted commit block chains a refusable step to the steps after it with `&&`, and
a retire/delete step is written `test -f <appended marker> && git rm ...`, never bare;
(3) after any append, `grep -c '^### NNNN' ledger/ledger.md` before retiring.
basis: `git show cb80ad0 --stat` (one deletion, no ledger change); `git show HEAD:ledger/ledger.md
| grep -c '^### 0025'` -> 0; `git show f8cecf7:docs/drafts/append_0025.py | grep -n committed_keep_n`
(the HEAD read); `git show f8cecf7:config/e9.toml | grep '^n = '` -> `n = 8`.
re-verify: `cd ~/dev/linear-ceiling && git show cb80ad0 --stat | tail -3 && git show cb80ad0^:ledger/ledger.md | grep -c '^### 0025'` (expect a single deletion and 0).

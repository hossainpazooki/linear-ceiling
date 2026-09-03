# The retire-before-append entry restated: its `status:` value was not one of the three the gate allows

kills: 2026-09-02-retire-step-ran-after-a-refused-append.md
ts: 2026-09-03T04:06:36Z
commit: 5960c20
session: linear-ceiling-rl-design (session_01DksT5fTgXwHmKFfgLSXmnT)
status: verified
fact: The 2026-09-02 entry carried `status: established`, which `check-learnings` rejects ("missing
or malformed required field: status" -- the value must be exactly `verified`, `refuted-assumption`
or `suspected`). The fact it recorded stands and is restated here unchanged: `cb80ad0` deleted
`docs/drafts/append_0025.py` after the script's "nothing to register" guard had REFUSED (it read
the prior keep n from `HEAD:config/e9.toml`, which the instrument commit `f8cecf7` had already
moved to 8), and the ledger at `cb80ad0^` carried no 0025. Rule unchanged: a draft script's prior
value comes from a pinned revision or the ledger, never HEAD; a retire/delete step is chained to
the append with `&&` and a ledger grep, never bare. Second rule, from this entry: emit the
`status:` value as one of the three words, nothing else -- the gate is a dialect, and a
substance-complete entry fails it on the value alone.
basis: `git show cb80ad0 --stat` -> `docs/drafts/append_0025.py | 190 ----` / `1 file changed, 190 deletions(-)`;
`git show cb80ad0^:ledger/ledger.md | grep -c '^### 0025'` -> `0`;
`git show f8cecf7:docs/drafts/append_0025.py | grep -n committed_keep_n` -> `41:def committed_keep_n() -> int:` / `165: old_n = committed_keep_n()`.
re-verify: `git show cb80ad0 --stat | tail -1 && git show cb80ad0^:ledger/ledger.md | grep -c '^### 0025'` (expect one 190-line deletion and 0).

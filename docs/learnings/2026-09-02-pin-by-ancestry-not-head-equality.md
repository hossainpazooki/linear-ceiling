# An upstream pin checked as HEAD-equality breaks the previous experiment at the next re-pin

kills: (nothing)
ts: 2026-09-01T22:10:51Z
commit: 151bb719e05231fdd12fc8766b1668c427655d5c
session: linear-ceiling-venue (edf43652-2973-456b-85d0-6d6dd532713a)
status: verified
fact: E8's first gate required the upstream HEAD to EQUAL its pinned sha. E9's registration
then had to add a script upstream, moving HEAD one commit past E8's pin — which would have
made E8's gate and summarizer refuse forever, a false alarm about tools that had not changed
by a byte. The pin's real claim is "the tools I invoke are the pinned bytes", and the check
that expresses it is three-part (`upstream_gate.check_upstream`): the pinned commit is HEAD or
an ancestor of HEAD; `git diff --quiet <pin> HEAD -- <invoked paths>` is clean; the working
tree is clean for those paths. Under that rule E8 (pin 71df450) passes with the upstream at
7e41f792 while any edit to dump_kv.py, score_mapper.py, or kvt/ still refuses. Corollary for
any repo pinning a moving instrument: one full pin per experiment recorded where the
experiment reads it, HEAD-equality nowhere.
basis: with the upstream at 7e41f792 (one commit past E8's pin 71df450), captured
  2026-09-01T22:10:51Z: `python -m linear_ceiling.e8 --check` ->
  `E8 gate: ready (entries 0009/0016 committed; upstream pinned and clean)`;
  `git -C ../kv-transfer-replication log --oneline -2` -> `7e41f79 feat: score_positions.py...`
  / `71df450 feat: score_mapper.py...`.
re-verify: .venv/Scripts/python.exe -m linear_ceiling.e8 --check

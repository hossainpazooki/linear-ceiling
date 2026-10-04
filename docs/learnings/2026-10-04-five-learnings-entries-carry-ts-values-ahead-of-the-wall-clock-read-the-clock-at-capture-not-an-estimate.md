# Five learnings entries carry `ts:` values ~1.5 h ahead of the wall clock: the session estimated the time instead of reading it

ts: 2026-10-04T08:26:00Z
commit: 01b660b (basis captured at 366a4db, pre-dates this entry's anchor)
session: d4f6aa2f (transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\d4f6aa2f-529e-4861-9322-e476f4693f66.jsonl)
status: verified
fact: The five 2026-10-04 learnings committed in 366a4db carry ts 09:30Z, 09:35Z, 09:40Z, 09:45Z and 09:50Z, yet the commit that contains them was made at 2026-10-04T04:11:10-04:00 = 08:11:10Z, and `date -u` run in the same session fifteen minutes later printed 08:26Z. The session had typed times it believed to be current rather than reading the clock, so every one of those entries is stamped after it existed. The facts and bases in them stand; only the anchors are wrong, and distinct-but-wrong timestamps pass the identical-timestamp check. Rule: `ts:` is read off `date -u` at the moment the basis lands and copied, never composed.
basis: `date -u +'now %Y-%m-%dT%H:%MZ'` → `now 2026-10-04T08:26Z`; `git log -1 --format='%h committed %cI' 366a4db` → `366a4db committed 2026-10-04T04:11:10-04:00`; `grep -h '^ts:' docs/learnings/2026-10-04-*.md` → the five values above.
re-verify: git log -1 --format='%cI' 366a4db; grep -h '^ts:' docs/learnings/2026-10-04-a-gate-measured-for-free-*.md   # the commit time (08:11Z) precedes the entry's ts (09:30Z)

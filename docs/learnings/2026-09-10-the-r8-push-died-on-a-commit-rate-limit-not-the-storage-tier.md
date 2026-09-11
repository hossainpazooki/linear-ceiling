# The E9-long R8 push died on Hugging Face's 128-commits-per-hour repository limit, not on the free storage tier

kills: 2026-09-10-the-third-private-hf-backup-crosses-the-free-tier-check-quota-before-the-sitting.md
ts: 2026-09-10T03:47:00Z
commit: 50bc439b29b3f126b2f6a2f4b4a4b19bd994ef84
session: lcfm-sprint-e9l-review (9c42735d)
status: verified
fact: The superseded entry inferred, from an `hf.exe` that was no longer running and left no resume state,
that the push had hit the free 100 GB private allowance and "would fail roughly 24 GB in". The server said
otherwise, in the operator's terminal, in words: `429 Too Many Requests for url:
https://huggingface.co/api/datasets/hossainpazooki/linear-ceiling-e9l-2026-09-10/commit/main. You have
exceeded the rate limit for repository commits (128 per hour). You can retry this action in about 1 hour.`
The push had committed 247 of 724 files at that point, so it was well past the small records, and the limit
counts commits, not bytes. Two consequences. First, the first retry is the same command after the window
clears, NOT a plan upgrade or a scramble to free space. Second, the arithmetic in the superseded entry
survives as a separate and still-unverified risk for the NEXT attempt, and is restated here so it is not
lost: staging measures 61,937,723,784 B, and the repo documents two prior private datasets at ~48 GB (E9,
2026-09-04) and 27.7 GB (n420, 2026-09-08) against Hugging Face's free 100 GB private allowance; those two
sizes are the repo's own figures and were never measured against the Hub, so ~75.7 GB is a lower bound on
what is stored. A storage ceiling may well bite on a later attempt; it is not what stopped this one. The
429 is a transient server condition and cannot be re-executed, so this entry's basis is a captured quote
rather than a runnable line, exactly the shape
`2026-09-10-a-re-verify-line-anchored-on-a-providers-transient-record-rots-within-hours` warns about.
basis: the operator's terminal at 2026-09-10T03:47Z, quoted verbatim above, under the progress line
  `Committing  ██████░░░░░░░░░░░░░░  247 / 724`; the command was
  `hf.exe upload hossainpazooki/linear-ceiling-e9l-2026-09-10 . --repo-type dataset` from
  `~/dev/hf-staging/linear-ceiling-e9l-2026-09-10`, with `hf.exe auth whoami` printing `user: hossainpazooki`
  immediately before it. Staging size and the two prior figures are the superseded entry's own measurements,
  re-stated unchanged.
re-verify: .venv/Scripts/python.exe tools/hf_verify_backup.py hossainpazooki/linear-ceiling-e9l-2026-09-10 ~/dev/hf-staging/linear-ceiling-e9l-2026-09-10 --exclude README.md   # needs a read token in $HF_TOKEN; prints BACKUP VERIFIED, or the files still missing

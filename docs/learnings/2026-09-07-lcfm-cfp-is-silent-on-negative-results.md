# The LCFM 2026 call says nothing about negative, preliminary or ongoing results; "Robust evaluation" is the only topic hook

kills: (nothing)
ts: 2026-09-07T03:56:21Z
commit: 74c35fd964262bb7d7685f7df76ffeab074996b0
session: lcfm-sprint-pickup (e992199e-cc8f-4335-bce4-fa177630087c)
status: verified
fact: the workshop page (longcontextfm.github.io, fetched twice this session) contains no occurrence of
"negative", "ongoing", "work in progress" or "preliminary"; it states the deadline (September 10, 23:59
AoE), 4-page short / 8-page long excluding references and appendix, non-archival, and that submissions
under review elsewhere are accepted subject to the other venue's policy. Its topic list has no caching,
serving or inference keyword (a 09-01 finding, re-confirmed) and one line the program fits: "Robust
evaluation", beside "Long-context and long-horizon agentic foundation models". The mentor's action
item "check whether the workshop accepts negative or ongoing results" therefore has no answer on the
page: the submission must be framed as an evaluation of what the public record can evidence, not as
a negative result, and a reviewer's tolerance for a negative headline is unknown, not established.
basis: `curl -sL https://longcontextfm.github.io/` at 2026-09-07T03:56:21Z (18,805 bytes) piped through
  `grep -o -i <word> | wc -l`: negative 0, ongoing 0, "work in progress" 0, preliminary 0,
  "Robust evaluation" 1, non-archival 1, "September 10" 1. Earlier the same session, WebFetch of the same
  URL quoted verbatim: "Submission Deadline: September 10, 2026, 23:59 AOE"; "We welcome short papers
  up to 4 pages or long papers up to 8 pages, not including references or appendix."; "This is a
  non-archival workshop."; "We accept submissions that are under review at other venues (e.g., ICLR
  2027), as long as this does not violate the dual-submission / anonymity policy of the other venue."
re-verify: curl -sL https://longcontextfm.github.io/ | grep -o -i "negative\|ongoing\|preliminary" | wc -l   # 0 as of 2026-09-07; a policy line would make this nonzero

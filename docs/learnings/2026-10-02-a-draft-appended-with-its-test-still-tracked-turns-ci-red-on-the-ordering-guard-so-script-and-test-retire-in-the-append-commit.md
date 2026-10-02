# A draft appended with its test still tracked turns CI red on its own ordering guard; the script and its test retire in the append commit

ts: 2026-10-02T03:33:00Z
commit: 470133e
session: dev-fd (f87605d5; transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\f87605d5-fe82-43ce-b903-815d591b48ad.jsonl)
status: verified
fact: Commit b3bf7ec appended entry 0045 but left `docs/drafts/append_0045.py` and `tests/test_append_0045.py` tracked. CI then ran the test, which builds the entry against the committed ledger; the draft's ordering guard saw 0045 already present and raised `ordering: 0044 present, 0045 absent`, failing two tests. The next commit, 470133e, removed both files and CI went green. The guard did its job; the lesson is procedural: an append script's test imports the script by path and encodes the pre-append ledger state, so both files leave in the same commit as the ledger change, never one commit later.
basis: at 470133e (HEAD when read), ~03:33Z: `gh run view 36960475923 --log-failed` printed `E ValueError: ordering: 0044 present, 0045 absent` twice and `FAILED tests/test_append_0045.py::test_entry_states_the_cells_figures_and_the_candidate_ledger_checks`, `FAILED tests/test_append_0045.py::test_the_e7_hash_paragraph_appears_only_with_the_llama_cell`; `gh run list` showed b3bf7ec `failure` (03:30:31Z) and 470133e `success` (03:32:14Z); `git show --stat 470133e` printed `docs/drafts/append_0045.py | 295 ---` and `tests/test_append_0045.py | 109 ---`. Re-captured at write (04:37Z): `gh run list` still prints `b3bf7ec failure`.
re-verify: gh run list --limit 8 --json headSha,conclusion --jq '.[] | select(.headSha[0:7]=="b3bf7ec") | .conclusion'   # expect failure; 470133e is the fix

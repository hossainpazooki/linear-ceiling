ts: 2026-09-09T02:22:00Z
commit: a71c3b4
session: Claude Code session 878feb6f, HF backup push (operator's shell)
status: verified
fact: `hf.exe upload-large-folder ... --include "<dir>/*"` fails on Windows even with the pattern double-quoted in bash and MSYS conversion disabled: the expansion happens on the Python side (forward slashes up to the last directory, a backslash after, i.e. `glob` output), the first match becomes the `--include` value and the rest are "unexpected extra arguments". `--include` is also one pattern per flag. The working form passes no patterns and uploads the whole staged tree.
basis: operator's terminal: `Error: Got unexpected extra arguments (data/kv/qwen3-0.6b-to-1.7b-n420/source\layer01.npz data/kv/qwen3-0.6b-to-1.7b-n420/source\layer02.npz ...)`, identical with and without `MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL="*"`; the pattern-free run: `Files: hashed 89/89 (27.7G/27.7G) | pre-uploaded: 61/61 | committed: 89/89 ... Upload is complete!` in 7 min 02 s.
re-verify: grep -n "globs them itself" docs/gpu-experiment-protocol.md | head -1

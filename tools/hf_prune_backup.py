"""Remove from an HF dataset every file that is not in the local staging tree, in ONE commit (protocol R8 repair).

Written 2026-09-10, after an `hf upload <repo> .` ran from the repository root instead of the staging tree and pushed
repository files into the E9-long backup dataset.

usage: python tools/hf_prune_backup.py <repo_id> <staging_dir>                          # dry run; changes nothing
       python tools/hf_prune_backup.py <repo_id> <staging_dir> --apply --expect-ops N    # one delete commit

Run the dry run first and read its plan. `--apply` refuses unless `--expect-ops` equals the number of delete operations
it computes at apply time, and the commit names the revision the plan was computed from as its parent, so a dataset
that changed in between (another upload, another session) is never pruned blind. A folder that holds no local file is
deleted as one operation; files are deleted one by one only inside a folder that also holds staging files.
`.gitattributes` is never touched (the Hub writes it). The dataset must be private. Reads HF_TOKEN from the environment.

The deleted files stay in the dataset's git history, and count against storage, until that history is squashed.
Squashing is a separate, deliberate step and this tool does not do it.
"""
import argparse
import os
import sys
from collections import Counter
from pathlib import Path

from huggingface_hub import CommitOperationDelete, HfApi

KEEP = {".gitattributes"}


def local_files(root: Path) -> set[str]:
    out = set()
    for p in root.rglob("*"):
        rel = p.relative_to(root).as_posix()
        if p.is_file() and not rel.startswith(".cache/"):
            out.add(rel)
    return out


def plan(remote: set[str], local: set[str]) -> list[tuple[str, bool]]:
    """The minimal delete operations as (path, is_folder): each extraneous file is covered by its highest ancestor
    directory that contains no local file, or deleted on its own when every ancestor also holds staging files."""
    local_dirs = set()
    for f in local:
        parts = f.split("/")
        for i in range(1, len(parts)):
            local_dirs.add("/".join(parts[:i]))
    ops, folders = [], set()
    for f in sorted(remote - local - KEEP):
        parts = f.split("/")
        target = next(("/".join(parts[:i]) for i in range(1, len(parts)) if "/".join(parts[:i]) not in local_dirs), None)
        if target is None:
            ops.append((f, False))
        elif target not in folders:
            folders.add(target)
            ops.append((target, True))
    return ops


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("repo_id")
    ap.add_argument("staging_dir")
    ap.add_argument("--apply", action="store_true", help="create the delete commit (default: dry run)")
    ap.add_argument("--expect-ops", type=int, default=None, help="the operation count the dry run printed")
    a = ap.parse_args()
    if not os.environ.get("HF_TOKEN"):
        print("HF_TOKEN not set in the environment")
        return 2
    root = Path(a.staging_dir)
    if not root.is_dir():
        print(f"staging dir not found: {root}")
        return 2
    local = local_files(root)
    if not local:
        print(f"REFUSED: staging dir holds no files: {root}")
        return 2

    api = HfApi()
    info = api.dataset_info(a.repo_id)
    if not info.private:
        print(f"REFUSED: {a.repo_id} is not private")
        return 6
    remote = set(api.list_repo_files(a.repo_id, repo_type="dataset", revision=info.sha))
    extra = remote - local - KEEP
    ops = plan(remote, local)

    print(f"repo {a.repo_id} @ {info.sha[:8]} | remote {len(remote)} files | local {len(local)} files | "
          f"extraneous {len(extra)} | local files missing on the Hub {len(local - remote)}")
    print("extraneous files by top-level path:")
    for top, n in Counter(p.split("/")[0] if "/" in p else "(root file)" for p in extra).most_common():
        print(f"  {n:7d}  {top}")
    n_dirs = sum(1 for _, is_folder in ops if is_folder)
    print(f"delete operations: {len(ops)} ({n_dirs} folders, {len(ops) - n_dirs} files)")
    for path, is_folder in ops:
        print(f"  {'DIR ' if is_folder else 'FILE'} {path}{'/' if is_folder else ''}")

    if not a.apply:
        print(f"DRY RUN: nothing changed. To apply exactly this plan: --apply --expect-ops {len(ops)}")
        return 0
    if a.expect_ops is None or a.expect_ops != len(ops):
        print(f"REFUSED: --expect-ops {a.expect_ops} does not match the {len(ops)} operations computed now; "
              "rerun the dry run and read the plan again")
        return 3
    if not ops:
        print("nothing to delete")
        return 0
    commit = api.create_commit(
        a.repo_id, repo_type="dataset",
        operations=[CommitOperationDelete(path_in_repo=p + ("/" if f else ""), is_folder=f) for p, f in ops],
        commit_message=f"R8 repair: remove {len(extra)} files that are not in the staging tree",
        parent_commit=info.sha)
    print(f"PRUNED in commit {commit.oid[:8]} (parent {info.sha[:8]}). Next: tools/hf_backup.sh, which uploads anything "
          "missing and ends in the verifier.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

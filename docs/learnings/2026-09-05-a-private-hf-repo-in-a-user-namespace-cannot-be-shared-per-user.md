# A private Hugging Face repo in a user namespace has no per-user sharing; a collaborator gets a scoped read token or the repo moves to an organization

kills: (nothing)
ts: 2026-09-05T02:23:03Z
commit: 31a5f692e85298eb32a8f39fe2a71e1ce5ef2542
session: algoverse-gpu-run-session (8a0fb97e-0020-43aa-a9b2-9ae67eec2fe3)
status: verified
fact: The E9 backup dataset hossainpazooki/linear-ceiling-e9-2026-09-04 is private in a user
namespace. The Hub exposes no collaborators endpoint for it (404 with the owner's token, while the
repo itself answers 200 private=true), the docs say only the owner can access a private user-owned
repo, and the forum answer to exactly this question is to transfer the repo to an organization and
use resource groups. The fine-grained write token used for the backup carries only
repo.access.read / repo.content.read / repo.write on that repo and cannot transfer it or manage an
org. The practical route for one co-author is a fresh fine-grained token with read-only content
permission on that one repo, expiring, named for holder and expiry, passed as an environment
variable and never as a --token flag; the durable route is the org transfer.
basis: `GET /api/datasets/hossainpazooki/linear-ceiling-e9-2026-09-04/collaborators` -> 404 "Sorry, we
  can't find the page you are looking for."; `GET /api/datasets/hossainpazooki/linear-ceiling-e9-2026-09-04`
  -> 200 private=True (captured 2026-09-05T02:23:03Z with the owner's token); whoami-v2 token scopes
  `[('hossainpazooki/linear-ceiling-e9-2026-09-04', ['repo.access.read', 'repo.content.read', 'repo.write'])]`;
  https://discuss.huggingface.co/t/share-my-private-dataset-with-another-user/39291 ;
  https://huggingface.co/docs/hub/security-resource-groups
re-verify: curl -s -o /dev/null -w "%{http_code}\n" -H "Authorization: Bearer $HF_TOKEN" https://huggingface.co/api/datasets/hossainpazooki/linear-ceiling-e9-2026-09-04/collaborators

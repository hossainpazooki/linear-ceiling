"""RunPod box driver with hard cost guardrails — the `tools/ec2/box.sh` roles on a container host.

  balance | price | up | wait-ssh | arm-deadman | status | ssh | put | pull | terminate | spend | watchdog

WHAT CONTAINERS CHANGE. `tools/ec2/` drives a VM; a RunPod pod is a container on someone else's host,
reached over SSH/TCP. Four box-discipline rules change, and each is a way to lose money or evidence:

  1. `sudo shutdown -h` DOES NOT STOP BILLING. tools/ec2/setup.sh arms `sudo shutdown -h +1440` as its
     24 h safety net (EC2 shutdown behaviour = stop). In a container that either fails or kills PID 1
     and the POD KEEPS BILLING. Every self-destruct here goes through RunPod instead.
  2. STOP IS NOT TERMINATE. A stopped pod keeps billing for its disk. There is deliberately no `stop`.
  3. CONTAINER DISK IS EPHEMERAL, which makes R5 (pull -> verify -> delete) load-bearing rather than
     tidy: an unpulled dump is GONE, not paused. It is also why the dead man is a pure TTL backstop
     (below) and never fires on job completion.
  4. NO INSTANCE METADATA. §12's "instance id, region, IP" become pod id, machine id and the mapped
     SSH host/port, read back from the API by `status` (R7 step 6's read-back discipline).

WHO ENDS THE SITTING, AND WHY IT IS THE HOME SIDE. The on-pod dead man is a PURE TTL BACKSTOP. It
never watches for job completion, because "job finished -> terminate" races the pull: the results
live on ephemeral disk, so a pod that helpfully removes itself the moment the fit ends destroys the
only copy of the artifacts the sitting exists to produce. The normal path is: job finishes -> home
pulls -> home VERIFIES sha256 -> home terminates. The dead man only catches the case where home
never came back, and the home watchdog catches the case where the dead man did not arm.

COST GUARDRAILS (refusals, not advice):
  * Spend is `max(balance_delta, elapsed x rate)`; the PESSIMISTIC figure drives every guardrail. A
    lagging `clientBalance` otherwise reads as $0.00 on a pod that has burned for an hour.
  * The cap is CAMPAIGN-WIDE, not per-pod: `campaign_start_balance` is written once, on the first
    ever `up`, and never overwritten, so a second sitting cannot re-baseline its way past the budget.
  * `watchdog` enforces the account ceiling AND this sitting's (--sitting-max, --ttl); tighter wins.
  * `terminate` without --pod only ever touches pods named `linear-ceiling-*`.
  * Nothing here creates a network volume.

THE KEY. From ~/.config/linear-ceiling/runpod_api_key (0600) or $RUNPOD_API_KEY: never printed, never
written to the state file, never passed on a command line, NEVER uploaded to the pod. RunPod account
keys are account-scoped, so a key on rented hardware could terminate anything on the account. The
dead man therefore uses `runpodctl`, which RunPod preinstalls and which authenticates with the pod's
OWN credentials; if that is unavailable it REFUSES TO ARM and says so loudly rather than pretending.
(A PUBLIC key is not a secret and is passed in the create env — that is how these images authorize SSH.)
"""
import argparse
import http.client
import json
import os
import secrets
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.runpod.io/graphql"
# The argument is PodTerminateInput! (non-null). Declaring the variable nullable is a VALIDATION
# error, so the server answers HTTP 400 before executing and the pod keeps billing -- the one place
# in this file where a typo costs money rather than raising. Proven 2026-09-18 against a nonexistent
# podId: nullable -> 400 GRAPHQL_VALIDATION_FAILED, non-null -> 200 POD_NOT_FOUND. Do not "simplify".
TERMINATE_MUTATION = "mutation($in:PodTerminateInput!){podTerminate(input:$in)}"
KEY_FILE = Path.home() / ".config" / "linear-ceiling" / "runpod_api_key"
STATE = Path.home() / ".config" / "linear-ceiling" / "runpod_state.json"
KNOWN_HOSTS = Path.home() / ".config" / "linear-ceiling" / "runpod_known_hosts"
NAME_PREFIX = "linear-ceiling-"
SSH_KEY = Path.home() / ".ssh" / "id_rsa"

# A first-connect host-key prompt would hang a non-interactive flow while the meter runs, and an
# agentless key means -i must be explicit. Campaign-local known_hosts keeps churn out of ~/.ssh.
SSH_OPTS = ["-o", "StrictHostKeyChecking=accept-new", "-o", f"UserKnownHostsFile={KNOWN_HOSTS}",
            "-o", "ConnectTimeout=15", "-o", "ServerAliveInterval=30", "-o", "ServerAliveCountMax=4",
            "-o", "BatchMode=yes", "-i", str(SSH_KEY)]


def key() -> str:
    k = os.environ.get("RUNPOD_API_KEY") or (KEY_FILE.read_text().strip() if KEY_FILE.exists() else "")
    if not k:
        raise SystemExit(f"rp REFUSED: no API key ($RUNPOD_API_KEY or {KEY_FILE})")
    return k


def gql(query: str, variables: dict | None = None, *, timeout: int = 60) -> dict:
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    # A User-Agent is not optional: RunPod's edge answers urllib's default with a bare 403, which
    # reads exactly like a bad key.
    req = urllib.request.Request(API, data=body, method="POST", headers={
        "Authorization": f"Bearer {key()}", "Content-Type": "application/json",
        "User-Agent": "linear-ceiling-rp/1 (+tools/runpod/rp.py)"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            out = json.loads(r.read())
    except urllib.error.HTTPError as e:
        # The BODY carries the actual GraphQL message; without it a 400 reads only "Bad Request",
        # which is how a validation error in the terminate mutation hid until 2026-09-18.
        try:
            detail = e.read().decode("utf-8", "replace")[:500]
        except Exception:
            detail = "(no body)"
        raise SystemExit(f"rp REFUSED: RunPod API HTTP {e.code} ({e.reason}): {detail}") from e
    except urllib.error.URLError as e:
        raise SystemExit(f"rp REFUSED: RunPod API unreachable ({e.reason})") from e
    except (OSError, http.client.HTTPException, ValueError) as e:
        # TimeoutError, RemoteDisconnected and JSONDecodeError all land here. They used to escape
        # gql entirely and kill the watchdog, which is precisely when a pod is left unwatched.
        raise SystemExit(f"rp REFUSED: RunPod API call failed ({type(e).__name__}: {e})") from e
    if out.get("errors"):
        raise SystemExit(f"rp REFUSED: RunPod API error: {out['errors'][0].get('message')}")
    return out["data"]


def balance() -> float:
    return float(gql("query{myself{clientBalance}}")["myself"]["clientBalance"])


def pods() -> list:
    return gql("query{myself{pods{id name desiredStatus costPerHr machineId "
               "runtime{uptimeInSeconds ports{ip isIpPublic privatePort publicPort}}}}}")["myself"]["pods"]


def load_state() -> dict:
    return json.loads(STATE.read_text()) if STATE.exists() else {}


def save_state(s: dict) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(s, indent=2, sort_keys=True) + "\n")
    STATE.chmod(0o600)


def spend_now(state: dict) -> tuple[float, float, float]:
    """(sitting_spend, campaign_spend, balance). Both floored by elapsed x rate.

    The balance delta is the honest measure; the elapsed floor covers a lagging `clientBalance`. The
    guardrails trigger on whichever says MORE money is gone: over-reporting can only end a sitting
    early, under-reporting is how a $10 cap becomes a $10 bill. Once a sitting is terminated the
    elapsed floor is FROZEN at the recorded figure, or `spend` would keep climbing forever."""
    b = balance()
    if state.get("terminated_spend") is not None and not state.get("pod_id"):
        sit = float(state["terminated_spend"])
    else:
        delta = float(state.get("balance_at_start", b)) - b
        rate = max(float(state.get("price") or 0.0), float(state.get("cost_per_hr_actual") or 0.0))
        elapsed = 0.0
        if state.get("created_epoch") and rate:
            elapsed = max(0.0, (time.time() - float(state["created_epoch"])) / 3600.0) * rate
        sit = max(delta, elapsed)
    camp_start = float(state.get("campaign_start_balance", state.get("balance_at_start", b)))
    camp = max(camp_start - b, sit)
    return (round(sit, 4), round(camp, 4), b)


# ---------------------------------------------------------------- read-only

def cmd_balance(a) -> int:
    print(f"clientBalance ${balance():.4f}")
    return 0


def cmd_price(a) -> int:
    """Query each cloud SEPARATELY and label the rows.

    `lowestPrice` without a `secureCloud` argument mixes the COMMUNITY list price with SECURE stock
    attributes, which on 2026-09-18 produced a "$0.33 community RTX A6000, 50 GB RAM, 9 vCPU" that
    does not exist to rent: asked properly, community's cheapest >=48 GB card was the L40S at $0.79.
    A create against the phantom returns "no capacity" -- unbilled, but it is not a plan."""
    q = ("query($sec:Boolean,$mem:Int,$vcpu:Int){gpuTypes{id displayName memoryInGb "
         "lowestPrice(input:{gpuCount:1,secureCloud:$sec,minMemoryInGb:$mem,minVcpuCount:$vcpu}){"
         "uninterruptablePrice stockStatus}}}")
    print(f"(GPU >= {a.min_gb} GB, host RAM >= {a.min_ram} GB, vCPU >= {a.min_vcpu}; each cloud asked separately)")
    print(f"{'cloud':<11}{'gpu id':<30}{'name':<20}{'GB':>4}{'$/h':>7}  stock")
    best = []
    for label, sec in (("community", False), ("secure", True)):
        d = gql(q, {"sec": sec, "mem": a.min_ram, "vcpu": a.min_vcpu})
        rows = [g for g in d["gpuTypes"] if g["memoryInGb"] and g["memoryInGb"] >= a.min_gb
                and (g["lowestPrice"] or {}).get("uninterruptablePrice")]
        rows.sort(key=lambda g: g["lowestPrice"]["uninterruptablePrice"])
        for g in rows[: a.limit]:
            pr = g["lowestPrice"]
            print(f"{label:<11}{g['id'][:29]:<30}{g['displayName'][:19]:<20}{g['memoryInGb']:>4}"
                  f"{pr['uninterruptablePrice']:>7}  {pr['stockStatus']}")
        if rows:
            best.append((rows[0]["lowestPrice"]["uninterruptablePrice"], label, rows[0]["id"]))
    if best:
        pr, label, gid = min(best)
        print(f"\ncheapest adequate: {gid} on {label} at ${pr}/h  "
              f"-> --gpu {gid!r} --cloud {label.upper()} --price {pr}")
    return 0


def cmd_status(a) -> int:
    st = load_state()
    ps = pods()
    sit, camp, bal = spend_now(st)
    print(f"balance ${bal:.4f}   sitting ${sit:.4f}   campaign ${camp:.4f}   pods {len(ps)}")
    for p in ps:
        rt = p.get("runtime") or {}
        print(f"  {p['id']}  {p['name']}  {p['desiredStatus']}  ${p['costPerHr']}/h  "
              f"machine {p.get('machineId')}  up {(rt.get('uptimeInSeconds') or 0) // 60} min")
        ip, port = _ports(p)
        if ip:
            print(f"    ssh: ssh {' '.join(SSH_OPTS)} -p {port} root@{ip}")
    if not ps:
        print("  (none — nothing is billing)")
    return 0


def cmd_spend(a) -> int:
    sit, camp, bal = spend_now(load_state())
    print(f"sitting ${sit:.4f}   campaign ${camp:.4f}   balance ${bal:.4f}")
    return 0


# ---------------------------------------------------------------- lifecycle

DEAD_MAN = r"""#!/usr/bin/env bash
# On-pod dead man: a PURE TTL BACKSTOP. It does NOT watch for job completion -- container disk is
# ephemeral, so terminating when the job ends would race the home side's pull and destroy the only
# copy of the artifacts. Normal shutdown is: home pulls -> home verifies sha256 -> home terminates.
# This exists only for the case where home never came back.
#
# `shutdown`/`halt` do not stop billing in a container. Termination goes through RunPod using the
# POD-SCOPED credentials RunPod preinstalls -- never an account key.
#
# THE ENV TRAP: RunPod exports RUNPOD_POD_ID / RUNPOD_API_KEY into the container, but root's .bashrc
# sources /etc/rp_environment only for INTERACTIVE shells. A non-interactive `ssh pod 'script'` sees
# neither, so a dead man that just read $RUNPOD_POD_ID would refuse to arm on every correct pod.
# Source it explicitly, and fall back to PID 1's environment.
set -u
TTL_MIN="${TTL_MIN:-210}"
[ -f /etc/rp_environment ] && . /etc/rp_environment || true
if [ -z "${RUNPOD_POD_ID:-}" ] && [ -r /proc/1/environ ]; then
  RUNPOD_POD_ID="$(tr '\0' '\n' < /proc/1/environ | sed -n 's/^RUNPOD_POD_ID=//p' | head -1)"
fi
POD="${RUNPOD_POD_ID:-}"

# `remove pod` is the deprecated spelling; `pod delete` is current. Try current first, then legacy.
rp_delete() { runpodctl pod delete "$POD" 2>/dev/null || runpodctl remove pod "$POD"; }

if ! command -v runpodctl >/dev/null 2>&1 || [ -z "$POD" ]; then
  echo "dead-man: REFUSING to arm -- runpodctl absent or RUNPOD_POD_ID unresolvable." >&2
  echo "dead-man: the home watchdog is the ONLY net for this sitting." >&2
  exit 1
fi
# Prove the credentials actually work BEFORE claiming to be armed: an unauthenticated runpodctl
# would otherwise only reveal itself at TTL, which is the one moment it must not.
if ! runpodctl get pod "$POD" >/dev/null 2>&1; then
  echo "dead-man: REFUSING to arm -- 'runpodctl get pod $POD' failed, so the pod-scoped credentials" >&2
  echo "dead-man: do not work here. The home watchdog is the ONLY net." >&2
  exit 1
fi
echo "dead-man: armed via runpodctl, TTL ${TTL_MIN}m, pod ${POD}"
sleep $((TTL_MIN * 60))
echo "dead-man: TTL ${TTL_MIN}m reached, terminating $POD"
for i in 1 2 3 4 5; do
  rp_delete && { echo "dead-man: terminated"; exit 0; }
  echo "dead-man: attempt $i failed, retrying in 30s" >&2; sleep 30
done
echo "dead-man: COULD NOT TERMINATE after 5 attempts -- pod is still billing" >&2
exit 1
"""


def _ports(p: dict) -> tuple[str | None, str | None]:
    for prt in ((p.get("runtime") or {}).get("ports") or []):
        if prt.get("privatePort") == 22 and prt.get("isIpPublic"):
            return prt["ip"], str(prt["publicPort"])
    return None, None


def cmd_up(a) -> int:
    pub = Path(a.pubkey).expanduser()
    if not pub.exists():
        raise SystemExit(f"rp REFUSED: {pub} not found. RunPod images authorize SSH from the PUBLIC_KEY "
                         "env var and this account has no pubKey set, so without it the pod boots, "
                         "bills, and nobody can log in.")
    pubkey = pub.read_text().strip()
    st = load_state()
    verify = Path(a.verify_file).expanduser().resolve() if a.verify_file else None
    if verify is not None and verify.exists():
        raise SystemExit(f"rp REFUSED: verification interlock {verify} already exists. Remove the stale "
                         "receipt before creating a new pod; a receipt from an older sitting must never "
                         "authorize termination of a new one.")
    bal = balance()
    camp_start = float(st.get("campaign_start_balance", bal))
    camp_spent = round(camp_start - bal, 4)
    projected = a.price * a.hours
    print(f"== plan\n  gpu            {a.gpu}\n  price          ${a.price}/h\n  hours          {a.hours}\n"
          f"  container GB   {a.disk}\n  host RAM >=    {a.min_ram} GB, vCPU >= {a.min_vcpu}\n"
          f"  projected      ${projected:.2f}\n  campaign spent ${camp_spent:.2f}\n"
          f"  campaign total ${camp_spent + projected:.2f}  vs cap ${a.cap:.2f}\n"
          f"  pubkey         {pub}")
    # The cap is CAMPAIGN-wide. Checking only this pod's projection lets sitting B re-baseline past
    # the budget that sitting A already spent a third of.
    if a.price > a.max_price:
        raise SystemExit(f"rp REFUSED: ${a.price}/h exceeds --max-price ${a.max_price}/h. Re-run "
                         "`rp.py price` -- ask each cloud separately -- and pick the cheapest adequate card.")
    if camp_spent + projected > a.cap:
        raise SystemExit(f"rp REFUSED: campaign ${camp_spent:.2f} + projected ${projected:.2f} "
                         f"exceeds cap ${a.cap:.2f}")
    if bal < projected:
        raise SystemExit(f"rp REFUSED: balance ${bal:.4f} below projected ${projected:.2f}")
    if st.get("pod_id"):
        raise SystemExit(f"rp REFUSED: state names pod {st['pod_id']}; terminate it first")
    live = [p for p in pods() if p["name"].startswith(NAME_PREFIX)]
    if live:
        raise SystemExit(f"rp REFUSED: the API already lists {live[0]['name']} ({live[0]['id']}). "
                         "A pod exists that this state file does not know about — adopt or terminate it first.")
    if a.dry_run:
        print("\n-- DRY RUN: nothing created, nothing billed. The mutation that WOULD run:")
        print(json.dumps(_create_input(a, "<PUBLIC_KEY from " + str(pub) + ">"), indent=2))
        return 0
    if not a.yes:
        raise SystemExit("rp REFUSED: creating a pod bills real money; pass --yes to confirm")

    # Write the record BEFORE the mutation. If the create succeeds server-side but the response is
    # lost, a pod bills with no local record: the watchdog has no created_epoch (TTL never fires) and
    # balance_at_start defaults to the current balance (spend reads ~0). This makes that unrecoverable
    # case recoverable.
    pending = {"pod_id": None, "pending": True, "balance_at_start": bal,
               "campaign_start_balance": camp_start, "created_epoch": time.time(), "price": a.price,
               "cap": a.cap, "gpu": a.gpu, "name": a.name, "cloud": a.cloud,
               "hours": a.hours, "projected": round(projected, 4),
               # The watchdog's ceiling must follow the card actually rented: a fixed $2.00 would kill
               # a correct L40S sitting at 2.53 h. sitting_max = price x TTL, warn at 60% of it.
               "sitting_max": round(projected, 4), "warn": round(0.6 * projected, 4),
               "verify_file": str(verify) if verify is not None else None,
               # New sittings bind the home verification receipt to a fresh nonce as well as the pod id.
               # Older state (notably the already-live 2026-09-18 Sitting A) has no nonce and retains the
               # existence-only compatibility path in cmd_terminate; never retrofit a nonce mid-sitting.
               "verify_nonce": secrets.token_hex(16) if a.verify_file else None,
               "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    save_state(pending)
    try:
        d = gql("""mutation($in:PodFindAndDeployOnDemandInput){podFindAndDeployOnDemand(input:$in){
                     id imageName machineId costPerHr}}""", {"in": _create_input(a, pubkey)})
        pod = d["podFindAndDeployOnDemand"]
    except SystemExit:
        adopted = [p for p in pods() if p["name"].startswith(NAME_PREFIX)]
        if adopted:
            save_state(pending | {"pod_id": adopted[0]["id"], "pending": False,
                                  "cost_per_hr_actual": adopted[0]["costPerHr"]})
            print(f"\nrp: the create call failed BUT pod {adopted[0]['id']} exists and was adopted "
                  f"into state. IT IS BILLING. Run `rp.py status`, then terminate or continue.")
            return 1
        save_state({"campaign_start_balance": camp_start})
        raise
    if not pod:
        save_state({"campaign_start_balance": camp_start})
        raise SystemExit("rp REFUSED: RunPod returned no pod (no capacity at that filter). Nothing billed.")
    actual = float(pod["costPerHr"])
    save_state(pending | {"pod_id": pod["id"], "pending": False, "cost_per_hr_actual": actual})
    if actual > a.max_price:
        # Stock and prices can move between the read-only quote and the mutation. The pre-create
        # check only constrains the operator's quoted value; this check constrains the bill RunPod
        # actually returned. Never leave a too-expensive pod running for a human to notice.
        _terminate_until_gone(f"actual price ${actual}/h exceeds --max-price ${a.max_price}/h")
        raise SystemExit(f"rp REFUSED: RunPod returned ${actual}/h; pod was terminated because it "
                         f"exceeds --max-price ${a.max_price}/h")
    print(f"\npod {pod['id']} created at ${actual}/h; start balance ${bal:.4f}")
    print("NEXT, in order: rp.py wait-ssh   ->   rp.py arm-deadman   ->   caffeinate -i rp.py watchdog ... &")
    return 0


def _create_input(a, pubkey: str) -> dict:
    inp = {"cloudType": a.cloud, "gpuCount": 1, "gpuTypeId": a.gpu, "name": a.name,
           "imageName": a.image, "containerDiskInGb": a.disk, "volumeInGb": 0,
           "minMemoryInGb": a.min_ram, "minVcpuCount": a.min_vcpu,
           "ports": "22/tcp", "startSsh": True, "supportPublicIp": True,
           # setup.sh builds torch 2.11.0+cu128, so a host on an older driver wastes the whole
           # bring-up. Both key names are sent: images differ in which they read.
           "allowedCudaVersions": a.cuda,
           "env": [{"key": "PUBLIC_KEY", "value": pubkey},
                   {"key": "SSH_PUBLIC_KEY", "value": pubkey}]}
    if a.terminate_after:
        # A free THIRD layer behind the home watchdog and the on-pod dead man. Never counted on --
        # there are reports of it not firing -- but it costs nothing to ask for.
        inp["terminateAfter"] = a.terminate_after
    return inp


def cmd_wait_ssh(a) -> int:
    """Poll until SSH answers; TERMINATE if it never does. A pod nobody can log into is pure burn."""
    KNOWN_HOSTS.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.time() + a.timeout * 60
    while time.time() < deadline:
        ps = [p for p in pods() if p["name"].startswith(NAME_PREFIX)]
        if not ps:
            print("wait-ssh: no pod; nothing to wait for")
            return 1
        ip, port = _ports(ps[0])
        if ip:
            r = subprocess.run(["ssh", *SSH_OPTS, "-p", port, f"root@{ip}", "true"],
                               capture_output=True, timeout=40)
            if r.returncode == 0:
                print(f"wait-ssh: OK — root@{ip} -p {port}")
                return 0
            print(f"  not yet ({(r.stderr or b'').decode().strip()[:80]})", flush=True)
        else:
            print("  waiting for a public SSH port", flush=True)
        time.sleep(a.every)
    print(f"wait-ssh: SSH never came up within {a.timeout} min — TERMINATING rather than burning")
    return cmd_terminate(argparse.Namespace(pod=None, force=True))


def cmd_arm_deadman(a) -> int:
    ip, port = _ssh_target()
    local = Path("/tmp/lc_deadman.sh")
    local.write_text(DEAD_MAN)
    if subprocess.call(["scp", *SSH_OPTS, "-P", port, str(local), f"root@{ip}:/workspace/deadman.sh"]):
        raise SystemExit("rp REFUSED: could not upload the dead man")
    subprocess.call(["ssh", *SSH_OPTS, "-p", port, f"root@{ip}",
                     f"chmod +x /workspace/deadman.sh && TTL_MIN={a.ttl_min} setsid nohup "
                     "/workspace/deadman.sh > /workspace/deadman.log 2>&1 < /dev/null & sleep 3"])
    out = subprocess.run(["ssh", *SSH_OPTS, "-p", port, f"root@{ip}", "cat /workspace/deadman.log"],
                         capture_output=True, text=True).stdout
    print(out.strip() or "(no output)")
    if "armed via runpodctl" in out:
        print(f"arm-deadman: ARMED (TTL {a.ttl_min} min, pure backstop; home still pulls then terminates)")
        return 0
    print("arm-deadman: NOT ARMED — runpodctl/pod-scoped credentials unavailable on this pod.\n"
          "             The home watchdog is now the ONLY net. Keep it running under caffeinate.")
    return 2


VERIFY_RECEIPT_SCHEMA = "linear-ceiling.runpod.verify.v1"


def _check_verify_interlock(st: dict, verify: Path, target_pod: str | None) -> tuple[bool, str]:
    """Validate the home receipt that makes destruction of ephemeral disk safe.

    State written before verify_nonce was introduced is deliberately supported by existence only. That
    compatibility is needed for a pod that was already billing when the stronger receipt shipped; every
    newly-created pod gets a nonce and therefore takes the fail-closed JSON path below.
    """
    if not verify.exists():
        return False, "does not exist"
    nonce = st.get("verify_nonce")
    if not nonce:
        # Narrow compatibility for the pod that was already live when receipt nonces shipped. A
        # missing/corrupt nonce in any later sitting is a refusal, never a silent downgrade.
        if st.get("name") == f"{NAME_PREFIX}sitting-a":
            return True, "legacy Sitting-A existence-only interlock"
        return False, "has no verification nonce in state (not an eligible legacy Sitting A)"
    try:
        receipt = json.loads(verify.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return False, f"is not a readable JSON receipt ({type(e).__name__})"
    if receipt.get("schema") != VERIFY_RECEIPT_SCHEMA:
        return False, f"has schema {receipt.get('schema')!r}, expected {VERIFY_RECEIPT_SCHEMA!r}"
    expected = {
        "verify_nonce": nonce,
        "pod_id": st.get("pod_id"),
        "created_utc": st.get("created_utc"),
    }
    for key_name, want in expected.items():
        if not want or receipt.get(key_name) != want:
            return False, f"does not match this sitting's {key_name}"
    if target_pod is not None and receipt.get("pod_id") != target_pod:
        return False, "belongs to another pod"
    if not receipt.get("report_sha256") or not receipt.get("verified_utc"):
        return False, "does not record a verified report hash and verification time"
    return True, "nonce- and pod-bound receipt"


def cmd_terminate(a) -> int:
    st = load_state()
    # The sitting's product (the mapper and the dumps) lives on EPHEMERAL disk: terminate destroys
    # whatever was not pulled, and re-creating it costs another card. So a plain `terminate` refuses
    # until the home side has written its verification file. --force is for the guardrails, which
    # must always be able to stop the meter.
    verify = Path(str(st.get("verify_file") or "")) if st.get("verify_file") else None
    pid = a.pod or st.get("pod_id")
    if not a.force and verify is not None:
        ok, why = _check_verify_interlock(st, verify, pid)
        if not ok:
            raise SystemExit(f"rp REFUSED: verification interlock {verify} {why}, so the pull has not "
                             "been verified for THIS sitting and terminating would destroy its only "
                             "artifacts. Verify first, or pass --force if you accept losing them.")
    live = pods()
    if pid:
        targets = [pid]
    else:
        # NEVER "every pod on the account". Without an explicit --pod this only touches our own.
        targets = [p["id"] for p in live if p["name"].startswith(NAME_PREFIX)]
        if not targets:
            print(f"no {NAME_PREFIX}* pod is running; nothing to terminate")
            return 0
    for t in targets:
        gql(TERMINATE_MUTATION, {"in": {"podId": t}})
        print(f"terminate sent: {t}")
    for _ in range(12):                              # R7 step 6: prove it, never assume it
        time.sleep(5)
        still = [p["id"] for p in pods()]
        if not any(t in still for t in targets):
            sit, camp, bal = spend_now(st)
            save_state({k: v for k, v in st.items() if k not in ("pod_id", "created_epoch")}
                       | {"terminated_spend": sit, "pod_id": None})
            print(f"PROVEN GONE. sitting ${sit:.4f}, campaign ${camp:.4f}, balance ${bal:.4f}")
            return 0
    raise SystemExit("rp REFUSED to claim success: pod still listed after 60 s — CHECK THE CONSOLE, "
                     "it is still billing")


def _terminate_until_gone(reason: str) -> int:
    """Keep trying until the API lists no linear-ceiling pod. NEVER return while one bills.

    The old code did `return cmd_terminate(...)`: one failed attempt exited the watchdog and left the
    pod running with nothing watching it. A kill path that gives up is not a kill path."""
    attempt = 0
    while True:
        attempt += 1
        print(f"watchdog: TERMINATING ({reason}) attempt {attempt}", flush=True)
        try:
            cmd_terminate(argparse.Namespace(pod=None, force=True))
        except (Exception, SystemExit) as e:   # SystemExit is a BaseException: `except Exception`
            # does NOT catch it, and gql() raises SystemExit for every API failure. This retry loop
            # is the one path that must never give up, so it catches both. (2026-09-18: the watchdog
            # died here-adjacent on [SSL: UNEXPECTED_EOF_WHILE_READING] and the pod ran unwatched.)
            print(f"  terminate attempt {attempt} failed: {e}", flush=True)
        try:
            if not [x for x in pods() if x["name"].startswith(NAME_PREFIX)]:
                print("watchdog: pod is gone. \a", flush=True)
                return 0
        except (Exception, SystemExit) as e:
            print(f"  could not confirm ({e}); retrying", flush=True)
        print("  \a STILL BILLING — retrying in 30s. CHECK THE CONSOLE.", flush=True)
        time.sleep(30)


def cmd_watchdog(a) -> int:
    """Home-side net, independent of the pod.

    Re-execs itself under `caffeinate -dimsu` so a sleeping Mac cannot silently remove the only net.
    Ceilings are MANDATORY: a watchdog with no sitting ceiling only fires at the account limit, by
    which point a hung sitting has eaten the whole campaign."""
    if os.environ.get("RP_CAFFEINATED") != "1" and shutil.which("caffeinate"):
        os.environ["RP_CAFFEINATED"] = "1"
        argv = ["caffeinate", "-dimsu", sys.executable, *sys.argv]
        print(f"watchdog: re-exec under caffeinate ({' '.join(argv[:3])} ...)", flush=True)
        os.execvp("caffeinate", argv)
    st = load_state()
    if not st or not st.get("created_epoch"):
        raise SystemExit("rp REFUSED: no pod state to watch. An empty state file is an error here, not "
                         "a quiet no-op: it is indistinguishable from 'the watchdog is running'.")
    sitting_max = a.sitting_max if a.sitting_max is not None else st.get("sitting_max", st.get("projected"))
    ttl = a.ttl if a.ttl is not None else st.get("hours")
    if sitting_max is None or ttl is None:
        raise SystemExit("rp REFUSED: --sitting-max and --ttl are mandatory (and `up` normally stores "
                         "defaults for both). Without them the only ceiling is the account limit.")
    limit = min(a.kill, float(sitting_max))
    warn_at = a.warn if a.warn is not None else st.get("warn", 0.6 * float(sitting_max))
    print(f"watchdog: sitting kill ${limit:.2f}, account kill ${a.kill:.2f}, TTL {ttl}h, "
          f"warn ${warn_at:.2f}, poll {a.every}s. Ctrl-C stops the NET, not the pod.", flush=True)
    warned = False
    unreachable = 0
    empty_polls = 0
    while True:
        try:
            sit, camp, bal = spend_now(st)
            ps = [x for x in pods() if x["name"].startswith(NAME_PREFIX)]
            unreachable = 0
        except (Exception, SystemExit) as e:
            # BOTH, deliberately. gql() converts every network failure into SystemExit, and SystemExit
            # derives from BaseException -- so the original `except SystemExit` missed ordinary errors
            # and the B2 fix's `except Exception` missed the SystemExits, killing the watchdog on a
            # transient SSL EOF while a pod was billing. Neither alone is correct.
            unreachable += 1
            print(f"  watchdog: API unreachable ({e}); retry {unreachable}", flush=True)
            # A HOME network drop also stops the pull, so terminating on recovery destroys a healthy
            # run AND its unpulled evidence (measured: a simulated 15-minute outage force-terminated a
            # healthy pod at $1.69). Alert and KEEP POLLING; the first successful poll re-evaluates the
            # spend, TTL and drain rules, which are the right authorities. The terminate stays only as
            # a long backstop for a genuinely unreachable account.
            if unreachable * a.every >= a.unreachable_terminate_after * 60:
                print(f"\a  watchdog: API unreachable for {a.unreachable_terminate_after:.0f} min. "
                      f"NOT terminating -- a home outage is not a runaway pod. Still polling; the "
                      f"ceilings decide on the first successful poll.", flush=True)
                if unreachable * a.every >= a.unreachable_backstop_after * 60:
                    return _terminate_until_gone(
                        f"API unreachable for {a.unreachable_backstop_after:.0f} min (long backstop)")
            time.sleep(a.every)
            continue
        hours = (time.time() - float(st["created_epoch"])) / 3600.0
        print(f"  sitting ${sit:.4f} campaign ${camp:.4f} balance ${bal:.4f} pods {len(ps)} "
              f"up {hours:.2f}h", flush=True)
        if not ps:
            # TWO consecutive empty listings, never one. Exiting removes the only home-side spend
            # ceiling, and a single empty answer is not proof: the account listing is eventually
            # consistent and can omit a pod that is still billing (it can also answer with a partial
            # page during a control-plane blip). Requiring the next poll to agree costs one interval
            # and turns a transient omission into a retry instead of an unwatched pod.
            empty_polls += 1
            if empty_polls < 2:
                print(f"  watchdog: listing shows nothing billing ({empty_polls}/2); "
                      f"confirming before I stand down", flush=True)
                time.sleep(a.every)
                continue
            print("watchdog: nothing billing on two consecutive polls; exiting")
            return 0
        empty_polls = 0
        if sit >= limit or camp >= a.kill:
            return _terminate_until_gone(f"sitting ${sit:.4f} / campaign ${camp:.4f}")
        if hours >= float(ttl):
            return _terminate_until_gone(f"TTL {hours:.2f}h >= {ttl}h")
        if sit >= warn_at and not warned:
            print(f"watchdog: WARNING sitting ${sit:.4f} >= ${warn_at:.2f} \a")
            warned = True
        time.sleep(a.every)


# ---------------------------------------------------------------- transport

def _ssh_target() -> tuple[str, str]:
    for p in pods():
        if p["name"].startswith(NAME_PREFIX):
            ip, port = _ports(p)
            if ip:
                KNOWN_HOSTS.parent.mkdir(parents=True, exist_ok=True)
                return ip, port
    raise SystemExit("rp REFUSED: no public SSH port on a linear-ceiling pod (still starting?)")


def cmd_ssh(a) -> int:
    ip, port = _ssh_target()
    return subprocess.call(["ssh", *SSH_OPTS, "-p", port, f"root@{ip}", *a.rest])


def cmd_put(a) -> int:
    ip, port = _ssh_target()
    return subprocess.call(["scp", *SSH_OPTS, "-P", port, *a.paths, f"root@{ip}:{a.dest}"])


def cmd_pull(a) -> int:
    """rsync if the image has it, else tar-over-ssh — never assume a tool the image may not ship."""
    ip, port = _ssh_target()
    has_rsync = subprocess.run(["ssh", *SSH_OPTS, "-p", port, f"root@{ip}",
                                "command -v rsync"], capture_output=True).returncode == 0
    if has_rsync and not a.force_tar:
        return subprocess.call(["rsync", "-avP", "-e", f"ssh {' '.join(SSH_OPTS)} -p {port}",
                                f"root@{ip}:{a.remote}", a.local])
    print("pull: rsync unavailable on the pod; falling back to tar-over-ssh")
    Path(a.local).mkdir(parents=True, exist_ok=True)
    p1 = subprocess.Popen(["ssh", *SSH_OPTS, "-p", port, f"root@{ip}",
                           f"tar -czf - -C $(dirname {a.remote}) $(basename {a.remote})"],
                          stdout=subprocess.PIPE)
    return subprocess.call(["tar", "-xzf", "-", "-C", a.local], stdin=p1.stdout)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("balance").set_defaults(fn=cmd_balance)
    sub.add_parser("status").set_defaults(fn=cmd_status)
    sub.add_parser("spend").set_defaults(fn=cmd_spend)

    p = sub.add_parser("price")
    p.add_argument("--min-gb", type=int, default=40); p.add_argument("--min-ram", type=int, default=48)
    p.add_argument("--min-vcpu", type=int, default=8); p.add_argument("--limit", type=int, default=12)
    p.set_defaults(fn=cmd_price)

    p = sub.add_parser("up", help="create a pod (bills money; --dry-run first, --yes required)")
    p.add_argument("--gpu", required=True); p.add_argument("--price", type=float, required=True)
    p.add_argument("--hours", type=float, required=True)
    # Real use is ~50 GB (22.5 GB bf16 weights + ~8 GB venvs + ~10 GB pull set + caches). 120 leaves
    # headroom without narrowing the host pool: minDisk is a filter, and stock is already "Low".
    # 250 GB for sitting B: the box WRITES up to ~12.4 GB of dumps per handoff at the cap, and the
    # 8-handoff keep subset it must hold until the puller takes it is 50.12 GiB -- recomputed
    # 2026-09-19 from the committed coverage.json rather than from the cap figure times 8. Peak is
    # ~95 GiB of 250 (weights 22.5 + venvs ~8 + repos/traces ~2 + working handoff <= 12.4 + 50.1),
    # against sitting A's ~50 GB. Sized from the measured budget, not guessed.
    p.add_argument("--disk", type=int, default=250, help="container disk GB (ephemeral; no volume)")
    # 48 GB, measured not guessed: kvt/models.load_model calls from_pretrained(dtype=float32) with NO
    # device_map and only then .to(device), so the whole fp32 model materialises in host RAM first --
    # 29.91 GiB for Llama-3.1-8B (32 x 4096 x ... verified from the gated config). 48 leaves ~18 GiB of
    # headroom; 32 would be marginal. It is also the highest floor that still admits the RTX A6000 at
    # $0.33/h (56 drops it to the $0.74 RTX 6000 Ada), so this number is worth $0.41/h -- do not raise
    # it casually, and do not lower it below 48 to chase stock.
    p.add_argument("--min-ram", type=int, default=48, help="pod RAM floor in GB; fp32 8B loads to host first (~30 GiB)")
    p.add_argument("--min-vcpu", type=int, default=8)
        # runpod/base 1.3.1: CUDA 12.8.1, and NO torch -- correct, because sitting_a.sh builds the pinned
    # stack (torch 2.11.0+cu128, transformers 5.15.1) that entry 0028's tolerance was measured on; a
    # pytorch image would ship an unused torch and cost GB. Verified in runpod/containers
    # official-templates/base/Dockerfile: apt installs openssh-server, rsync, tmux, jq, git, curl, wget,
    # and uv arrives via COPY --from=ghcr.io/astral-sh/uv. container-template/start.sh appends
    # $PUBLIC_KEY to authorized_keys and generates host keys -- and gates ALL ssh setup on PUBLIC_KEY
    # being set, which is exactly why an account with no pubKey yields an unreachable pod. It also
    # writes /etc/rp_environment from printenv, which is what the dead man sources.
    p.add_argument("--image", default="runpod/base:1.3.1-cuda1281-ubuntu2204")
    # Default is sitting-b now that A is done. This is not cosmetic: cmd_terminate's legacy
    # existence-only receipt path is reachable ONLY for a pod named exactly
    # "linear-ceiling-sitting-a", so B takes the fail-closed JSON-receipt path by default.
    p.add_argument("--name", default=f"{NAME_PREFIX}sitting-b")
    p.add_argument("--pubkey", default=str(Path.home() / ".ssh" / "id_rsa.pub"))
    p.add_argument("--cap", type=float, default=10.0, help="CAMPAIGN-wide cap, not per-pod")
    p.add_argument("--cloud", default="COMMUNITY", choices=["COMMUNITY", "SECURE"])
    p.add_argument("--max-price", type=float, default=0.85,
                   help="refuse a $/h above this; the cheap card is the whole point of the brief")
    p.add_argument("--cuda", nargs="*", default=["12.8", "12.9"],
                   help="allowedCudaVersions; setup.sh builds torch 2.11.0+cu128")
    # DO NOT set this for sitting B. It is a provider-side hard kill that cannot be extended without
    # editing the pod (which restarts the container and, at volumeInGb 0, wipes /workspace mid-run), and
    # a B that overruns its estimate would be destroyed rather than closed under the registered partial
    # rule. Sitting A could afford it; B cannot. Left available for short, bounded sittings only.
    p.add_argument("--terminate-after", default=None,
                   help="ISO DateTime for RunPod's terminateAfter. DO NOT USE for sitting B -- see the code comment")
    vg = p.add_mutually_exclusive_group(required=True)
    vg.add_argument("--verify-file",
                    help="path the home side writes after verifying the pull; `terminate` refuses without it")
    vg.add_argument("--unsafe-no-verify-interlock", action="store_true",
                    help="explicitly create ephemeral disk with no verified-pull termination interlock")
    p.add_argument("--dry-run", action="store_true"); p.add_argument("--yes", action="store_true")
    p.set_defaults(fn=cmd_up)

    p = sub.add_parser("wait-ssh"); p.add_argument("--timeout", type=float, default=12.0)
    p.add_argument("--every", type=int, default=15); p.set_defaults(fn=cmd_wait_ssh)
    p = sub.add_parser("arm-deadman"); p.add_argument("--ttl-min", type=int, default=210)
    p.set_defaults(fn=cmd_arm_deadman)
    p = sub.add_parser("terminate"); p.add_argument("--pod")
    p.add_argument("--force", action="store_true",
                   help="terminate even though the pull was not verified (guardrails always pass this)")
    p.set_defaults(fn=cmd_terminate)

    p = sub.add_parser("watchdog")
    p.add_argument("--warn", type=float, default=None, help="default: 60%% of the sitting ceiling `up` stored")
    p.add_argument("--kill", type=float, default=9.0)
    p.add_argument("--sitting-max", type=float, default=None); p.add_argument("--ttl", type=float, default=None)
    p.add_argument("--unreachable-terminate-after", type=float, default=10.0,
                   help="minutes of unreachability after which to ALERT (no longer terminates)")
    p.add_argument("--unreachable-backstop-after", type=float, default=45.0,
                   help="minutes after which to terminate anyway; a home outage must not trip this")
    p.add_argument("--every", type=int, default=60); p.set_defaults(fn=cmd_watchdog)

    p = sub.add_parser("ssh"); p.add_argument("rest", nargs="*"); p.set_defaults(fn=cmd_ssh)
    p = sub.add_parser("put"); p.add_argument("paths", nargs="+"); p.add_argument("--dest", default="/workspace/")
    p.set_defaults(fn=cmd_put)
    p = sub.add_parser("pull"); p.add_argument("remote"); p.add_argument("local")
    p.add_argument("--force-tar", action="store_true"); p.set_defaults(fn=cmd_pull)
    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    raise SystemExit(main())

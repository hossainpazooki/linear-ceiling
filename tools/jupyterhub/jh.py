"""Drive a JupyterHub-only GPU box (TLJH, no ssh/scp) over HTTP from the local machine.

Configuration, all from the environment (never from a file inside a checkout):
  JH_URL         hub base URL, e.g. http://192.0.2.10
  JH_USER        hub username
  JH_TOKEN       hub API token (mint one via POST /hub/api/users/<user>/tokens after a browser login)
  JH_STATE_DIR   where kernel_id.txt is kept (default: a temp dir); nothing secret is written there

usage:
  jh.py exec  "<shell command>" [timeout_s]    run on the box via a python3 kernel, print stdout+stderr+RC
  jh.py up    <local> <remote>                 upload one file (base64 through /api/contents; split files > 60 MB)
  jh.py down  <remote> <local>                 stream one file down via /user/<u>/files/ (no size cap)
  jh.py ls    <remote_dir>                     list a directory via /api/contents

Traps this encodes (see docs/gpu-experiment-protocol.md): keep each exec under ~40 s or the kernel
websocket drops and the next poll reads a stale log; the Authorization header, not ?token=, is what
the kernel channel accepts; /files/ does not serve dotfiles, copy them somewhere visible first.
"""
import base64
import json
import os
import sys
import tempfile
import time
import uuid
from pathlib import Path

import requests
import websocket

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

H = os.environ["JH_URL"].rstrip("/")
U = os.environ["JH_USER"]
T = os.environ["JH_TOKEN"]
BASE = f"{H}/user/{U}"
HDR = {"Authorization": f"token {T}"}
STATE = Path(os.environ.get("JH_STATE_DIR") or tempfile.gettempdir())
KID = STATE / "kernel_id.txt"


def kernel_id() -> str:
    if KID.exists():
        k = KID.read_text().strip()
        if requests.get(f"{BASE}/api/kernels/{k}", headers=HDR, timeout=20).status_code == 200:
            return k
    r = requests.post(f"{BASE}/api/kernels", headers=HDR, json={"name": "python3"}, timeout=60)
    r.raise_for_status()
    k = r.json()["id"]
    KID.write_text(k)
    time.sleep(2)
    return k


def exec_(cmd: str, timeout: int = 600) -> str:
    k = kernel_id()
    ws_url = BASE.replace("http://", "ws://").replace("https://", "wss://")
    ws = websocket.create_connection(f"{ws_url}/api/kernels/{k}/channels", timeout=30,
                                     header=[f"Authorization: token {T}"])
    code = ("import subprocess,sys\n"
            f"_r=subprocess.run({cmd!r}, shell=True, capture_output=True, text=True, executable='/bin/bash')\n"
            "sys.stdout.write(_r.stdout); sys.stdout.flush()\n"
            "sys.stderr.write(_r.stderr); sys.stderr.flush()\n"
            "print('\\nRC=', _r.returncode)")
    mid = uuid.uuid4().hex
    msg = {"header": {"msg_id": mid, "username": U, "session": uuid.uuid4().hex, "msg_type": "execute_request",
                      "version": "5.3", "date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
           "parent_header": {}, "metadata": {}, "channel": "shell",
           "content": {"code": code, "silent": False, "store_history": False, "user_expressions": {},
                       "allow_stdin": False, "stop_on_error": True}}
    ws.send(json.dumps(msg))
    out, t0 = [], time.time()
    ws.settimeout(timeout)
    while True:
        if time.time() - t0 > timeout:
            out.append(f"\n[jh] TIMEOUT after {timeout}s")
            break
        m = json.loads(ws.recv())
        if m.get("parent_header", {}).get("msg_id") != mid:
            continue
        t = m["header"]["msg_type"]
        if t == "stream":
            out.append(m["content"]["text"])
        elif t == "error":
            out.append("\n".join(m["content"]["traceback"]))
        elif t == "status" and m["content"]["execution_state"] == "idle" and m["channel"] == "iopub":
            break
    ws.close()
    s = "".join(out)
    sys.stdout.write(s)
    return s


def up(local: str, remote: str) -> None:
    data = Path(local).read_bytes()
    r = requests.put(f"{BASE}/api/contents/{remote}", headers=HDR, timeout=600,
                     json={"type": "file", "format": "base64", "content": base64.b64encode(data).decode()})
    print(r.status_code, r.json().get("path"), len(data), "bytes")


def down(remote: str, local: str) -> None:
    Path(local).parent.mkdir(parents=True, exist_ok=True)
    with requests.get(f"{BASE}/files/{remote}", headers=HDR, stream=True, timeout=600) as r:
        r.raise_for_status()
        n = 0
        with open(local, "wb") as f:
            for chunk in r.iter_content(1 << 22):
                f.write(chunk)
                n += len(chunk)
    print(local, n, "bytes")


def ls(remote: str) -> None:
    r = requests.get(f"{BASE}/api/contents/{remote}", headers=HDR, timeout=60)
    for c in r.json().get("content", []):
        print(c["type"][:1], c.get("size"), c["name"])


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        sys.exit(2)
    if a[0] == "exec":
        exec_(a[1], int(a[2]) if len(a) > 2 else 600)
    elif a[0] == "up":
        up(a[1], a[2])
    elif a[0] == "down":
        down(a[1], a[2])
    elif a[0] == "ls":
        ls(a[1])
    else:
        print(__doc__)
        sys.exit(2)

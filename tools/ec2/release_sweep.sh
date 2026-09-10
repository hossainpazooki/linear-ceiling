#!/bin/bash
# R7 steps 0, 2, 3 (listing side), 4 and 5 on the box, in order, stopping at the first failure. Deletes ONLY the HF
# model cache (step 4), and only after steps 0 and 2 passed. Termination (step 6) is `box.sh terminate` from home,
# after this script's output is in the runbook. Usage: bash ~/release_sweep.sh  (prints; exit 0 = swept, ready to terminate)
set -uo pipefail
EXP=e9l
OURS_FILES="k1.json k1.safetensors traces.tar.gz setup.sh run.sh probe_e9l.py release_sweep.sh setup.log setup.rc probe.log probe.rc ${EXP}.log ${EXP}.rc launches.log manifest_check.out release.log e9l.records.sha256 PYTHON_PACKAGES_LICENSES THIRD_PARTY_SOURCE_CODE_URLS"
echo "== step 0: $(date -u +%FT%TZ) who is here (single-tenant instance; anything not ours still aborts)"
ls -la ~
ps -u "$(whoami)" -o pid,etimes,cmd --no-headers | grep -v "sshd\|bash -c\|release_sweep\|ps -u\|grep" || true
# Single-tenant rule: anything whose mtime predates the instance launch is the image's baseline (licenses, nvidia dirs,
# the AMI's empty ~/.aws), listed for the record; anything newer must be ours (uploaded, cloned, or created by our
# tooling: .nv = CUDA's kernel cache, .zshrc = the uv installer's shell hook, .local = uv itself).
LAUNCH_UTC=${LAUNCH_UTC:-"2026-09-09 23:40"}
echo "  image baseline (mtime before $LAUNCH_UTC):"; find ~ -maxdepth 1 -mindepth 1 ! -newermt "$LAUNCH_UTC" -printf "    %TY-%Tm-%Td %TH:%TM %f
" | sort
foreign=0
for f in $(find ~ -maxdepth 1 -mindepth 1 -newermt "$LAUNCH_UTC" -printf "%f
"); do
  case " $OURS_FILES " in *" $f "*) ;; *)
    case "$f" in .cache|.local|.config|.nv|.zshrc|.bash*|.profile|.ssh|.sudo_as_admin_successful|.lesshst|.python_history|.wget-hsts|kv-transfer-replication|linear-ceiling|${EXP}.*.halt.log|.venv*) ;; *) echo "  NOT OURS: $f"; foreign=1;; esac;; esac
done
if pgrep -f "[l]inear_ceiling.e9 " > /dev/null; then echo "ABORT: the driver is still running"; exit 10; fi
[ "$foreign" = 0 ] || { echo "ABORT: foreign presence; nothing deleted"; exit 11; }
echo "== step 2: no tensor directory may remain under results/$EXP/ on the box"
left=$(find ~/linear-ceiling/results/$EXP -name "layer*.npz" 2>/dev/null | wc -l)
echo "  layer*.npz files remaining: $left"; find ~/linear-ceiling/results/$EXP -maxdepth 2 -type d | sort
[ "$left" = 0 ] || { echo "ABORT: tensors remain; pull and verify them first"; exit 12; }
echo "== step 3: box-side hashes of every log the entry may cite (pull these home before terminate)"
cd ~ && sha256sum setup.log probe.log ${EXP}.log launches.log manifest_check.out setup.sh run.sh probe_e9l.py ${EXP}.*.halt.log 2>/dev/null
echo "== step 3b: box-side hashes of the small records, for the home diff by path"
cd ~/linear-ceiling/results/$EXP && find . -type f -not -path "./scratch/*" -not -path "./bridge/*/*" | sort | xargs sha256sum > ~/${EXP}.records.sha256 && wc -l ~/${EXP}.records.sha256
echo "== step 4: sensitive-data sweep"
hits=0
[ -f ~/.cache/huggingface/token ] && { echo "  HF token file present"; hits=1; }
# `grep -l … && hits=1` is FAIL-OPEN: a missing file (no ~/.bash_history) makes grep exit 2 even when it matched, and the
# hit is masked (caught 2026-09-10 01:21Z on this very script's own pattern literal). Count matches instead; exclude this script.
tok=$(grep -rls "hf_[A-Za-z0-9]\{20,\}\|HF_TOKEN=" ~/.bash_history ~/*.sh ~/*.py ~/*.log 2>/dev/null | grep -v "release_sweep.sh$" | awk 'END{print NR}')
[ "$tok" = 0 ] || { echo "  token-shaped strings in $tok file(s)"; grep -rls "hf_[A-Za-z0-9]\{20,\}\|HF_TOKEN=" ~/*.sh ~/*.py ~/*.log 2>/dev/null | grep -v "release_sweep.sh$"; hits=1; }
[ -f ~/.git-credentials ] && { echo "  .git-credentials present"; hits=1; }
[ -f ~/.netrc ] && { echo "  .netrc present"; hits=1; }
[ -f ~/.aws/credentials ] && { echo "  ~/.aws/credentials present"; hits=1; }
aws=$(grep -rls "aws_secret_access_key\|AKIA[0-9A-Z]\{16\}" ~/.aws 2>/dev/null | awk 'END{print NR}')
[ "$aws" = 0 ] || { echo "  AWS key material under ~/.aws in $aws file(s)"; hits=1; }
git -C ~/linear-ceiling remote -v | grep -v https && hits=1
git -C ~/kv-transfer-replication remote -v | grep -v https && hits=1
echo "  sweep hits: $hits"
[ "$hits" = 0 ] || { echo "ABORT: sensitive data found; fix by hand"; exit 13; }
du -sh ~/.cache/huggingface 2>/dev/null; rm -rf ~/.cache/huggingface; echo "  HF cache removed"
echo "== step 5: processes of ours"
ps -u "$(whoami)" -o pid,cmd --no-headers | grep -v "sshd\|bash -c\|release_sweep\|ps -u\|grep" || echo "  none"
echo "SWEEP_DONE $(date -u +%FT%TZ); terminate from home with box.sh terminate after the logs are pulled and hashed"

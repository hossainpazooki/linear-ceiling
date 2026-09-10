#!/usr/bin/env bash
# Home-side lifecycle of ONE rented EC2 GPU instance for a sitting (E9-long, 2026-09-10).
# Git Bash / MINGW64 or Linux. State lives in ~/.lc-e9l-box.json, outside every checkout.
#
#   tools/ec2/box.sh up          launch (retries the next subnet on InsufficientInstanceCapacity), wait for ssh, print BOX=
#   tools/ec2/box.sh status      instance state + public IP
#   tools/ec2/box.sh ssh [cmd]   ssh with the sitting's key
#   tools/ec2/box.sh put <local> <remote>     scp to the box
#   tools/ec2/box.sh stop        stop (compute billing ends; the root volume and everything on it stay)
#   tools/ec2/box.sh terminate   terminate and PROVE it: waits until describe-instances says terminated (R7 step 6)
#
# The AMI is pinned by id (Deep Learning Base OSS Nvidia Driver GPU AMI (Ubuntu 22.04) 20260907, resolved
# 2026-09-09 by describe-images); the key pair and the ssh-only security group were created 2026-09-09.
set -euo pipefail
PROFILE=${LC_AWS_PROFILE:-kv-platform-admin}
REGION=${LC_AWS_REGION:-us-east-1}
AMI=${LC_AMI:-ami-0eb7d782cce2fe526}
TYPE=${LC_TYPE:-g6e.4xlarge}
KEY=${LC_KEY:-lc-e9l-2026-09-10}
SG=${LC_SG:-sg-03021d0b6c09b4c75}
SUBNETS=${LC_SUBNETS:-subnet-b5ed629b,subnet-d051019a,subnet-dafb7686,subnet-c0cd4da7}   # us-east-1a,b,c,d
ROOT_GB=${LC_ROOT_GB:-250}
NAME=${LC_NAME:-lc-e9l-2026-09-10}
STATE=${LC_BOX_STATE:-$HOME/.lc-e9l-box.json}
KEYFILE=${LC_KEYFILE:-$HOME/.ssh/lc-e9l-2026-09-10}
SSH_OPTS=(-i "$KEYFILE" -o StrictHostKeyChecking=accept-new -o ServerAliveInterval=30 -o ConnectTimeout=10)

aws_() { command aws --profile "$PROFILE" --region "$REGION" "$@"; }
iid() { python -c "import json,sys;print(json.load(open(sys.argv[1]))['instance_id'])" "$STATE"; }
ip_of() { aws_ ec2 describe-instances --instance-ids "$1" --query 'Reservations[0].Instances[0].PublicIpAddress' --output text; }

case "${1:-}" in
up)
  if [ -f "$STATE" ]; then echo "refusing: $STATE exists (an instance may be running); status/terminate first"; exit 3; fi
  BDM='[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":'"$ROOT_GB"',"VolumeType":"gp3","DeleteOnTermination":true}}]'
  ID=""
  for SN in ${SUBNETS//,/ }; do
    echo "== run-instances $TYPE in $SN"
    if ID=$(aws_ ec2 run-instances --image-id "$AMI" --instance-type "$TYPE" --key-name "$KEY" \
        --security-group-ids "$SG" --subnet-id "$SN" --block-device-mappings "$BDM" \
        --instance-initiated-shutdown-behavior stop \
        --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$NAME},{Key=purpose,Value=e9l-sitting}]" \
        --query 'Instances[0].InstanceId' --output text 2>/tmp/lc-run-err); then break; fi
    cat /tmp/lc-run-err; ID=""
    grep -q "InsufficientInstanceCapacity\|Unsupported" /tmp/lc-run-err || exit 4
  done
  [ -n "$ID" ] || { echo "no capacity in any subnet"; exit 5; }
  T0=$(date -u +%FT%TZ)
  echo "instance $ID launched $T0; waiting for running"
  aws_ ec2 wait instance-running --instance-ids "$ID"
  IP=$(ip_of "$ID")
  python -c "import json,sys;json.dump({'instance_id':sys.argv[1],'ip':sys.argv[2],'launched_utc':sys.argv[3],'type':sys.argv[4],'ami':sys.argv[5]},open(sys.argv[6],'w'),indent=1)" "$ID" "$IP" "$T0" "$TYPE" "$AMI" "$STATE"
  echo "public ip $IP; waiting for ssh"
  for i in $(seq 1 40); do
    if ssh "${SSH_OPTS[@]}" "ubuntu@$IP" true 2>/dev/null; then echo "ssh up after ${i} tries"; break; fi
    sleep 6
  done
  echo "BOX=ubuntu@$IP  BOX_KEY=$KEYFILE  (state: $STATE)"
  ;;
status)
  [ -f "$STATE" ] || { echo "no state file $STATE"; exit 0; }
  ID=$(iid); aws_ ec2 describe-instances --instance-ids "$ID" \
    --query 'Reservations[0].Instances[0].[InstanceId,State.Name,InstanceType,PublicIpAddress,LaunchTime]' --output text
  ;;
ssh)
  shift; ID=$(iid); IP=$(ip_of "$ID"); exec ssh "${SSH_OPTS[@]}" "ubuntu@$IP" "$@"
  ;;
put)
  ID=$(iid); IP=$(ip_of "$ID"); exec scp "${SSH_OPTS[@]}" "$2" "ubuntu@$IP:$3"
  ;;
stop)
  ID=$(iid); aws_ ec2 stop-instances --instance-ids "$ID" --query 'StoppingInstances[0].CurrentState.Name' --output text
  ;;
terminate)
  ID=$(iid)
  echo "terminating $ID at $(date -u +%FT%TZ)"
  aws_ ec2 terminate-instances --instance-ids "$ID" --query 'TerminatingInstances[0].CurrentState.Name' --output text
  aws_ ec2 wait instance-terminated --instance-ids "$ID"
  ST=$(aws_ ec2 describe-instances --instance-ids "$ID" --query 'Reservations[0].Instances[0].State.Name' --output text)
  echo "state now: $ST at $(date -u +%FT%TZ)"
  [ "$ST" = "terminated" ] || { echo "NOT terminated"; exit 6; }
  mv "$STATE" "$STATE.terminated.$(date -u +%Y%m%dT%H%M%SZ)"
  ;;
*)
  echo "usage: box.sh up|status|ssh [cmd]|put <local> <remote>|stop|terminate"; exit 2
  ;;
esac

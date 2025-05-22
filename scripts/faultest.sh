#!/usr/bin/env bash
set -euo pipefail

# 1) Start the publisher immediately at full speed
rm -f ~/faulttest-send.log
nohup python3.12 ~/send.py --count 1000 --no-sleep --mode persistent \
     > ~/faulttest-send.log 2>&1 &

# 2) Kill node2
START=$(date +%s.%N)
ssh afionescu@192.168.0.113 "sudo systemctl stop rabbitmq-server"
echo "→ Killed node2 at $START"

# 3) Wait for ping to fail
while sudo rabbitmqctl -n rabbit@rabbitmq-node2 ping >/dev/null 2>&1; do
  sleep 0.1
done
DROP=$(date +%s.%N)
echo "→ node2 dropped at $DROP (Δ=$(awk "BEGIN{print $DROP-$START}")s)"

# 4) Restart node2
ssh afionescu@192.168.0.113 "sudo systemctl start rabbitmq-server"
echo "→ Restarted node2"

# 5) Wait for ping to succeed
while ! sudo rabbitmqctl -n rabbit@rabbitmq-node2 ping >/dev/null 2>&1; do
  sleep 0.1
done
REJOIN=$(date +%s.%N)
echo "→ node2 rejoined at $REJOIN (Δ=$(awk "BEGIN{print $REJOIN-$DROP}")s)"

# 6) Report
echo "== Sent ==";    grep -c "Sent to" ~/faulttest-send.log
echo "== Node2 rec =="; ssh afionescu@192.168.0.113 "grep -c Received ~/receive-node2.log"
echo "== Node3 rec =="; ssh afionescu@192.168.0.114 "grep -c Received ~/receive-node3.log"

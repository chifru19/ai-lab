#!/usr/bin/env bash
set -euo pipefail

ENDPOINT="http://localhost:8000/v1/triage"

declare -a LOG_BATCH=(
  "session closed for user normal_user from 192.168.1.100 port 45210"
  "Failed password for invalid user admin from 10.0.0.99 port 50000 ssh2"
  "SQL injection attempt detected from 192.168.1.50 targeting /api/v1/users?id=1 OR 1=1"
  "sudo: root : TTY=pts/0 ; PWD=/root ; USER=root ; COMMAND=/bin/bash"
  "cron job completed successfully for system maintenance"
)

echo "==> Starting batch security event simulation against $ENDPOINT..."
for i in "${!LOG_BATCH[@]]; do
  log="${LOG_BATCH[$i]}"
  echo "--------------------------------------------------------"
  echo "[Event $((i+1))/${#LOG_BATCH[*]}] Payload: $log"
  
  PAYLOAD=$(python3 -c 'import json, sys; print(json.dumps({"log_line": sys.argv}))' "$log")
  
  START_TS=$(date +%s.%N)
  RESPONSE=$(curl -s -X POST "$ENDPOINT" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD")
  END_TS=$(date +%s.%N)
  ELAPSED=$(awk "BEGIN {print $END_TS - $START_TS}")

  # Parse fields safely via python/jq or fallback display
  echo "$RESPONSE" | python3 -c '
import sys, json
try:
    data = json.load(sys.stdin)
    print(f"  [RESULT] Gate: {data.get(\"gate_triggered\")} | Action: {data.get(\"action\")} | Containment: {data.get(\"containment_status\")} | LLM Duration: {data.get(\"duration_sec\")}s")
except Exception as e:
    print(f"  [RAW RESPONSE/ERROR]: {sys.stdin.read().strip()}")
'
  echo "  [CLIENT METRIC] Total roundtrip time: ${ELAPSED}s"
  sleep 1
done

echo "==> Batch simulation complete."

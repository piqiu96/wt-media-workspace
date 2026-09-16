#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/run-discovery-scheduler.sh

Trigger one Cloud discovery scheduling tick. The Cloud service evaluates
enabled strategies, applies timezone/idempotency rules, creates crawl_task
records, and runs due strategies. This script never writes the database.

Environment:
  WT_MEDIA_CLOUD_BASE_URL       Cloud API base (default: http://127.0.0.1:18080)
  WT_MEDIA_SCHEDULER_USER       Admin username (default: admin)
  WT_MEDIA_SCHEDULER_PASSWORD   Admin password (default: admin123)
  WT_MEDIA_SCHEDULER_REPLACE_EXISTING  Replace an existing session (default: true)
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi
if [[ $# -gt 0 ]]; then
  echo "unknown argument: $1" >&2
  usage >&2
  exit 2
fi

CLOUD_BASE_URL="${WT_MEDIA_CLOUD_BASE_URL:-http://127.0.0.1:18080}"
SCHEDULER_USER="${WT_MEDIA_SCHEDULER_USER:-admin}"
SCHEDULER_PASSWORD="${WT_MEDIA_SCHEDULER_PASSWORD:-admin123}"
SCHEDULER_REPLACE_EXISTING="${WT_MEDIA_SCHEDULER_REPLACE_EXISTING:-true}"

cookie_file="$(mktemp)"
login_response="$(mktemp)"
run_response="$(mktemp)"
trap 'rm -f "$cookie_file" "$login_response" "$run_response"' EXIT

login_payload="$(WT_MEDIA_SCHEDULER_USER_VALUE="$SCHEDULER_USER" \
  WT_MEDIA_SCHEDULER_PASSWORD_VALUE="$SCHEDULER_PASSWORD" \
  WT_MEDIA_SCHEDULER_REPLACE_VALUE="$SCHEDULER_REPLACE_EXISTING" \
  python3 -c 'import json, os; print(json.dumps({"username": os.environ["WT_MEDIA_SCHEDULER_USER_VALUE"], "password": os.environ["WT_MEDIA_SCHEDULER_PASSWORD_VALUE"], "replace_existing": os.environ["WT_MEDIA_SCHEDULER_REPLACE_VALUE"].lower() == "true"}))')"

login_status="$(curl --silent --show-error --output "$login_response" --write-out '%{http_code}' \
  --cookie-jar "$cookie_file" \
  --header 'Content-Type: application/json' \
  --data "$login_payload" \
  "$CLOUD_BASE_URL/api/v1/auth/login")"
if [[ "$login_status" != "200" ]]; then
  cat "$login_response" >&2
  echo "scheduler login failed (HTTP $login_status)" >&2
  exit 1
fi

run_status="$(curl --silent --show-error --output "$run_response" --write-out '%{http_code}' \
  --request POST \
  --cookie "$cookie_file" \
  "$CLOUD_BASE_URL/api/v1/discovery-scheduler/run-due")"
if [[ "$run_status" != "200" ]]; then
  cat "$run_response" >&2
  echo "discovery scheduler failed (HTTP $run_status)" >&2
  exit 1
fi

python3 - "$run_response" <<'PY'
import json
import sys

payload = json.load(open(sys.argv[1], encoding="utf-8"))
if payload.get("errcode") != 0:
    raise SystemExit(f"scheduler rejected: {payload.get('message', 'unknown error')}")
data = payload.get("data") or {}
print(f"scheduler tick: at={data.get('at')} triggered={data.get('triggered', 0)}")
PY

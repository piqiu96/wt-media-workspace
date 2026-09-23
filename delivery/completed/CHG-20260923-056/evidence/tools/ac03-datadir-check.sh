set -uo pipefail
TOK="$(python3 -c 'import uuid;print(uuid.uuid4())')"
SCRATCH="$(mktemp -d /tmp/wt-agent-dd-XXXX)"

PYTHONPATH=src \
WT_MEDIA_LOCAL_API_HOST=127.0.0.1 \
WT_MEDIA_LOCAL_API_PORT=18766 \
WT_MEDIA_AGENT_RUNTIME_TOKEN="$TOK" \
WT_MEDIA_AGENT_DATA_DIR="$SCRATCH" \
.venv/bin/python -m wt_media_agent.local_api.server > /tmp/agent-dd.log 2>&1 &
AGENT=$!
for _ in $(seq 1 20); do curl -sf -o /dev/null "http://127.0.0.1:18766/healthz" -H "Authorization: Bearer $TOK" && break; sleep 0.5; done
sleep 1
echo "scratch dir set to : $SCRATCH"
echo "tree under it:"
find "$SCRATCH" -maxdepth 2 | sed "s|$SCRATCH|<scratch>|" | sort
echo
echo "repo .local/ touched (should be NOTHING):"
find .local -maxdepth 2 -newermt '-3 minutes' 2>/dev/null | head -5
kill $AGENT 2>/dev/null; sleep 1
echo "listeners remaining: $(lsof -nP -iTCP:18766 -sTCP:LISTEN | wc -l | tr -d ' ')"
rm -rf "$SCRATCH"

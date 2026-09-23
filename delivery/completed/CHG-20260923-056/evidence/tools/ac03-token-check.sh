set -uo pipefail
# AC-03 premise check for T-07 commit D: the four variable names Desktop now sends
# are the ones the Agent honours, and a token makes the API demand it.
TOK="$(python3 -c 'import uuid;print(uuid.uuid4())')"
SCRATCH="$(mktemp -d /tmp/wt-agent-tok-XXXX)"

PYTHONPATH=src \
WT_MEDIA_LOCAL_API_HOST=127.0.0.1 \
WT_MEDIA_LOCAL_API_PORT=18765 \
WT_MEDIA_AGENT_RUNTIME_TOKEN="$TOK" \
WT_MEDIA_AGENT_DATA_DIR="$SCRATCH" \
.venv/bin/python -m wt_media_agent.local_api.server > /tmp/agent-tok.log 2>&1 &
AGENT=$!

for _ in $(seq 1 20); do
  curl -sf -o /dev/null "http://127.0.0.1:18765/healthz" -H "Authorization: Bearer $TOK" && break
  sleep 0.5
done

echo "agent pid            : $AGENT"
echo "listening port       : $(lsof -nP -iTCP:18765 -sTCP:LISTEN | tail -1 | awk '{print $9}')"
echo "data dir created     : $SCRATCH/data exists=$([ -d "$SCRATCH/data" ] && echo yes || echo no)"
echo
echo -n "healthz WITH token   : "; curl -s -o /tmp/with.out -w '%{http_code}' http://127.0.0.1:18765/healthz -H "Authorization: Bearer $TOK"; echo " body=$(cat /tmp/with.out)"
echo -n "healthz WITHOUT token: "; curl -s -o /tmp/without.out -w '%{http_code}' http://127.0.0.1:18765/healthz; echo " body=$(cat /tmp/without.out)"
echo -n "healthz WRONG token  : "; curl -s -o /tmp/wrong.out -w '%{http_code}' http://127.0.0.1:18765/healthz -H "Authorization: Bearer $(python3 -c 'import uuid;print(uuid.uuid4())')"; echo " body=$(cat /tmp/wrong.out)"

kill $AGENT 2>/dev/null
sleep 1
echo
echo "agent stopped        : $(lsof -nP -iTCP:18765 -sTCP:LISTEN | wc -l | tr -d ' ') listeners remaining"
rm -rf "$SCRATCH"

#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT="$(bash "$SCRIPT_DIR/local-control.sh" help)"

grep -Fqx 'Usage: scripts/local-control.sh <start|verify|stop|help>' <<<"$OUTPUT"
grep -Fqx '  start   Rebuild and start the full local end-to-end environment.' <<<"$OUTPUT"
grep -Fqx '  verify  Run end-to-end readiness checks against the running environment.' <<<"$OUTPUT"
grep -Fqx '  stop    Stop the Cloud and Local Agent processes started for local review.' <<<"$OUTPUT"

#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/local-control.sh <start|verify|stop|help>

  start   Rebuild and start the full local end-to-end environment.
  verify  Run end-to-end readiness checks against the running environment.
  stop    Stop the Cloud and Local Agent processes started for local review.
  help    Show this help.
EOF
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HARNESS="$SCRIPT_DIR/m2b-local-acceptance.sh"

case "${1:-help}" in
  start)
    exec bash "$HARNESS" all --force-restart
    ;;
  verify)
    exec bash "$HARNESS" verify
    ;;
  stop)
    exec bash "$HARNESS" stop
    ;;
  help|-h|--help)
    usage
    ;;
  *)
    echo "unknown command: $1" >&2
    usage >&2
    exit 2
    ;;
esac

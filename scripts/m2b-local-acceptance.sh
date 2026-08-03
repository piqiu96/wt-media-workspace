#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${WT_MEDIA_M2B_PYTHON_BIN:-python3}"

exec "$PYTHON_BIN" "$SCRIPT_DIR/m2b_local_acceptance.py" "$@"

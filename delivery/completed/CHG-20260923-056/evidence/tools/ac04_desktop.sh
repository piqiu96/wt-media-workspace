#!/usr/bin/env bash
# AC-04: the Desktop suite is green and `main.rs` is under the 300-line ceiling.
#
# The line count is a proxy for "the entry point is an entry point"; the ceiling
# is the acceptance number, so it is asserted rather than just printed.
#
# Usage: bash ac04_desktop.sh
set -uo pipefail

DESKTOP_DIR="${WT_MEDIA_DESKTOP_DIR:-/Users/aqiuye/Develop/workspace/wt-media/wt-media-desktop}"
cd "$DESKTOP_DIR"

echo "=== AC-04: Desktop ==="
echo "repo: $DESKTOP_DIR  HEAD: $(git rev-parse --short HEAD)"
echo

cargo test --workspace 2>&1 | grep -E '^(test result|error)' | sed 's/^/  /'
echo

lines="$(wc -l < src-tauri/src/main.rs | tr -d ' ')"
printf 'main.rs: %s lines (ceiling 300)\n' "$lines"
if [ "$lines" -ge 300 ]; then
  echo "FAIL: main.rs is at or over the ceiling"; exit 1
fi

echo
echo "=== result ==="
cargo test --workspace 2>&1 | grep -q 'FAILED' && { echo "FAIL: a test failed"; exit 1; }
echo "PASS: suite green, main.rs $lines < 300"

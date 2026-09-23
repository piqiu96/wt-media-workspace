#!/usr/bin/env bash
# AC-07: the three repositories' existing suites, run where they live.
#
# The Agent floor is 85: the baseline recorded for this CHG, so a suite that
# silently lost tests cannot pass by staying green.
#
# Usage: bash ac07_three_repos.sh
set -uo pipefail

ROOT="${WT_MEDIA_ROOT:-/Users/aqiuye/Develop/workspace/wt-media}"
fail=0

echo "=== AC-07: three repositories ==="
echo

echo "--- wt-media-agent: bash scripts/test.sh ---"
out="$(cd "$ROOT/wt-media-agent" && bash scripts/test.sh 2>&1)"
echo "$out" | grep -E '^(Ran|OK|FAILED)' | sed 's/^/  /'
ran="$(echo "$out" | sed -nE 's/^Ran ([0-9]+) tests?.*/\1/p' | tail -1)"
echo "$out" | grep -q '^OK' || { echo "  FAIL: suite not OK"; fail=1; }
[ "${ran:-0}" -ge 85 ] || { echo "  FAIL: $ran < 85 baseline"; fail=1; }
echo

echo "--- wt-media-desktop: cargo test --workspace ---"
out="$(cd "$ROOT/wt-media-desktop" && cargo test --workspace 2>&1)"
echo "$out" | grep -E '^test result' | sed 's/^/  /'
echo "$out" | grep -q 'FAILED' && { echo "  FAIL: a test failed"; fail=1; }
echo

echo "--- wt-media-cloud/web: npm test ---"
out="$(cd "$ROOT/wt-media-cloud/web" && npm test 2>&1)"
echo "$out" | grep -E '^( *Test Files| *Tests)' | sed 's/^/  /'
echo "$out" | grep -qE 'failed' && { echo "  FAIL: a test failed"; fail=1; }
echo

echo "=== result ==="
[ "$fail" -eq 0 ] && echo "PASS: all three suites green, agent >= 85" || echo "FAIL"
exit "$fail"

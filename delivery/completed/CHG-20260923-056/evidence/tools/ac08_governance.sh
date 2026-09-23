#!/usr/bin/env bash
# AC-08: the two governance verifiers the plan names, with 0 ERROR.
#
# The verifier's own contract (its header) is "ERROR: a declared invariant is
# broken. Exit code is 1", so the verdict is the exit code, not a substring.
#
# A verifier that prints nothing and exits 0 is indistinguishable from one that
# works, so both scripts are also run against a **copy** of the workspace with a
# required file removed: there they must report ERROR and exit 1. The copy is
# under $TMPDIR and the real tree is never touched.
#
# `verify_m0_config.py` and the other verifiers are out of scope for this CHG;
# their pre-existing red items are registered in the change record, so naming
# exactly two scripts here is deliberate rather than an omission.
#
# Usage: bash ac08_governance.sh
set -uo pipefail

WS_DIR="${WT_MEDIA_WORKSPACE:-/Users/aqiuye/Develop/workspace/wt-media/wt-media-workspace}"
cd "$WS_DIR"

fail=0

echo "=== AC-08: governance verifiers ==="
echo "repo: $WS_DIR  HEAD: $(git rev-parse --short HEAD)"
echo

for script in verify_agent_entry.py verify_delivery_governance.py; do
  echo "--- $script ---"
  out="$(python3 "scripts/$script" 2>&1)"
  code=$?
  echo "$out" | tail -5 | sed 's/^/  /'
  printf '  exit=%s\n' "$code"
  if [ "$code" -ne 0 ]; then echo "  FAIL: non-zero exit"; fail=1; fi
  if echo "$out" | grep -qi 'error'; then
    echo "  FAIL: output mentions an error"; fail=1
  fi
  echo
done

echo "--- positive control: the same verifiers on a broken copy ---"
probe="$(mktemp -d)/wt-media-workspace"
cp -R "$WS_DIR" "$probe"
rm -f "$probe/.ai/CURRENT_CONTEXT.md"
mkdir -p "$probe/.ai"   # keep the directory, drop the file it must find
for script in verify_agent_entry.py verify_delivery_governance.py; do
  out="$(cd "$probe" && python3 "scripts/$script" 2>&1)"; code=$?
  first="$(echo "$out" | grep -i 'error' | head -1)"
  printf '  %-32s exit=%s  %s\n' "$script" "$code" "${first:0:96}"
  if [ "$code" -eq 0 ]; then
    echo "    HARD STOP: a required file is missing and the verifier still passed"
    fail=1
  fi
done
rm -rf "$(dirname "$probe")"
echo

echo "=== result ==="
[ "$fail" -eq 0 ] && echo "PASS: 0 ERROR on the real tree, non-zero exit on the broken copy" || echo "FAIL"
exit "$fail"

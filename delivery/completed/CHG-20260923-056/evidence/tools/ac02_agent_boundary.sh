#!/usr/bin/env bash
# AC-02: executors do not build clients from the environment; every client is
# constructed at one injection point.
#
# Two kinds of evidence, because either alone is weak:
#   1. the AST test that enforces the boundary (it can see levels grep cannot);
#   2. grep, which is what a reader would run, reported with its denominator and
#      with a positive control.
#
# The positive control matters more than the zeros. "0 hits" from a pattern that
# cannot match anything is indistinguishable from a clean tree, so each pattern
# is also run against a string that must produce hits. A pattern with a zero
# result and a zero control is reported as a broken measurement, not a pass.
#
# The assertions are about *where* hits land, not how many there are: "one
# construction site, and it is the factory" is the property, and pinning the
# count instead would break on a refactor that kept the property.
#
# Usage: bash ac02_agent_boundary.sh
set -uo pipefail

AGENT_DIR="${WT_MEDIA_AGENT_DIR:-/Users/aqiuye/Develop/workspace/wt-media/wt-media-agent}"
cd "$AGENT_DIR"

fail=0

# Search `path` for `pattern`, print every hit, and require that each hit's file
# is one of the allowed paths. `control` is a string the pattern must match.
sites() {
  local label="$1" pattern="$2" path="$3" control="$4" allowed="$5"
  local lines total
  total="$(find $path -name '*.py' | xargs wc -l | tail -1 | awk '{print $1}')"
  lines="$(grep -rnE "$pattern" $path --include='*.py' || true)"

  if printf '%s\n' "$control" | grep -qE "$pattern"; then :; else
    printf '%-52s HARD STOP: pattern matches nothing, not even its control\n' "$label"
    fail=1; return
  fi

  printf '%-52s %s hit(s) (of %s lines)\n' "$label" "$(printf '%s' "$lines" | grep -c . )" "$total"
  local bad=0
  while IFS= read -r hit; do
    [ -z "$hit" ] && continue
    printf '    %s\n' "$hit"
    local file="${hit%%:*}"
    case "$allowed" in
      *" $file "*) : ;;
      *) printf '        ^^ NOT in the allowed set: %s\n' "$allowed"; bad=1 ;;
    esac
  done <<< "$lines"
  [ "$bad" -ne 0 ] && fail=1
  return 0
}

echo "=== AC-02: environment reads and client construction ==="
echo "repo: $AGENT_DIR  HEAD: $(git rev-parse --short HEAD)"
echo

echo "--- 1. environment reads: one module only ---"
sites "os.getenv / os.environ in src/" \
  'os\.getenv|os\.environ' 'src' 'x = os.getenv("A")' \
  ' src/wt_media_agent/runtime/config.py '
echo

echo "--- 2. BitBrowser client: built only by its factory ---"
sites "BitBrowserClient( in src/" \
  'BitBrowserClient\(' 'src' 'c = BitBrowserClient(url)' \
  ' src/wt_media_agent/clients/bitbrowser/factory.py '
sites "  ... under executors/ (none may exist)" \
  'BitBrowserClient\(' 'src/wt_media_agent/executors' 'c = BitBrowserClient(url)' ' '
sites "  ... under local_api/ (none may exist)" \
  'BitBrowserClient\(' 'src/wt_media_agent/local_api' 'c = BitBrowserClient(url)' ' '
echo

echo "--- 3. Cloud client: constructed only at assembly ---"
sites "CloudAgentClient( in src/" \
  'CloudAgentClient\(' 'src' 'c = CloudAgentClient(url)' \
  ' src/wt_media_agent/bootstrap/app.py '
sites "  ... under executors/ (none may exist)" \
  'CloudAgentClient\(' 'src/wt_media_agent/executors' 'c = CloudAgentClient(url)' ' '
echo

echo "--- 4. what the AST test says (the level grep cannot see) ---"
PYTHONPATH=src .venv/bin/python -m unittest tests.test_dependency_boundaries 2>&1 | tail -3
echo

echo "=== result ==="
if [ "$fail" -eq 0 ]; then
  echo "PASS: every pattern had a live control and every hit landed in its allowed file"
else
  echo "FAIL: see NOT-in-allowed-set / HARD STOP above"
fi
exit "$fail"

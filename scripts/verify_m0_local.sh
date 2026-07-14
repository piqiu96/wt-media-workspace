#!/usr/bin/env sh
set -eu

WORKSPACE_REPO="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
OUTER_ROOT="$(CDPATH= cd -- "$WORKSPACE_REPO/.." && pwd)"

GO_BIN="${GO_BIN:-$OUTER_ROOT/../devenv/go26/go/bin/go}"
WT_MEDIA_GO_ROOT="${WT_MEDIA_GO_ROOT:-$OUTER_ROOT/../devenv/go26/go}"
WT_MEDIA_GO_PATH="${WT_MEDIA_GO_PATH:-$OUTER_ROOT/../devenv/go19/gopath}"

(cd "$WORKSPACE_REPO" && python3 -m unittest discover -s tests)
(cd "$WORKSPACE_REPO" && python3 scripts/verify_skills.py)
(cd "$WORKSPACE_REPO" && python3 scripts/verify_m0_config.py)

(
  cd "$OUTER_ROOT/wt-media-cloud"
  env GOROOT="$WT_MEDIA_GO_ROOT" GOPATH="$WT_MEDIA_GO_PATH" GO_BIN="$GO_BIN" GOCACHE="$PWD/.cache/go-build" scripts/verify-health.sh
)

(cd "$OUTER_ROOT/wt-media-agent" && scripts/verify-health.sh)
(cd "$OUTER_ROOT/wt-media-desktop" && npm run verify)

echo "WT Media M0 local verification ok"

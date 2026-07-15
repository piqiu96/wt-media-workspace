#!/usr/bin/env sh
set -eu

WORKSPACE_REPO="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
OUTER_ROOT="$(CDPATH= cd -- "$WORKSPACE_REPO/.." && pwd)"

GO_BIN="${GO_BIN:-$OUTER_ROOT/../devenv/go26/go/bin/go}"
WT_MEDIA_GO_ROOT="${WT_MEDIA_GO_ROOT:-$OUTER_ROOT/../devenv/go26/go}"
WT_MEDIA_GO_PATH="${WT_MEDIA_GO_PATH:-$OUTER_ROOT/../devenv/go19/gopath}"
AGENT_M0_DATA_DIR="${AGENT_M0_DATA_DIR:-/tmp/wt-media-agent-m0-local}"

(cd "$WORKSPACE_REPO" && python3 -m unittest discover -s tests)
(cd "$WORKSPACE_REPO" && python3 scripts/verify_skills.py)
(cd "$WORKSPACE_REPO" && python3 scripts/verify_m0_config.py)
(cd "$WORKSPACE_REPO" && python3 scripts/verify_product_master_alignment.py)

(
  cd "$OUTER_ROOT/wt-media-cloud"
  env GOROOT="$WT_MEDIA_GO_ROOT" GOPATH="$WT_MEDIA_GO_PATH" GO_BIN="$GO_BIN" GOCACHE="$PWD/.cache/go-build" scripts/bootstrap.sh
  env GOROOT="$WT_MEDIA_GO_ROOT" GOPATH="$WT_MEDIA_GO_PATH" GO_BIN="$GO_BIN" GOCACHE="$PWD/.cache/go-build" scripts/test.sh
  if [ -n "${WT_MEDIA_MYSQL_DSN:-}" ]; then
    env GOROOT="$WT_MEDIA_GO_ROOT" GOPATH="$WT_MEDIA_GO_PATH" GO_BIN="$GO_BIN" GOCACHE="$PWD/.cache/go-build" scripts/migrate.sh
    env GOROOT="$WT_MEDIA_GO_ROOT" GOPATH="$WT_MEDIA_GO_PATH" GO_BIN="$GO_BIN" GOCACHE="$PWD/.cache/go-build" scripts/migrate.sh
  else
    echo "Skipping Cloud MySQL migration: WT_MEDIA_MYSQL_DSN is not set"
  fi
  env GOROOT="$WT_MEDIA_GO_ROOT" GOPATH="$WT_MEDIA_GO_PATH" GO_BIN="$GO_BIN" GOCACHE="$PWD/.cache/go-build" scripts/build.sh
)

(
  cd "$OUTER_ROOT/wt-media-agent"
  scripts/bootstrap.sh
  scripts/test.sh
  scripts/migrate-storage.sh --data-dir "$AGENT_M0_DATA_DIR"
  scripts/migrate-storage.sh --data-dir "$AGENT_M0_DATA_DIR"
  scripts/build.sh
)

(
  cd "$OUTER_ROOT/wt-media-desktop"
  scripts/bootstrap.sh
  npm run lint
  scripts/test.sh
  scripts/build.sh
)

echo "WT Media M0 local verification ok"

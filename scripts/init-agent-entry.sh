#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/init-agent-entry.sh workspace [--dry-run]
  scripts/init-agent-entry.sh repo <cloud|agent|desktop|path> [--dry-run]

Initialize the agent entry files for the workspace or one specified repository.
Existing files are never overwritten.
With --dry-run nothing is written; the script only reports what it would do.
USAGE
}

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MAP_FILE="$ROOT/config/repository-map.yaml"

if [[ ! -f "$MAP_FILE" ]]; then
  echo "missing repository map: $MAP_FILE" >&2
  exit 1
fi

map_path() {
  local key="$1"
  awk -v key="$key" '
    $0 ~ "^[[:space:]]*" key ":[[:space:]]*$" { selected = 1; next }
    selected && /path:/ {
      sub(/^[[:space:]]*path:[[:space:]]*/, "")
      print
      exit
    }
  ' "$MAP_FILE"
}

# Always consume the heredoc on stdin, even when nothing is written, so a
# dry run cannot leave the caller's pipeline in an unexpected state.
write_if_missing() {
  local file="$1"
  if [[ -e "$file" ]]; then
    printf 'exists: %s\n' "${file#"$ROOT"/}"
    cat > /dev/null
  elif [[ "$DRY_RUN" -eq 1 ]]; then
    printf 'would create: %s\n' "${file#"$ROOT"/}"
    cat > /dev/null
  else
    cat > "$file"
    printf 'created: %s\n' "${file#"$ROOT"/}"
  fi
}

init_workspace() {
  if [[ "$DRY_RUN" -eq 0 ]]; then
    mkdir -p "$ROOT/.ai"
  fi

  write_if_missing "$ROOT/AGENTS.md" <<'FILE'
# WT Media Workspace Agent Rules

Read `AGENT-INDEX.md` first.

This repository is the governance control plane. It does not contain runtime code.
FILE

  write_if_missing "$ROOT/CLAUDE.md" <<'FILE'
# WT Media Workspace Claude Entry

Read `AGENT-INDEX.md` first.

This repository is governance-only and must not become a runtime dependency.
FILE

  write_if_missing "$ROOT/AGENT-INDEX.md" <<'FILE'
# WT Media Agent Index

Read `.ai/CURRENT_CONTEXT.md` for the current execution snapshot.
FILE

  write_if_missing "$ROOT/.ai/CURRENT_CONTEXT.md" <<'FILE'
# WT Media Current AI Context

- Status: ACTIVE
- Active CHG: TBD
- Current milestone: TBD
FILE
}

init_repo() {
  local input="$1"
  local target

  case "$input" in
    cloud|agent|desktop)
      local mapped
      mapped="$(map_path "$input")"
      if [[ -z "$mapped" ]]; then
        echo "repository '$input' is not defined in $MAP_FILE" >&2
        exit 1
      fi
      target="$ROOT/$mapped"
      ;;
    *)
      if [[ "$input" = /* ]]; then
        target="$input"
      else
        target="$ROOT/$input"
      fi
      ;;
  esac

  if [[ ! -d "$target" ]]; then
    echo "target repository does not exist: $target" >&2
    exit 1
  fi

  if [[ ! -e "$target/.git" ]]; then
    echo "target is not a Git repository: $target" >&2
    exit 1
  fi

  local repo_name
  repo_name="$(basename "$target")"

  local workspace_rel
  workspace_rel="$(python3 - "$ROOT" "$target" <<'PY'
import os
import sys
print(os.path.relpath(sys.argv[1], start=sys.argv[2]))
PY
)"

  write_if_missing "$target/AGENT-INDEX.md" <<FILE
# ${repo_name} Agent Index

## Workspace

\`$workspace_rel\`

## Rule

- Read this file before code changes.
- Read \`AGENTS.md\` and \`CLAUDE.md\` in this repository.
- Use the workspace only as governance context, never as a runtime dependency.
FILE

  write_if_missing "$target/AGENTS.md" <<FILE
# ${repo_name} Agent Rules

Read \`AGENT-INDEX.md\` first.

Keep runtime implementation inside this repository and follow its own architecture and tests.
FILE

  write_if_missing "$target/CLAUDE.md" <<FILE
# ${repo_name} Claude Entry

Read \`AGENT-INDEX.md\` first.

This repository owns its own runtime scope. Do not make it depend on the governance workspace at runtime.
FILE
}

DRY_RUN=0
positional=()
for argument in "$@"; do
  case "$argument" in
    --dry-run) DRY_RUN=1 ;;
    *) positional+=("$argument") ;;
  esac
done

case "${positional[0]:-}" in
  workspace)
    init_workspace
    ;;
  repo)
    if [[ ${#positional[@]} -ne 2 ]]; then
      usage >&2
      exit 2
    fi
    init_repo "${positional[1]}"
    ;;
  help|-h|--help)
    usage
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac

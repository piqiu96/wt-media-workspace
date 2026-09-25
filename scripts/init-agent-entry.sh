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

The shape written here is the shape required by
docs/engineering/specs/agent-workspace-conventions.md section 3:
AGENTS.md and CLAUDE.md are pointers, AGENT-INDEX.md carries the body, and
DIRECTORY_MAP.md carries the directory facts and the no-scan zones.
The execution snapshot is not written here: it has exactly one generator,
scripts/prepare_ai_workspace.py.
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
  REPO_NAME="WT Media Workspace"

  write_if_missing "$ROOT/AGENTS.md" <<'FILE'
# WT Media Workspace Agent Rules（Codex 入口）

- 正文：`AGENT-INDEX.md`

## 权威源

本仓库的治理规范、仓库职责边界、需求路由、上下文加载规则与**全部红线**的唯一落点是 [`AGENT-INDEX.md`](AGENT-INDEX.md)。本文件只做指针，不复述其中任何规则。

`AGENTS.md` 与 `CLAUDE.md` 平级：互不软链、互不替代，二者都指向 `AGENT-INDEX.md`。
FILE

  write_if_missing "$ROOT/CLAUDE.md" <<'FILE'
# CLAUDE.md

- 正文：`AGENT-INDEX.md`

## 权威源

本仓库的治理规范、仓库职责边界、需求路由、上下文加载规则与**全部红线**的唯一落点是 [`AGENT-INDEX.md`](AGENT-INDEX.md)。本文件只做指针，不复述其中任何规则。

`AGENTS.md` 与本文件平级：互不软链、互不替代，二者都指向 `AGENT-INDEX.md`。
FILE

  write_if_missing "$ROOT/AGENT-INDEX.md" <<'FILE'
# WT Media Agent Index

> 本文件是 WT Media 全部仓库的 Agent 统一索引与治理规范正文。

**读取顺序**：见第 4 节——该节是全项目唯一落点，`.ai/CURRENT_CONTEXT.md` 的 Required Reading Order 是它的生成物镜像。

（治理仓不适用运行仓的八节序列；本仓章节结构由本文件自己规定。按需补第 1–12 节。）
FILE

  if [[ -e "$ROOT/.ai/CURRENT_CONTEXT.md" ]]; then
    printf 'exists: %s\n' ".ai/CURRENT_CONTEXT.md"
  else
    printf 'not created: %s\n' ".ai/CURRENT_CONTEXT.md"
    printf '  next: python3 scripts/prepare_ai_workspace.py --no-active\n'
    printf '  （执行快照只有这一个生成器；本脚本不再手写它——手写版没有反引号，会被 CONTEXT_RE 静默读成 None）\n'
  fi
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
  REPO_NAME="$repo_name"

  local workspace_rel
  workspace_rel="$(python3 - "$ROOT" "$target" <<'PY'
import os
import sys
print(os.path.relpath(sys.argv[1], start=sys.argv[2]))
PY
)"

  write_if_missing "$target/AGENT-INDEX.md" <<FILE
# ${repo_name} Agent Index

> 本文件是本仓**全部正式内容**的唯一落点。每节写实处，不留占位符。

## 依赖

（本仓依赖的兄弟仓与外部服务，以及各自用在哪。不写版本号。）

## 定位

（本仓是什么，在系统里承担什么。）

## 本仓库拥有

- 待补

## 本仓库不拥有

- 待补

## 需求路由

| 我改什么 | 改这里 |
| --- | --- |
| 待补 | 待补 |

## 本仓规则

（本仓全部规则的唯一落点。一条一行，写清做什么／不做什么。）

- 待补

## 禁止

- 待补

## 本仓内加载顺序

- 本仓内先读什么、再读什么

本节只写**本仓内**顺序；跨仓读取顺序与全部红线的唯一落点是 \`${workspace_rel}/AGENT-INDEX.md\` 第 4 节与第 2 节，本节不复述。
FILE

  write_if_missing "$target/CLAUDE.md" <<FILE
# ${repo_name} Claude 入口

- 正文：\`AGENT-INDEX.md\`

## 权威源

本仓的全部正式内容——定位、职责边界、需求路由、**本仓规则**、禁止项与**本仓内加载顺序**——的唯一落点是 [\`AGENT-INDEX.md\`](AGENT-INDEX.md)。本文件只做指针，不复述其中任何规则。

跨仓的读取顺序与全部红线的唯一落点是 [\`${workspace_rel}/AGENT-INDEX.md\`](${workspace_rel}/AGENT-INDEX.md) 第 4 节与第 2 节。
FILE

  write_if_missing "$target/AGENTS.md" <<FILE
# ${repo_name} Agent Rules（Codex 入口）

- 正文：\`AGENT-INDEX.md\`

## 权威源

本仓的全部正式内容——定位、职责边界、需求路由、**本仓规则**、禁止项与**本仓内加载顺序**——的唯一落点是 [\`AGENT-INDEX.md\`](AGENT-INDEX.md)。本文件只做指针，不复述其中任何规则。

跨仓的读取顺序与全部红线的唯一落点是 [\`${workspace_rel}/AGENT-INDEX.md\`](${workspace_rel}/AGENT-INDEX.md) 第 4 节与第 2 节。
FILE

  write_if_missing "$target/DIRECTORY_MAP.md" <<FILE
# ${repo_name} Directory Map

> 本文件是本仓**目录事实与禁止扫描区**的唯一落点。它不承载规则——规则归 \`AGENT-INDEX.md\`。

## 目录

生成时的顶层目录（职责与进入时机需人工补全）：

$(list_top_dirs "$target")

## 禁止扫描区

（暂无。把确实不必进入的目录列到这里并写明理由——**本节是禁止扫描区的唯一落点**，不要在 \`AGENT-INDEX.md\` 里再写一份。）
FILE
}

# Top-level directories of $1, one bullet each, without the .git dir.
list_top_dirs() {
  local dir="$1"
  local entry
  for entry in "$dir"/*/ "$dir"/.*/; do
    [[ -d "$entry" ]] || continue
    entry="$(basename "$entry")"
    case "$entry" in
      .|..|.git|"*") continue ;;
    esac
    printf -- '- `%s/`\n' "$entry"
  done
}

DRY_RUN=0
REPO_NAME=""
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

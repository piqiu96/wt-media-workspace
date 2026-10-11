#!/usr/bin/env bash
#
# 本地开发环境的唯一入口：启停与进程状态。
#
# 本文件是**薄封装**：真正干活的是 scripts/m2b_local_acceptance.py，本文件只负责
# 动词分派与 usage。端口、地址、运行目录等数值型参数一律不出现在本文件里——它们的
# 唯一落点是 harness 读取的配置文件与环境变量，在这里复述一份就是第二份真相。
# 这条约束由 scripts/verify-control.sh 机检。
#
# 与 `AGENT-INDEX.md` §6「修改 Agent Sidecar 启停 → Desktop」的分工：本文件管的是
# **本地开发环境**里 Cloud、Local Agent、Cloud worker 与两个前端 dev server 的进程
# 启停，sidecar 的生命周期由 Desktop 的 Rust 实现持有，是另一件事。
set -euo pipefail

BIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HARNESS="$BIN_DIR/../scripts/m2b-local-acceptance.sh"

usage() {
  cat <<'EOF'
Usage: bin/control.sh <start|stop|restart|status|verify|help>

  start    Rebuild and start the full local end-to-end environment.
  stop     Stop the Cloud, Local Agent, Cloud worker and front-end dev servers started for local review.
  restart  Stop those processes, then rebuild and start the environment again.
  status   Report whether those processes are alive and, where they serve one, answering.
  verify   Run end-to-end readiness checks against the running environment.
  help     Show this help.
EOF
}

case "${1:-help}" in
  start)   exec bash "$HARNESS" all --force-restart ;;
  stop)    exec bash "$HARNESS" stop ;;
  restart) bash "$HARNESS" stop && exec bash "$HARNESS" all --force-restart ;;
  status)  exec bash "$HARNESS" status ;;
  verify)  exec bash "$HARNESS" verify ;;
  help|-h|--help) usage ;;
  *) echo "unknown command: $1" >&2; usage >&2; exit 2 ;;
esac

#!/usr/bin/env bash
#
# bin/control.sh 的判别力测试。
#
# 三条判据各自能失败，不是「跑一遍没报错」：
#   1. usage 逐字断言——动词清单改了而 usage 没跟着改，这里红。
#   2. 未知名词退出码 2 且 usage 落到 stderr——分派被短路成「总是打印 usage」时，这里红。
#   3. `status` 端到端跑通并给出两行读数——HARNESS 路径写错时，这里红（命令找不到）。
#   4. 本文件不含端口字面量——把端口搬进 control.sh 时，这里红。
set -euo pipefail

BIN_DIR="$(cd "$(dirname "$0")/../bin" && pwd)"
CONTROL="$BIN_DIR/control.sh"
HARNESS="$BIN_DIR/../scripts/m2b-local-acceptance.sh"

# 每一条断言的失败都要自己说明是哪一条——裸 grep 在 set -e 下只给一个静默的非零退出码。
assert_line() {
  grep -Fqx "$1" <<<"$OUTPUT" || { echo "FAIL: usage line missing: $1" >&2; exit 1; }
}

# 1. usage 逐字
OUTPUT="$(bash "$CONTROL" help)"
assert_line 'Usage: bin/control.sh <start|stop|restart|status|verify|help>'
assert_line '  start    Rebuild and start the full local end-to-end environment.'
assert_line '  stop     Stop the Cloud and Local Agent processes started for local review.'
assert_line '  restart  Stop those processes, then rebuild and start the environment again.'
assert_line '  status   Report whether those processes are alive and answering their health endpoint.'
assert_line '  verify   Run end-to-end readiness checks against the running environment.'
assert_line '  help     Show this help.'

# 2. 未知名词：退出码 2，usage 在 stderr（不在 stdout）
set +e
UNKNOWN_OUT="$(bash "$CONTROL" no-such-verb 2>/dev/null)"
UNKNOWN_RC=$?
UNKNOWN_ERR="$(bash "$CONTROL" no-such-verb 2>&1 >/dev/null)"
set -e
[ "$UNKNOWN_RC" -eq 2 ] || { echo "FAIL: unknown verb exit=$UNKNOWN_RC, want 2" >&2; exit 1; }
[ -z "$UNKNOWN_OUT" ] || { echo "FAIL: unknown verb wrote usage to stdout" >&2; exit 1; }
grep -Fq 'Usage: bin/control.sh' <<<"$UNKNOWN_ERR" || { echo "FAIL: unknown verb: no usage on stderr" >&2; exit 1; }

# 3. status 端到端：先证明 harness 在，再跑，再验两行读数
test -f "$HARNESS" || { echo "FAIL: harness missing at $HARNESS" >&2; exit 1; }
set +e
STATUS_OUT="$(bash "$CONTROL" status 2>&1)"
STATUS_RC=$?
set -e
case "$STATUS_RC" in 0|1) ;; *) echo "FAIL: status exit=$STATUS_RC, want 0 or 1" >&2; exit 1 ;; esac
grep -Eq '^cloud: pid=[^ ]* alive=(yes|no) health=(ok|down) url=' <<<"$STATUS_OUT" \
  || { echo "FAIL: no cloud status line" >&2; exit 1; }
grep -Eq '^agent: pid=[^ ]* alive=(yes|no) health=(ok|down) url=' <<<"$STATUS_OUT" \
  || { echo "FAIL: no agent status line" >&2; exit 1; }

# 4. control.sh 不得复述端口值
if grep -nE ':[0-9]{4,5}([^0-9]|$)' "$CONTROL"; then
  echo "FAIL: bin/control.sh carries a port literal; it belongs to the harness config" >&2
  exit 1
fi

echo "PASS: bin/control.sh usage, dispatch, status wiring, and no-port-literal"

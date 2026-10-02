#!/usr/bin/env bash
#
# bin/control.sh 的判别力测试。
#
# 六条判据各自能失败，不是「跑一遍没报错」：
#   1. 入口本体：存在、被 git 跟踪、index 模式 100755、磁盘有执行位。
#   2. 入口能**直接**调用（不经 `bash`）——`bash bin/control.sh` 在缺执行位时照样成功，
#      那样写的检查与「执行位」这个缺陷正好错开一格（CHG-20260926-068 的起因）。
#   3. usage 逐字断言——动词清单改了而 usage 没跟着改，这里红。
#   4. 未知名词退出码 2 且 usage 落到 stderr——分派被短路成「总是打印 usage」时，这里红。
#   5. `status` 端到端跑通并给出三行读数（cloud/agent/worker）——HARNESS 路径写错时，
#      这里红（命令找不到）；worker 行缺少时也红。
#   6. 本文件不含端口字面量——把端口搬进 control.sh 时，这里红。
#
# 判据 1／2 的 `index 模式` 与 `磁盘执行位` 是**两件事**：磁盘 `+x` 而 index `100644` 在本机
# 恒绿、在新克隆与 CI 恒红，所以两侧都要断言。缺执行位时退出码本身随调用方 shell 选项变化
# （实测：无选项／`-u`／`pipefail` → 126，`-e`／`-eu` → 1），故下面断言**属性**（退 0）而非字面码。
set -euo pipefail

BIN_DIR="$(cd "$(dirname "$0")/../bin" && pwd)"
ROOT_DIR="$(cd "$BIN_DIR/.." && pwd)"
CONTROL="$BIN_DIR/control.sh"
HARNESS="$BIN_DIR/../scripts/m2b-local-acceptance.sh"

# 每一条断言的失败都要自己说明是哪一条——裸 grep 在 set -e 下只给一个静默的非零退出码。
die() { echo "FAIL: $1" >&2; exit 1; }

# 1. 入口本体：存在、被跟踪、index 模式、磁盘执行位
[ -f "$CONTROL" ] || die "bin/control.sh missing at $CONTROL"
git -C "$ROOT_DIR" ls-files --error-unmatch bin/control.sh >/dev/null 2>&1 \
  || die "bin/control.sh is not tracked by git in $ROOT_DIR"
INDEX_MODE="$(git -C "$ROOT_DIR" ls-files -s -- bin/control.sh | awk '{print $1}')"
[ "$INDEX_MODE" = "100755" ] \
  || die "git index mode is '$INDEX_MODE', want 100755 (a fresh checkout would not be executable)"
[ -x "$CONTROL" ] || die "bin/control.sh is not executable on disk"

# 2. 直接调用（不是 `bash "$CONTROL"`）
set +e
OUTPUT="$("$CONTROL" help 2>/dev/null)"
HELP_RC=$?
set -e
[ "$HELP_RC" -eq 0 ] \
  || die "direct invocation '$CONTROL help' exit=$HELP_RC, want 0 (a non-executable entry reads 126 from a plain shell and 1 from inside this set -e script)"

# 3. usage 逐字
assert_line() {
  grep -Fqx "$1" <<<"$OUTPUT" || die "usage line missing: $1"
}
assert_line 'Usage: bin/control.sh <start|stop|restart|status|verify|help>'
assert_line '  start    Rebuild and start the full local end-to-end environment.'
assert_line '  stop     Stop the Cloud, Local Agent and Cloud worker processes started for local review.'
assert_line '  restart  Stop those processes, then rebuild and start the environment again.'
assert_line '  status   Report whether those processes are alive and, where they serve one, answering.'
assert_line '  verify   Run end-to-end readiness checks against the running environment.'
assert_line '  help     Show this help.'

# 4. 未知名词：退出码 2，usage 在 stderr（不在 stdout）
set +e
UNKNOWN_OUT="$("$CONTROL" no-such-verb 2>/dev/null)"
UNKNOWN_RC=$?
UNKNOWN_ERR="$("$CONTROL" no-such-verb 2>&1 >/dev/null)"
set -e
[ "$UNKNOWN_RC" -eq 2 ] || die "unknown verb exit=$UNKNOWN_RC, want 2"
[ -z "$UNKNOWN_OUT" ] || die "unknown verb wrote usage to stdout"
grep -Fq 'Usage: bin/control.sh' <<<"$UNKNOWN_ERR" || die "unknown verb: no usage on stderr"

# 5. status 端到端：先证明 harness 在，再跑，再验三行读数
#
# worker 那一行单独断言：它是唯一没有健康端点的组件（`health=pid-only`、`url=-`）。
# 少了这条，把 worker 从 status 里删掉仍然全绿——而「status 看不见 worker」正是这个
# 组件此前不存在时的读法。
test -f "$HARNESS" || die "harness missing at $HARNESS"
set +e
STATUS_OUT="$("$CONTROL" status 2>&1)"
STATUS_RC=$?
set -e
case "$STATUS_RC" in 0|1) ;; *) die "status exit=$STATUS_RC, want 0 or 1" ;; esac
grep -Eq '^cloud: pid=[^ ]* alive=(yes|no) health=(ok|down) url=' <<<"$STATUS_OUT" \
  || die "no cloud status line"
grep -Eq '^agent: pid=[^ ]* alive=(yes|no) health=(ok|down) url=' <<<"$STATUS_OUT" \
  || die "no agent status line"
grep -Eq '^worker: pid=[^ ]* alive=(yes|no) health=pid-only url=-$' <<<"$STATUS_OUT" \
  || die "no worker status line"

# 6. control.sh 不得复述端口值
if grep -nE ':[0-9]{4,5}([^0-9]|$)' "$CONTROL"; then
  die "bin/control.sh carries a port literal; it belongs to the harness config"
fi

echo "PASS: bin/control.sh entry (tracked, index 100755, executable, directly invocable), usage, dispatch, status wiring (cloud/agent/worker), and no-port-literal"

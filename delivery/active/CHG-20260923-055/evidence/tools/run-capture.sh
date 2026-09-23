#!/usr/bin/env bash
# 一次跑完「登录 → 起模拟台 → 抓图 → 收台」。
#
# 为什么必须原子：运营账号的会话 cookie 存活窗口很短（实测约 10 分钟），
# 分步操作会让抓图落在过期会话上，抓回登录页 —— 那正是本次诊断早期
# 得到 18KB「内容池」截图的假象来源。
#
# 凭据不落在任何文件里：密码从环境变量 WT055_PASSWORD 读入。
# 会话 cookie 只写进 0600 临时文件 /tmp/.wt055session，收台时删除。
#
# 用法：
#   WT055_PASSWORD=<运营账号密码> bash run-capture.sh <输出目录> [视口规格...]
set -uo pipefail

# tools → evidence → CHG-…-055 → active → delivery → wt-media-workspace → wt-media
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../../../.." && pwd)"   # wt-media/
CLOUD="${CLOUD:-http://127.0.0.1:18080}"
TOOLS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SESSION_FILE=/tmp/.wt055session
PROXY_LOG="${PROXY_LOG:-/tmp/wt055-proxy.log}"
USER_NAME="${WT055_USER:-operator01}"

OUT_DIR="${1:?用法: WT055_PASSWORD=... bash run-capture.sh <输出目录> [视口规格...]}"
shift || true

: "${WT055_PASSWORD:?必须通过环境变量 WT055_PASSWORD 提供账号密码，脚本不存凭据}"

umask 077

# ---- 1. 登录（替换旧会话：该账号是单会话策略，不替换会拿到 409）----
hdr="$(mktemp /tmp/wt055-hdr-XXXXXX)"
body="$(mktemp /tmp/wt055-body-XXXXXX)"
code="$(curl -s -D "$hdr" -o "$body" -w '%{http_code}' -X POST "$CLOUD/api/v1/auth/login" \
  -H 'Content-Type: application/json' \
  -d "{\"username\":\"$USER_NAME\",\"password\":\"$WT055_PASSWORD\",\"replace_existing\":true}")"
if [ "$code" != "200" ]; then
  echo "登录失败 HTTP $code：$(cat "$body")" >&2
  rm -f "$hdr" "$body"; exit 1
fi
python3 - "$hdr" "$SESSION_FILE" <<'PY'
import re, sys, pathlib
hdr, dest = sys.argv[1], sys.argv[2]
m = re.search(r"wt_media_session=([^;]+);", pathlib.Path(hdr).read_text())
if not m:
    raise SystemExit("登录响应里没有 wt_media_session")
p = pathlib.Path(dest); p.write_text(m.group(1)); p.chmod(0o600)
PY
rm -f "$hdr" "$body"
echo "会话已刷新（临时文件 0600，收台时删除）"

# ---- 2. 起模拟台（原样附加 tauri.conf.json 的 CSP）----
pkill -f "csp-probe-proxy.py" 2>/dev/null; sleep 1
WT_MEDIA_M3_SESSION="$(cat "$SESSION_FILE")" nohup python3 "$TOOLS/csp-probe-proxy.py" \
  "$REPO_ROOT/wt-media-desktop/.generated/frontend" \
  --csp-file "$REPO_ROOT/wt-media-desktop/src-tauri/tauri.conf.json" \
  > "$PROXY_LOG" 2>&1 &
sleep 3
grep -q "CSP in effect" "$PROXY_LOG" || { echo "模拟台未就绪" >&2; cat "$PROXY_LOG"; exit 1; }
grep "CSP in effect" "$PROXY_LOG"

# ---- 3. 抓图 ----
bash "$TOOLS/capture.sh" "$OUT_DIR" "$@"
rc=$?

# ---- 4. 收台 ----
pkill -f "csp-probe-proxy.py" 2>/dev/null
rm -f "$SESSION_FILE"
echo "模拟台已停，会话临时文件已删除"
exit $rc

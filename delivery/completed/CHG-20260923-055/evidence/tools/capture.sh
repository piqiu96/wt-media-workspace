#!/usr/bin/env bash
# 无头抓图：把打包产物挂在「带应用真实 CSP」的模拟台（csp-probe-proxy.py）上逐视口取图。
#
# 为什么要这一层：原生端的差异来自 tauri.conf.json 的 CSP，而普通无头 Chromium
# 不带 CSP —— 这正是首轮 Desktop 走查漏掉根因 A 的原因。见 change.md 的证据纪律一节。
#
# 本脚本不含任何凭据。代理台需要的会话 cookie 由调用方通过环境变量传入，
# 由 csp-probe-proxy.py 在启动时读取。
#
# 用法：
#   bash capture.sh <输出目录> [视口规格...]
# 视口规格格式：<文件名>:<宽>x<高>[:<probe标签>]
set -uo pipefail
set +m          # 关掉作业控制：收掉 chrome 时 shell 会打印 "Killed: 9" 噪声，污染证据日志

CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
BASE="${BASE:-http://127.0.0.1:5174}"
BUDGET="${BUDGET:-30000}"          # 15000 太短：会抓到登录页/探针未执行
HARD_TIMEOUT="${HARD_TIMEOUT:-100}" # 单张硬超时（秒）
ROUTE="${ROUTE:-/content-pool}"

OUT_DIR="${1:?用法: capture.sh <输出目录> [文件名:宽x高[:标签] ...]}"
shift || true

SPECS=("$@")
if [ "${#SPECS[@]}" -eq 0 ]; then
  SPECS=("shot-1280x800:1280x800" "shot-1512x900:1512x900:rowdetail")
fi

mkdir -p "$OUT_DIR"
# 每次跑用全新 profile：复用 profile 会带上旧会话/缓存，抓出与本次无关的页面。
PROFILE="$(mktemp -d /tmp/wt055-chrome-XXXXXX)"
cleanup() { pkill -9 -f "user-data-dir=$PROFILE" 2>/dev/null; rm -rf "$PROFILE"; }
trap cleanup EXIT

shoot() {  # name size label
  local name="$1" size="$2" label="${3:-}" url out
  url="$BASE$ROUTE"
  [ -n "$label" ] && url="$url#probe=$label"
  out="$OUT_DIR/$name.png"
  rm -f "$out"

  # 落图后 Chrome 不会自己退出（修好 CSP 后图片会真正发起外部请求，
  # --virtual-time-budget 的网络等待把退出路径拖住）。所以不看退出码：
  # 轮询文件是否出现并停止增长，一稳定就收掉进程。
  "$CHROME" --headless=new \
    --virtual-time-budget="$BUDGET" \
    --window-size="${size/x/,}" \
    --force-device-scale-factor=1 \
    --hide-scrollbars \
    --no-first-run --no-default-browser-check \
    --user-data-dir="$PROFILE" \
    --screenshot="$out" \
    "$url" >/dev/null 2>&1 &
  local cpid=$! waited=0 prev=-1 now=0
  while [ "$waited" -lt "$HARD_TIMEOUT" ]; do
    sleep 1; waited=$((waited + 1))
    now=$([ -f "$out" ] && stat -f%z "$out" || echo 0)
    # 连续两秒字节数相同且非空 → PNG 已写完
    if [ "$now" -gt 2000 ] && [ "$now" = "$prev" ]; then break; fi
    prev="$now"
  done
  kill -9 "$cpid" 2>/dev/null
  pkill -9 -f "user-data-dir=$PROFILE" 2>/dev/null

  if [ -s "$out" ]; then
    printf '%-34s %8s B  %2ss  %s\n' "$name.png" "$(stat -f%z "$out")" "$waited" "$url"
    return 0
  fi
  printf '%-34s %8s    %2ss  TIMEOUT/EMPTY  %s\n' "$name.png" "-" "$waited" "$url"
  return 1
}

fail=0
for spec in "${SPECS[@]}"; do
  IFS=':' read -r name size label <<<"$spec"
  shoot "$name" "$size" "${label:-}" || fail=$((fail + 1))
done

echo "---- 失败/空图：$fail / ${#SPECS[@]} ----"
exit $((fail > 0))

#!/usr/bin/env bash
# 用固定假数据量「内容」列的布局，前后两次跑只差被测产物本身。
#
# 为什么不用 run-capture.sh：那条通道要真实会话（凭据 + 10 分钟有效期），
# 量布局却不需要真数据 —— 变量越多越说不清是谁造成的差异。
# 本脚本走 csp-probe-proxy.py --stub，**不接触任何凭据**。
#
# 用法：
#   bash measure-stub.sh <静态根> <输出目录> <标签> [视口...]
# 例：
#   bash measure-stub.sh /tmp/wt055-before /tmp/wt055-m before 1280x800
set -uo pipefail
set +m

TOOLS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STUB="$TOOLS/stub-contentpool.json"
CSP_FILE="${CSP_FILE:-/Users/aqiuye/Develop/workspace/wt-media/wt-media-desktop/src-tauri/tauri.conf.json}"

ROOT="${1:?用法: measure-stub.sh <静态根> <输出目录> <标签> [视口...]}"
OUT_DIR="${2:?}"
LABEL="${3:?}"
shift 3
VIEWPORTS=("$@")
[ "${#VIEWPORTS[@]}" -eq 0 ] && VIEWPORTS=("1280x800")

[ -d "$ROOT" ] || { echo "静态根不存在：$ROOT" >&2; exit 1; }
[ -f "$ROOT/index.html" ] || { echo "静态根缺少 index.html（打包产物可能叫 index.desktop.html，需复制）" >&2; exit 1; }

mkdir -p "$OUT_DIR"
# 注意：BSD mktemp 要求 X 出现在模板末尾，写成 foo-XXXXXX.log 会失败并返回字面量。
LOG="/tmp/wt055-stub-$$.log"
: > "$LOG"

cleanup() { pkill -f "csp-probe-proxy.py" 2>/dev/null; }
trap cleanup EXIT

pkill -f "csp-probe-proxy.py" 2>/dev/null; sleep 1
nohup python3 "$TOOLS/csp-probe-proxy.py" "$ROOT" --csp-file "$CSP_FILE" --stub "$STUB" \
  > "$LOG" 2>&1 &
sleep 3
grep -q "CSP in effect" "$LOG" || { echo "模拟台未就绪" >&2; cat "$LOG"; exit 1; }
grep -E "CSP in effect|static root|data mode" "$LOG"

SPECS=()
for vp in "${VIEWPORTS[@]}"; do
  SPECS+=("${LABEL}-${vp}:${vp}:${LABEL}-${vp}")
done

echo "---- 抓图 ----"
BASE="http://127.0.0.1:5174" bash "$TOOLS/capture.sh" "$OUT_DIR" "${SPECS[@]}"
rc=$?

echo "---- 探针读数 ----"
grep "^PROBE " "$LOG" | sed 's/^PROBE //' | python3 -c '
import json, sys
for line in sys.stdin:
    line = line.strip()
    if not line: continue
    label, _, raw = line.partition(" ")
    try: d = json.loads(raw)
    except Exception as e:
        print("%s 解析失败: %s" % (label, e)); continue
    print("== %s ==" % label)
    if not d.get("ok"):
        print("  探针失败:", d.get("error")); continue
    print("  视口:", d["viewport"])
    # 封面是否真的加载成功：close-loop 用。若 failed>0，说明这一跑并不等价于
    # 用户「封面正常显示」的情形，读数不能拿来当反证。
    im = d.get("img") or {}
    print("  封面: total=%s loaded=%s failed=%s pending=%s src=%s"
          % (im.get("total"), im.get("loaded"), im.get("failed"), im.get("pending"), im.get("sampleSrc")))
    c = d.get("content") or {}
    print("  滚动容器: client=%s scroll=%s overflowX=%s" % (c.get("clientWidth"), c.get("scrollWidth"), c.get("overflowX")))
    it = d.get("innerTable") or {}
    print("  内层表宽:", it.get("styleWidth"))
    for h in (d.get("header") or []):
        if h.get("text") in ("内容", "发布时间", "发现时间", "修改时间", "操作", "来源"):
            print("  表头[%s] w=%s" % (h["text"], h["r"]["width"]))
    p = d.get("row0TitleParts") or {}
    if p:
        print("  .title-cell w=%s" % (p["cell"] or {}).get("width"))
        print("  .title-media w=%s" % (p["media"] or {}).get("width"))
        print("  .title-copy  w=%s h=%s  <-- 关键" % ((p["copy"] or {}).get("width"), (p["copy"] or {}).get("height")))
        print("  标题元素     w=%s h=%s" % ((p["first"] or {}).get("width"), (p["first"] or {}).get("height")))
        print("  platform_id  w=%s h=%s" % ((p["small"] or {}).get("width"), (p["small"] or {}).get("height")))
    tp = d.get("row0Cells") or []
    print("  各 td 宽:", [x["w"] for x in tp])
    print("  行高:", d.get("rows"))
    # 竖排计数块：定列宽用。列宽下界 = 最宽项 need + 左右内边距。
    ms = d.get("metricSamples") or []
    if ms:
        mf = d.get("metricFont") or {}
        mc = d.get("metricCell") or {}
        print("  计数块字体: 标签 %s / 数值 %s, gap=%s" % (mf.get("label"), mf.get("value"), mf.get("gap")))
        for s in ms:
            print("    %-6s %-10s 标签%3s + 数值%3s = %3s" % (s["label"], s["value"], s["labelW"], s["valueW"], s["need"]))
        print("  最宽项 need =", max(s["need"] for s in ms))
        print("  当前所在 td: w=%s padding=%s/%s listW=%s" % (mc.get("w"), mc.get("padLeft"), mc.get("padRight"), mc.get("listW")))
'
echo "---- 日志：$LOG ----"
exit $rc

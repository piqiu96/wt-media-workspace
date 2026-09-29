#!/usr/bin/env bash
# ============================================================
# build-desktop-frontend.sh — 联合构建 Desktop 前端并复制到 Desktop 仓库
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE_DIR="$SCRIPT_DIR/.."
CLOUD_WEB_DIR="$WORKSPACE_DIR/../wt-media-cloud/web"
DESKTOP_DIR="$WORKSPACE_DIR/../wt-media-desktop"
GENERATED_DIR="$DESKTOP_DIR/.generated/frontend"

echo "=== 1. 清理旧的构建产物 ==="
rm -rf "$GENERATED_DIR"
mkdir -p "$GENERATED_DIR"

echo "=== 2. 构建 Desktop 前端 ==="
cd "$CLOUD_WEB_DIR"
npm run build:desktop

echo "=== 3. 复制构建产物到 Desktop ==="
cp -r "$CLOUD_WEB_DIR/dist-desktop/"* "$GENERATED_DIR/"
if [[ -f "$GENERATED_DIR/index.desktop.html" ]]; then
  cp "$GENERATED_DIR/index.desktop.html" "$GENERATED_DIR/index.html"
fi
rm -rf "$CLOUD_WEB_DIR/dist-desktop"

echo "=== 4. 记录前端构建版本 ==="
# 前端构建版本是五类版本之一，而它必须由这里记录：只有本脚本知道这份产物出自
# wt-media-cloud/web 的哪一次提交（Desktop 仓里没有 package.json，也看不到来源仓）。
# release-versions.sh 会把「包版本 + 来源提交 [+ .dirty]」与产物自身的摘要写进
# $GENERATED_DIR/frontend-build.json；Desktop 的发布闸门随后校验该摘要仍描述这棵树，
# 否则拒绝发布（见 wt-media-desktop/scripts/release-versions.sh 与 tests/README.md）。
bash "$DESKTOP_DIR/scripts/release-versions.sh" --stamp-frontend "$GENERATED_DIR"

echo "=== 5. 验证 ==="
echo "  Desktop 前端文件数: $(find "$GENERATED_DIR" -type f | wc -l)"
test -s "$GENERATED_DIR/index.html"
echo "  index.html: $(wc -c < "$GENERATED_DIR/index.html") bytes"

echo ""
echo "=== Desktop 前端构建完成 ==="
echo "  运行 cd $DESKTOP_DIR && cargo tauri build 以打包"

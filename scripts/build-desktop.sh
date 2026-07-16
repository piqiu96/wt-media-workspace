#!/usr/bin/env bash
# ============================================================
# build-desktop.sh — 联合构建 Desktop 前端并复制到 Desktop 仓库
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
rm -rf "$CLOUD_WEB_DIR/dist-desktop"

echo "=== 4. 验证 ==="
echo "  Desktop 前端文件数: $(find "$GENERATED_DIR" -type f | wc -l)"
echo "  index.html: $(wc -c < "$GENERATED_DIR/index.desktop.html") bytes"

echo ""
echo "=== Desktop 前端构建完成 ==="
echo "  运行 cd $DESKTOP_DIR && cargo tauri build 以打包"

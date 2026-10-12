# Checkpoint: CHG-20260930-070

- CHG: `CHG-20260930-070`（内容池交互对齐前端交互规范）
- Level: S
- Updated: 2026-10-12

## 状态

`VERIFYING`

## Completed

- 内容池行操作按 `pending / material_created / ignored` 展示，详情和跨对象跳转文案统一为“详情 / 素材详情”。
- 选中内容后显示数量和批量操作，未选中时隐藏。素材详情跳转不再触发当前页的重复加载。
- 定向测试 18/18 通过；全量前端测试 506/506 通过；Cloud 和 Desktop 前端构建均通过。确定性环境脚本已按最新源码重新运行，新 DMG 已启动。CHG 范围代码已在 Cloud 独立提交 `8d2247e`。

## Current

代码、自动验证和本地打包完成，Desktop 已启动，等待用户走查页面。

## Next

1. 记录用户在 Desktop 内容池的走查结果；签收后关闭 CHG。

## Blocked

- 无代码阻塞；用户视觉走查尚未完成。

## Recent verification

| 判据 | 读数 |
| --- | --- |
| `ContentPoolPage.test.js` | 18/18 PASS |
| `npm test` | 55 文件、506/506 PASS |
| `npm run build:cloud` | exit 0 |
| `npm run build:desktop` | exit 0 |
| `git diff --check` | exit 0 |
| `scripts/m2b-local-acceptance.sh all --force-restart` | exit 0；Cloud、Agent、Worker、BitBrowser、Web/ Desktop dev server、Desktop assets、DMG、登录 smoke 全部 PASS；新包已启动 |

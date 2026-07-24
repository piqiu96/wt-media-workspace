# Profile Diff 操作确认修复

## 时间

2026-07-24 18:48:20 +0800

## 背景

人工验收反馈：Desktop 浏览器窗口页面中点击“接受本地变化”没有明显反应。

## 修复

- 将“接受本地变化”从浏览器原生 `confirm()` 改为页面内 `t-dialog` 确认弹窗；
- 将“恢复Cloud配置并读回验证”同步改为页面内 `t-dialog` 确认弹窗；
- 保留原业务语义：接受本地变化只更新 Cloud 窗口镜像允许字段，不覆盖授权用户、媒体账号绑定、游戏、标签、备注、Cookie 和业务状态；
- 保留原业务语义：恢复 Cloud 配置只把 Cloud 已保存窗口配置写回本机 BitBrowser 并读回验证，不写入账号、Cookie、授权用户或业务状态。

## 验证

- `npm --prefix web test -- --run profileBindings localAgentStatus`：PASS，5 tests；
- `npm --prefix web run build:desktop`：PASS。

## 结论

当前 Diff 操作不再依赖 Desktop/Tauri 中不可靠的浏览器原生确认框。人工验收时点击“接受本地变化”应先出现页面内确认弹窗，点击“确认接受”后再执行 Cloud 镜像更新。

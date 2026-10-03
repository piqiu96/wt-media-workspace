# GitHub RC 打包试跑记录

## 候选 v0.1.0-rc.1

- Workspace Run：[37082431936](https://github.com/piqiu96/wt-media-workspace/actions/runs/37082431936)，结论：失败，未创建 Pre-release。
- 固定来源：Workspace `c7888d3`；Cloud `61bd43f`（`v0.1.0-rc.1`）；Agent `b0ab365`（`v0.2.2-rc.1`）；Desktop `50f707a`（`v0.1.0-rc.1`）。
- 通过：Manifest 与三仓只读拉取；macOS ARM、Intel 的原生 Agent Sidecar 构建及健康检查。
- 失败 1：Cloud Linux 构建设置 `CGO_ENABLED=0` 时，Go 1.26 链接 sonic/loader 报 `invalid reference to runtime.lastmoduledatap`。修复为与已通过的 Cloud 主干 CI 一致的 Linux 原生工具链；提交 `de9da96`。
- 失败 2：Windows Agent 冻结进程已返回 `healthz ok`，但 PyInstaller 子进程仍持有临时 `agent.log`，烟测清理触发 `WinError 32`。修复为清理整棵 Windows 进程树并容忍临时目录解锁延迟；提交 `ac7f0b6`。
- 其余 Desktop、汇总、发布 Job 因门禁跳过。未验证线上 Cloud、BitBrowser、账号操作或宝塔部署。

## 候选 v0.1.0-rc.2

- 待运行。Cloud、Agent 使用新组件 Tag；Desktop 沿用未改动的组件 Tag `v0.1.0-rc.1`。

# GitHub RC 打包试跑记录

## 候选 v0.1.0-rc.1

- Workspace Run：[37082431936](https://github.com/piqiu96/wt-media-workspace/actions/runs/37082431936)，结论：失败，未创建 Pre-release。
- 固定来源：Workspace `c7888d3`；Cloud `61bd43f`（`v0.1.0-rc.1`）；Agent `b0ab365`（`v0.2.2-rc.1`）；Desktop `50f707a`（`v0.1.0-rc.1`）。
- 通过：Manifest 与三仓只读拉取；macOS ARM、Intel 的原生 Agent Sidecar 构建及健康检查。
- 失败 1：Cloud Linux 链接 sonic/loader 报 `invalid reference to runtime.lastmoduledatap`。首轮以为由 `CGO_ENABLED=0` 引起，先去掉该设置（`de9da96`）；第二轮仍复现，证明它不是充分原因。随后核对 Runner 日志，发现发布工作流根据 `go.mod` 的最低语言版本选择了 **Go 1.24.0**，而已通过的 Cloud 主干 CI 使用 **Go 1.26.5**。发布工作流已改为与主干一致的 1.26.5，Cloud 主干也改为运行发布构建入口（`ed5a3c9`）。
- 失败 2：Windows Agent 冻结进程已返回 `healthz ok`，但 PyInstaller 子进程仍持有临时 `agent.log`，烟测清理触发 `WinError 32`。修复为清理整棵 Windows 进程树并容忍临时目录解锁延迟；提交 `ac7f0b6`。
- 其余 Desktop、汇总、发布 Job 因门禁跳过。未验证线上 Cloud、BitBrowser、账号操作或宝塔部署。

## 候选 v0.1.0-rc.2

- Workspace Run：[37083197026](https://github.com/piqiu96/wt-media-workspace/actions/runs/37083197026)，结论：失败，未创建 Pre-release。
- 通过：Manifest/跨仓读取；Windows、macOS Intel、macOS ARM 的 Agent 原生构建与健康检查。Windows 临时日志清理问题已解决。
- 失败：Cloud Linux 仍用 Go 1.24.0 链接失败，确认与 `CGO_ENABLED=0` 是否启用无关。Desktop、汇总、发布继续按门禁跳过。

## 候选 v0.1.0-rc.3

- 输入：Cloud `v0.1.0-rc.3`；Agent `v0.2.2-rc.2`；Desktop `v0.1.0-rc.1`。

- Workspace Run：[37083857785](https://github.com/piqiu96/wt-media-workspace/actions/runs/37083857785)，结论：失败，未创建 Pre-release。
- 固定来源：Workspace `d961aa9`；Cloud `ed5a3c9`（`v0.1.0-rc.3`）；Agent `ac7f0b6`（`v0.2.2-rc.2`）；Desktop `50f707a`（`v0.1.0-rc.1`）。
- 通过：Manifest/跨仓读取；Cloud Linux 包和 Desktop Web；Windows/macOS Intel/macOS ARM Agent Sidecar 与健康 smoke；macOS ARM 和 macOS Intel Desktop 包。
- 失败：Windows Desktop 编译到应用本体时报 3 个 Rust 错误。根因是 `rustix::process` 与 `Errno::XDEV/PERM` 属 Unix API，但源码未按 Windows 配置；Windows Runner 上这些路径不可用。失败 Job：<https://github.com/piqiu96/wt-media-workspace/actions/runs/37083857785/job/111090751159>。
- 后续：`package`、`publish-pre` 因门禁跳过；准备在 Desktop 用平台分支修复 Unix 进程信号/跨盘错误处理并用 Win32 查询进程存活，再以新组件 Tag 与产品 RC Tag 重跑整组。

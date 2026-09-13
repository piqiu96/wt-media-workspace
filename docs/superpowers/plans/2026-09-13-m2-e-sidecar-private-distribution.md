# M2-E：打包 Local Agent Sidecar 与私有分发计划

## 当前事实

- M2-C 已完成 Cloud、Agent、BitBrowser 的真实写回/读回自测，等待与 M2-E 合并人工验收。
- Desktop release 会优先尝试 `wt-media-agent` sidecar，但当前配置没有 `externalBin`，且失败后会依赖客户电脑的 `python3 -m wt_media_agent.local_main`；DMG 因而不具备独立交付能力。
- 现有 DMG 使用 `--no-sign` 构建，macOS 可能将签名不完整的 App 显示为“已损坏”。不购买证书时，ad-hoc 签名可以避免该损坏类错误；Gatekeeper 的“未知开发者”首次放行仍是 macOS 的系统行为。

## 目标

一份 macOS 私有分发 DMG 自带当前版本的 Local Agent；release 不回退到系统 Python；Tauri 负责启动、停止和本机桥接。构建记录 Sidecar 版本与 SHA-256，且不覆盖用户 Agent 数据目录。

## 不包含

- M2-D Cookie、验证码、上号；
- Windows 安装包发布或跨平台交叉编译（仅在脚本与说明中明确 Windows x64 的原生构建要求）；
- 为绕过 Gatekeeper、隔离或企业安全策略而规避 macOS 保护。

## 实施顺序

1. Agent 提供专用于 Local API 的可冻结入口，并用 PyInstaller 构建原生 Sidecar、输出版本/哈希清单。
2. Desktop 构建脚本将当前平台 Sidecar 放入 Tauri `externalBin` 约定位置；Tauri release 禁止 Python fallback，开发态保留明确 fallback。
3. 配置 macOS ad-hoc 签名与 release 校验，生成可私下发送的 DMG；验收完整签名、Sidecar 自启动、健康状态、停止和用户数据目录不被覆盖。
4. 在 M2-E 其余现有环境状态/恢复功能上做一次真实 Desktop 综合验收，再进入 M2 统一人工验收。

## 验收

- 自动：Agent 测试、Desktop Rust 测试、打包脚本/配置源测试。
- 真实：新启动 Desktop 只从包内 Sidecar 启动 Agent；关闭 Desktop 后 Agent 停止；DMG 具备 ad-hoc 完整签名；数据目录在重装后保留。
- 人工：在另一台未安装 Python 的 macOS 上安装；首次 Gatekeeper 放行遵循系统流程，不将其误报为“已损坏”。

# CHG-20260913-035：M2-E 打包 Local Agent Sidecar 与私有分发收口

> 日期：2026-09-13
> 状态：ACTIVE
> 所属 Milestone：M2-E Desktop本地执行投影与安全收口闭环
> 关联闭环：`delivery/milestones/M2-account-runtime.md#M2-E Desktop本地执行投影与安全收口闭环`
> 当前仓库：`wt-media-workspace`
> 预计影响仓库：`wt-media-cloud`、`wt-media-agent`、`wt-media-desktop`、`wt-media-workspace`

## 1. 用户可见目标

用户收到私下发送的 macOS DMG 后，Desktop 可从包内启动 Local Agent，不依赖客户电脑预装 Python；没有开发者证书时 App 使用 ad-hoc 完整签名，避免被 macOS 误判为“已损坏”。

## 2. 范围

### 包含

- Local Agent 的可冻结 Local API Sidecar 入口与原生构建脚本；
- 当前 macOS 架构 Sidecar 写入 Tauri `externalBin`，版本与 SHA-256 构建清单；
- release 仅允许包内 Sidecar 启动；Python fallback 只允许开发构建；
- 移除 Vue 直连 Local Agent 端口及对应 CSP 例外；非 Tauri 环境只使用 mock，Desktop 一律经 Rust invoke；
- macOS ad-hoc 签名、DMG 构建和可验证的发布前检查；
- Sidecar 生命周期、数据目录保留和安全桥边界的自动/本机验收。

### 不包含

- M2-D 的 Cookie、接码、验证码或上号；
- 绕过 Gatekeeper/隔离标记/企业安全策略；
- 当前 macOS 主机无法生成的 Windows 发行包；Windows x64 Sidecar 名称和原生构建要求已写入脚本与文档，实际安装包需在 Windows 原生机器执行；
- 重建 Profile、代理、账号或任务业务页面。

## 3. 关键规则

- Vue 不直接得到 Agent 端口、Token 或可执行文件路径；Rust 保持唯一系统桥。
- release 无 Sidecar 时必须报出可理解的启动失败，绝不静默回退到客户电脑 Python。
- Agent 用户数据目录只能由 Agent 自己创建/迁移，打包与升级不得清空或覆盖。
- macOS ad-hoc 签名不等于 Apple 开发者证书；首次“未知开发者”放行按系统流程处理，但不得出现“已损坏”类签名错误。
- macOS Apple Silicon 与 Intel 以各自原生 Sidecar 产物构建；Windows x64 仅允许在 Windows 原生环境构建，不跨平台伪造。

## 4. 任务

1. Agent Sidecar 入口、原生构建脚本和版本/哈希清单。
2. Desktop 外置二进制配置、release 启动边界与开发 fallback 分离，并收紧 Vue—Agent 通信边界。
3. macOS ad-hoc 签名和 DMG 构建/发布前校验。
4. 自动测试和本机真实打包验收：启动、健康、停止、数据目录保留。

## 5. 验收标准

- release Desktop 从包内 Sidecar 启动 Local Agent，系统 Python 不存在也不影响；
- Sidecar 版本、目标三元组和 SHA-256 均可从构建清单核验；
- macOS ARM64 / Intel Sidecar 处理明确，Windows x64 原生构建要求明确；
- DMG 内 App 的签名完整，用户数据目录不被构建或升级覆盖；
- Rust 测试、Agent 测试和发布前源检查通过；真实本机包完成启动/健康/停止。

## 6. Evidence

记录构建命令、Sidecar 版本/哈希、目标平台、签名检查、启动/健康/停止、数据目录保留，以及无法替代的另一台机器人工安装步骤。

## 7. Checkpoint

- Completed：Agent frozen sidecar 入口、原生目标构建与版本/SHA-256 清单；Desktop `externalBin`、release 禁止 Python fallback、开发 fallback 显式 opt-in、macOS ad-hoc 签名和 DMG 校验脚本；Cloud Web 已移除直连 `127.0.0.1:8765`，Desktop 统一经 Rust invoke 启动 Agent。
- Completed verification：Desktop Rust 11/11；Cloud Web local-agent boundary/status/service 10/10；Agent sidecar/解绑定向测试 5/5；Agent frozen sidecar 本机 `/healthz`、停止通过；已构建的 macOS ARM64 DMG 内 App `codesign --verify --deep --strict` 通过。
- Completed：清理旧的 `dist-*`、`.generated`、Sidecar 和 Desktop `target` 产物；使用 Python 3.12.13 构建 Agent Sidecar；先构建 App、修复 Sidecar 普通 ad-hoc 签名、再制作 DMG，解决 macOS 26 的 `libpython` Team ID 加载冲突。
- Completed verification：最终 DMG 签名 `codesign --verify --deep --strict` 通过；直接启动最终 DMG 内 Sidecar 的 `/healthz` 通过；直接启动最终 DMG 内 `WT Media.app` 后，包内 Sidecar 自动监听 `8765`；Cloud `18080` 与 BitBrowser `54345` 可达。
- Current：macOS ARM64 可安装包已生成并保持挂载运行，等待用户执行 M2 综合人工验收；Windows x64 安装包仍受当前 macOS 缺少 Windows 原生/交叉安装器工具链阻塞。
- Next：用户先验收 macOS DMG；如需 Windows 包，在 Windows x64 原生机器执行项目发布命令生成 NSIS/MSI，再回填 release matrix。
- Blockers：当前机器无 Windows target linker、NSIS、WiX、MinGW、zig 或 cargo-xwin，不能诚实生成 Windows 可安装包。真实供应商代理的出口、鉴权和区域能力仍需用户人工验收；本 CHG 不绕过 Gatekeeper，也不实现证书认证。

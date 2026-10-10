# Decision 0020: Tag 驱动发布与环境配置边界

## Status

Accepted（2026-10-03；用户确认 RC / 正式 Tag 规则及 GitHub 预发布试跑）

## Context

此前本地验收包把 Cloud 视为同机 `127.0.0.1:18080`。首次线上部署改为宝塔上的 Cloud，Desktop/Agent 出货配置必须指向相应环境的公网服务地址，且同一产品版本的四仓来源可追溯。旧的 `config_online` 规则仍只说明替换动作，不能表达不同环境的成品地址。

## Decision

1. Workspace 产品 Tag 是发布触发器。`vX.Y.Z-rc.N` 走 GitHub Pre-release，`vX.Y.Z` 先走 Draft Release；PR/分支 CI 不创建 Release。两种发布共用 `build → verify → package`，仅发布状态不同。
2. 产品 Tag 对应的简版 Release Manifest 固定 Cloud、Agent、Desktop 组件 Tag、目标环境、非敏感 Cloud origin 和目标平台。Tag 只是入口；构建前校验 Manifest，构建后核对包内地址、CSP、版本和摘要。正式包从正式 Tag 重新构建，不能把 RC 包改名。
3. Desktop 与 Agent 的 Cloud origin 是**打包输入**：RC 使用预发布地址，正式版使用生产地址。用户机器上的 Agent API 与 BitBrowser API 仍只走 loopback。没有预发布 Cloud 时可以明确标记不可连接测试地址，但打包试跑不能宣称联网链路通过。
4. Cloud 的数据库、对象存储和平台凭据只在服务器受控配置提供，不写入 Manifest、GitHub Artifact 或客户端。Cloud 运行时仍只读 `config/`；部署时注入该环境的配置。FFmpeg/FFprobe 只进入 Cloud `bin/`，记录来源、许可证和 SHA-256。
5. 组件仓只维护本仓构建/运行代码，不在运行时依赖 Workspace。Workspace 负责联合构建与版本清单；私有跨仓读取使用最小权限凭据。

## Consequences

- 旧本地发布配置中的 Cloud loopback 值只代表本地验收，不再是线上 Desktop/Agent 成品的固定地址。本决策在这点上取代 ADR-0016 中与本地 Cloud 地址绑定的发布解释；ADR-0016 的运行时配置加载和 Sidecar 目录规则继续有效。
- 首次 RC 打包试跑只验证 GitHub 制品链。宝塔部署、真实登录和对象存储连接另行验收。

## Revision 2026-10-11：正式版改为 CI 自动公开

Decision 第 1 条中「`vX.Y.Z` 先走 Draft Release」的人工公开门禁自本日起作废：`publish-release` job 在 `publish.sh stable` 建草稿并复验资产名与 SHA256 之后，由 CI 直接 `gh release edit --draft=false --prerelease=false` 公开并回读断言状态。用户裁定取消人工环节；安全底线由 `submit_tag.py --verify` 的自动核验（六资产精确集合、SHA256SUMS、build-info 版本一致）与 `publish.sh` 上传复验承担，官网下载按钮跟随 Cloud 部署、公开时序不影响用户。RC 通道（Pre-release）行为不变。v0.1.1 及之前的正式版 Release 仍由当时的人工流程公开。

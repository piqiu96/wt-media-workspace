# ADR-0016：Agent 运行时分层的目录、依赖与配置边界

- Status: Accepted
- Date: 2026-09-23
- Scope: `wt-media-agent` 的包目录、分层职责、依赖方向、配置目录约定与健康检查端点
- Supersedes: 架构基线 §5.2「推荐目录」、§5.4「分层关系」、§5.5「平台目录」；修正 §2.2 Cloud Agent 职责中与 ADR-0015 冲突的条目。不改变 M2 对外执行能力、Cloud-Agent Contract 语义与任何既有业务行为。

## Context

`wt-media-agent` 的功能代码可运行，但不具备长期部署与迭代形态。核查确认四类问题：

1. **没有真实启动闭环。** `config.py` 的 `AgentConfig` 与 `log_setup.py` 的 `configure_logging` 无任何调用者；`runner.py` 的 `TaskRunner`（领取→执行→checkpoint→离线补报）实现完整且有测试，但没有任何进程入口启动它；`wt-media-local-agent` / `wt-media-cloud-agent` 两个 console script 只打印 scaffold 后返回 0。实际对外服务的只有 `wt-media-local-health`。
2. **`runtimes/` 命名不准确。** 该目录装的是 BitBrowser、CDP 与环境探测——均为外部运行环境能力，不是 Agent 自身的 Runtime。架构基线 §5.4 把 Runtime 定义为「文件、FFmpeg、浏览器、比特浏览器、子进程、下载和对象存储」，与 `runtime` 一词在 Agent 自身能力上的通常含义冲突。
3. **边界不清。** executors 各自 `os.getenv` 拼接 `BitBrowserClient`（5 处重复）；executor 直接调用私有 `_post`；平台身份识别（B站/百家号）与代理解析全部内联在 834 行的 `local_api/server.py`。
4. **占位包与基线漂移。** `adapters/`（M3 移除 discovery 后已空）、`modes/`、`generated/` 均只有一行 docstring；§5.5 规定的 `platforms/` 目录在实现中并不存在，平台逻辑实际内联在 Local API 层。§2.2 仍把「抖音关键词和作者监控」记为 Cloud Agent 职责，与 ADR-0015 已确立的 Cloud-owned 执行冲突。

## Decision

1. **分层方向（替代 §5.4）。** 依赖只能自上而下：`bootstrap → runner → executors → {clients, services, storage}`。`runtime/` 是 Agent 自身的横切能力，被各层引用而不引用任何业务层；`local_api/` 是本机控制面，与 `runner` 平行。
2. **目录职责。**
   - `bootstrap/`：进程装配与生命周期，是唯一生产初始化入口。
   - `runtime/`：config、logging、lifecycle、health、context、version、constants、environment —— 改 Agent 自身能力放这里。
   - `runner/`：任务领取、租约、重试、取消、checkpoint、结果上报。
   - `executors/`：任务类型的执行编排 —— 写业务放这里。
   - `clients/`：外部系统协议（Cloud、BitBrowser、平台身份、代理）—— 调外部系统放这里。
   - `services/`：本机公共能力（浏览器/CDP/Cookie、网络、系统探针）—— 公共能力放这里。
   - `storage/`：SQLite 连接、checkpoint 与迁移。
   - `local_api/`：本机 HTTP/SSE 控制面。
   - `utils/`：只放纯函数（时间、字符串、hash、脱敏），禁止业务 Helper。
3. **依赖规则机器校验。** 允许方向固化为可执行断言，禁止 `clients → executors`、`services → executors`、`utils → 业务层`。`executors/` 不得直接 import `sqlite3` / `subprocess` / `socket` / `http.client` / `urllib` / `requests`；executor 访问外部与存储必须经 clients / services / storage。
4. **撤销 `runtimes/`。** BitBrowser、CDP、平台身份与代理解析按职责拆入 `clients/`（外部系统协议）与 `services/`（本机能力）；环境探测归 `runtime/environment.py`，因为它上报的是 Agent 自身运行环境事实。
5. **撤销 §5.5 的 `platforms/` 目录。** 平台差异放 `clients/<platform>/`。不预先创建未实现的平台目录；`douyin` 发现能力按 ADR-0015 归 Cloud，Agent 侧不建。
6. **配置目录对齐 Cloud。** 仓库根 `config/`（运行时唯一读取的目录）与 `config_online/`（发布替换源，非运行时目录），两目录布局 1:1 镜像；打包时执行 `config_online -> 产物/config`。**运行时代码不得引用 `config_online`**，也不提供在两者之间切换的环境变量或参数。加载器保留仅供测试与打包校验使用的目录接缝（对应 Cloud 的 `LoadFromDir`）。
7. **配置中的密钥允许进入仓库。** `config/` 放开发默认值，`config_online/` 放发布真实值，包括凭据；私有仓库 + 发布时整目录替换即凭据的分发机制，与 Cloud `config_online/credentials/` 同规则。两条边界仍然成立：凭据只随 Agent 侧产物分发，不得进入公开分发物；凭据永不进日志。
8. **配置值优先级为 env > file > default。** 这是与 Cloud 配置包「不读进程环境变量」的有意分歧，理由是脚本、CI 与 Desktop 已依赖既有 `WT_MEDIA_*` 变量。分歧只限值级别；**目录级别仍然只有 `config`**。
9. **运行数据目录遵循 §5.8**，内部再分 `data/`、`logs/`、`versions/`。配置不在数据目录内：它随产物走，不随用户数据走。
10. **健康检查双轨。** `/healthz` 冻结为既有契约路径，不扩字段；新增 `GET /api/v1/health` 返回 Agent 版本、Agent 状态、Cloud 状态、BitBrowser 状态与 Storage 状态。健康检查不得触发对外写请求（含 heartbeat）。
11. **明确不做。** 不引入 DDD、微服务、插件系统、事件总线、DI 容器或 Service Locator。`bootstrap/` 持有的是显式有序组件序列，不是动态注册表。

## Consequences

- **Positive**：新增能力只需增加一个 executor 与一个 client/service，无需改动核心 Runtime 与 bootstrap；依赖方向可被零依赖的 AST 测试机器校验，边界不再靠约定；配置、日志、生命周期、健康检查与版本号真实可达，Cloud 侧任务链路在交付物中可运行。
- **Negative**：与 §5.2 / §5.4 / §5.5 的既有目录描述不一致，必须同步改写这三处；`runtimes/` 与 `platforms/` 两个名称作废，引用它们的文档与 workspace skill 必须一并更新。
- **Follow-up**：`agent-platform-adapter-change` skill 需从 `src/wt_media_agent/platforms` 改指 `clients/<platform>`；`scripts/build_desktop_sidecar.py` 需落地 `config_online -> 产物/config` 并加产物校验；本次重构不改变任何既有 API 契约语义与已有测试含义，`/api/v1/health` 为纯新增路径。
- **已知领先**：Cloud 侧目前没有任何脚本、代码或 Dockerfile 步骤引用 `config_online`（全仓仅命中文档与一条 `LoadFromDir` 测试），替换动作在 Cloud 仍是文档约定。Agent 先落地真实打包步骤与产物校验，两边约定存在漂移风险，需在执行记录中记明 Agent 领先。

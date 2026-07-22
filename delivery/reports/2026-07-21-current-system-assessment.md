# 当前系统功能完成度检测与评估报告

> 评估日期：2026-07-21  
> 评估基线：`delivery/MASTER_IMPLEMENTATION_PLAN.md`、`docs/product`、`docs/engineering`、`docs/contracts` 及三个运行仓库当前 `main` 工作树  
> 结论口径：只有同时具备实现、自动验证、适用真实依赖证据和当前治理记录的能力，才可视为“已完成”；其余分别标为“已实现待验收”或“未实现”。

## 1. 结论摘要

系统已经具备可靠的工程底座和最小任务闭环，但还没有达到可交付的业务运营平台状态。

- **M0 工程基线、M1 Cloud–Agent–Desktop 最小任务闭环**：现有计划记为 `DONE`，本次代码级自动测试未发现回归。
- **M2 用户、账号与运行环境**：仍应保持 `IN_PROGRESS`。原始逐项审查为 **30/64（47%）PASS**；7 月 17 日后的提交新增了若干实现，但没有完成真实依赖、UI 全链路与治理证据复验，不能据此把 M2 标为完成。
- **M3–M10**：未进入实施，核心业务链路（内容发现、素材、合成、发布、互动、统计、产品化交付）没有正式实现。
- **当前总体判断**：平台处于“可开发、可验证部分基础能力”的阶段，而非“可投入运营”的阶段。M2 是唯一合理的当前主线；在 M2 完整退出前不应启动后续里程碑。

## 2. 检测范围与方法

本次为只读审查，未修改运行代码。方法包括：

1. 对照 PRD V2、第三章详细需求、工程架构边界、Contract Map 和总实施计划；
2. 检查 Cloud、Agent、Desktop 的模块、迁移、接口契约、测试和近期提交；
3. 执行当前可在本地运行的自动检测；
4. 将未提交工作树、已实现但尚无真实依赖/人工验收的内容与正式完成项明确分开。

## 3. 自动检测结果

| 范围 | 命令/检查 | 结果 | 评估 |
|---|---|---:|---|
| Cloud 后端 | Go 1.26 `go test ./...` | 通过 | Cloud 的模块级单测可用；代理模块没有测试文件。 |
| Agent | `PYTHONPATH=src python3 -m unittest discover -s tests -v` | 44/44 通过 | 覆盖任务领取/回传、SQLite 检查点、BitBrowser 扫描、Cookie 读写、账号检查和敏感 Profile 锁等单元行为。 |
| Cloud Web | `npm test -- --run` | 8/8 失败 | 相对 API URL 传给 Node 原生 `fetch` 时没有测试基址，三个 API-client 测试文件均失败；M2 不能宣称全量回归通过。 |
| Cloud Web 构建 | `npm run build:cloud` | 通过 | 产物可构建；主 JS gzip 约 371 kB，存在大包警告。 |
| Desktop 前端构建 | `npm run build:desktop` | 通过 | 产物可构建；同样存在大包警告。 |
| Desktop Rust | `cargo test --workspace` | 2/2 通过 | 仅覆盖一次性绑定票据；存在 16 条未使用代码/变量警告。 |
| M2 静态验收脚本 | `scripts/verify_m2_acceptance.py` | 失败（脚本异常） | 脚本仍读取已不存在的 `wt-media-desktop/src/services/local-agent.js`，没有输出可用验收结论。 |
| 产品—计划对齐脚本 | `scripts/verify_product_master_alignment.py` | 失败 | 仍断言 M1 为 `IN_PROGRESS`、M2 为 `NOT_STARTED`，与当前总计划冲突，属于过期规则。 |

上述测试不替代 MySQL、BitBrowser、真实代理、Cookie、Desktop Sidecar 和浏览器人工链路验证；本次没有将 fixture/单测当作真实依赖证据。

## 4. 按里程碑的完成度判断

| 里程碑 | 当前判断 | 已确认能力 | 主要缺口/阻断 |
|---|---|---|---|
| M0 | `DONE`（继承证据） | 四仓库可构建、启动/健康检查基线、迁移和治理骨架。 | 本次未重复完整真实启动演示。 |
| M1 | `DONE`（继承证据） | MySQL 任务、租约、幂等、Agent SQLite 检查点、离线回传、Local API/SSE、Desktop 桥接和敏感 Profile 保护基础。 | 仍需在后续业务任务中持续回归恢复与真实三端链路。 |
| M2 | `IN_PROGRESS` | 用户/会话/角色、媒体账号、Profile 扫描与 Diff、代理 CRUD/文本导入、Cookie 字段与导出、Cookie 读写和账号检查 Agent executor、Dashboard、Desktop Sidecar 启动代码。 | 64 点矩阵未复验；代理/Profile 回读、完整开户三路径、授权穿透、真实 Sidecar 生命周期、真实依赖和三角色 UI 验收均未闭环。 |
| M3 | `NOT_STARTED` | 无正式 `source_content`、策略、抓取任务或抖音入库实现。 | 内容发现到素材入库主链路缺失。 |
| M4 | `NOT_STARTED` | 仅有环境探测中的 FFmpeg 信息。 | 无素材生命周期、领取、合成池、FFmpeg executor、成片模型。 |
| M5 | `NOT_STARTED` | 对象存储仅为占位包。 | 无 Cloud Agent 生产、对象存储闭环、云端成片池与领取。 |
| M6–M7 | `NOT_STARTED` | 仅预留敏感操作类型。 | 无 publication、平台 Adapter、B站/百家号辅助发布或人工提交回填。 |
| M8 | `NOT_STARTED` | 无互动业务模型或 executor。 | 无点赞、收藏、评论及人工接管闭环。 |
| M9 | `NOT_STARTED` | 无统计快照与分析读模型。 | 无采集、看板、导出、对账。 |
| M10 | `NOT_STARTED` | Desktop/Agent 有打包和更新目录骨架。 | 无正式安装、签名公证、升级回滚、备份恢复、诊断和全系统验收。 |

## 5. M2 复核：已实现待验收能力

下列内容来自 2026-07-17 的提交或当前工作树，说明实现已推进，但不改变正式 M2 状态：

- **权限与会话**：Cloud 已有游戏范围判断、单会话失效处理；前端 HTTP 客户端已有 401 跳转；Agent Registry 会拒绝失效会话继续领取任务。
- **账号与 Profile**：Cloud 已有媒体账号、标签、绑定 Profile、Profile 扫描/Diff 等 API 和迁移；Agent 可扫描 BitBrowser 身份与 Profile。确认扫描后“写入 BitBrowser 并读回”的业务闭环仍未证实。
- **代理**：已有 CRUD、文本导入、文件导入、配额与到期扫描相关实现。当前未提交改动把检测结果返回 UI；但检测仍是 Cloud 侧 TCP 拨号，并非 PRD 所要求的 Agent 侧真实代理/浏览器可用性验证，且没有 Profile 分配写入 BitBrowser 后读回。
- **Cookie 与账号检查**：Cloud 已登记 `cookie_read_task`、`cookie_write_task`、`account_check_task`；Agent 有对应 executor 与单测；页面已有 Cookie 导出和开户向导。开户页面仍需证明任务创建、Agent 执行、部分成功、失败精确重试和身份回填的完整链路。
- **Desktop**：Tauri 已有 Sidecar 启动代码，前端有本地 Agent 状态页、Cloud/Desk 双构建。现有 Rust 测试未验证 Sidecar 真实拉起、健康检查、停止与故障恢复，不能消除 M2-E2 风险。

## 6. 架构与交付治理评估

### 符合项

- 代码仓库职责大体符合模块化单体 + 统一 Agent + Tauri 壳的目标边界；Vue 源码集中在 Cloud `web`，Desktop 保留 Rust 本机桥接。
- Cloud 维护业务事实、Agent 维护外部执行、Desktop 不直接读取 SQLite 的边界在现有代码和契约中可见。
- `task_schemas` 已登记 Cookie/账号检查任务类型，且 Agent 对应 executor 已实现；敏感 Profile 许可/串行机制已有单测。

### 风险与不符合项

1. **验收失真风险（高）**：M2 差距矩阵停留在 7 月 16 日，之后实现没有进行逐点复验；两份治理校验脚本又已过期/崩溃。当前无法用自动门禁可靠判定 M2。
2. **端到端证据缺失（高）**：没有当前 active CHG，也没有本轮 M2 的真实 MySQL、BitBrowser、代理、Cookie、Desktop 证据目录；`delivery/LEDGER.md` 为空，与 M2 `IN_PROGRESS` 主线不匹配。
3. **核心运行链路断裂（高）**：代理分配/回读、三种开户、账号检查回填、Sidecar 实际生命周期尚未形成用户可完成的闭环。
4. **前端回归门禁失效（高）**：8 个 API-client 测试全部失败。即使是测试基础设施问题，也会掩盖登录、账号、Profile API 客户端回归。
5. **可维护性与交付风险（中）**：Desktop Rust 有未使用代码告警；Web 主包超过构建建议阈值；`web/dist-*` 构建产物混入当前工作树，增加评审噪声。
6. **后续业务能力尚未开始（高）**：M3–M10 所需的正式领域模型和任务契约基本不存在，不能以 M2 的 executor 预留代码推断后续功能完成。

## 7. 建议与优先级

### P0：先恢复“可信验收”能力

1. 立刻建立一个 active M2 修复/复验 CHG，范围只覆盖现有 M2 代码的复验、测试修复、真实证据和矩阵回写；不要越过 M2 启动 M3。
2. 修复 Web 测试的浏览器基址或在测试中注入 `fetchImpl`，使 8 个 API-client 测试重新成为稳定门禁。
3. 更新 `verify_m2_acceptance.py` 的 Desktop 新路径，并使其在路径缺失时报告错误而非抛出异常；同步更新 `verify_product_master_alignment.py` 对 M1/M2 当前状态和五条闭环计划的断言。
4. 把 7 月 17 日后的提交逐项映射回 64 项矩阵，按“代码、测试、真实依赖、UI、完整跑通”重新判定，禁止仅凭提交标题改为 PASS。

### P1：按 M2-A → B → C → D → E 完成真正闭环

1. **A**：以不同角色和游戏范围执行接口/UI 负向测试，确认权限在全部业务入口穿透；验证失效会话下 Agent 停止领取并安全处理在途任务。
2. **B/C**：完成 Profile/代理的分配、BitBrowser 写入与读回；为扫描字段设置运营字段保护；补齐首次绑定、Diff 恢复和账号检查的 UI/批量结果。
3. **D**：以真实 Profile 和代理跑通批量 Cookie、接码链接、人工验证码三条开户路径，证明部分成功、容量预检、失败精确重试与账号身份回填。
4. **E**：在真实 Tauri 包/开发壳中验证 Sidecar 启动、健康、停止、重启、状态/SSE 和失败提示；将 Dashboard/任务页纳入 Desktop 人工验收。

### P2：为后续里程碑做最小准备，但不提前实现业务

- 在 M2 `DONE` 前，仅完善测试、合同版本和发布矩阵；不要提前创建 M3–M10 的占位业务接口或表。
- M2 完成后，以 M3 的“抖音发现 → source_content → material”单一纵向闭环作为下一张 active CHG，而不是并行铺开合成、发布和统计。

## 8. 重新进入 M2 VERIFYING 的准入条件

满足以下条件后，M2 才可从 `IN_PROGRESS` 进入 `VERIFYING`：

- Cloud、Agent、Web、Desktop 自动测试均通过，且治理脚本与当前架构路径一致；
- 64 项矩阵逐项更新，所有非 PASS 项都有明确处置或仍在范围内的实现；
- 五条 M2 业务闭环全部拥有 UI、API、持久化、Agent（适用时）、真实依赖、异常/恢复和角色权限证据；
- 对真实 MySQL、BitBrowser、代理、Cookie、Desktop 的证据写入 active CHG；
- release matrix、Contract 锁和各仓库独立提交与实际验证版本一致；
- 最后由人工完成三角色、浏览器/Desktop 整体验收，才可标记 `DONE`。

## 9. 主要证据位置

- 总计划：`delivery/MASTER_IMPLEMENTATION_PLAN.md`
- 原始 M2 差距矩阵：`delivery/reports/M2-prd-chapter3-gap-matrix.md`
- M2 五条闭环计划：`delivery/active/M2-PLAN-20260716/plan.md`
- 产品总纲与详细需求：`docs/product/prd/`
- 架构边界：`docs/engineering/architecture/社媒运营平台模块分界分层和通信规约.md`
- Cloud 任务契约：`../wt-media-cloud/contracts/task-schemas/v1/task-schema.openapi.yaml`
- 当前治理门禁：`scripts/verify_m2_acceptance.py`、`scripts/verify_product_master_alignment.py`

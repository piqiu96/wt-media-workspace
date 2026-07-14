# CHG-20260715-001：产品基线与 Master Plan 端到端对齐（中文审阅版）

> 本文是 `change.md` 的中文审阅副本，章节、决策、任务和验收编号与原文件逐项对应。
>
> 本文不构成第二份独立需求源；如两份文件出现差异，以 `change.md` 为执行依据，并将确认后的修改同步回两份文件。

## 1. 基本信息

- 变更级别：L（大型变更）
- 当前状态：实施中（`IMPLEMENTING`）
- 创建日期：2026-07-15
- 当前执行仓库：`wt-media-workspace`
- 受影响仓库：
  - `wt-media-workspace`

## 2. 变更目标

重新对齐当前产品事实、工程事实和 M0-M10 实施路线：

- 把 M0/M1 重新定义为：完成后能够通过真实 Cloud、MySQL、Agent、Desktop 和 Web 端到端人工验收的工程环境；
- 把 M2 按完整的用户、账号、窗口、代理、Cookie、开户、运行环境和权限范围重新规划并重新执行；
- 修正 M3-M10 的对象、依赖、状态和漏项，使后续每个 CHG 都能从唯一产品事实推导并独立验收。

本 CHG 只修订稳定基线、治理映射和实施计划，不实现任何运行时业务功能。

## 3. 基线引用

- 产品基线：
  - `docs/product/prd/社媒运营平台_产品需求说明书_V1.md`
  - `docs/product/prd/详细文档/第一章_项目概述.md`
  - `docs/product/prd/详细文档/第二章_系统架构.md`
  - `docs/product/prd/详细文档/第三章_用户与账号管理.md`
  - `docs/product/prd/详细文档/第四章_内容发现.md`
  - `docs/product/prd/详细文档/第五章_素材生产.md`
  - `docs/product/prd/详细文档/第六章_发布管理.md`
  - `docs/product/prd/详细文档/第七章_互动管理.md`
  - `docs/product/prd/详细文档/第八章_数据统计.md`
- 工程基线：`docs/engineering/architecture/社媒运营平台工程架构与分层设计_V1.md`
- 契约治理：`docs/contracts/contract-map.md`、`config/contract-map.yaml`
- 发布治理：`config/release-matrix.yaml`
- 决策记录：`docs/decisions/0002-bitbrowser-profile-identity-normalization.md`
- 总实施路线：`delivery/MASTER_IMPLEMENTATION_PLAN.md`
- 核查证据：`evidence/baseline-audit-20260715.md`

## 4. 当前事实

- CHG-20260714-020 已完成 M2 C1-C6 的基础能力验收，并取得真实 MySQL 和 BitBrowser 证据；但它没有交付完整的用户与账号产品域。
- M0 和 M1 当前被标记为 `DONE`，但 Desktop 构建和打包仍是脚手架命令，Desktop 入口仍使用模拟 Local Agent 服务，Cloud 的任务和 Agent Registry 仍保存在内存中。
- 当前 M2 计划没有包括第三章要求的完整用户管理 UI、浏览器窗口/Profile 管理、代理管理、Cookie 操作、账号检测和三种开户路径。
- 当前 M3 仍使用 `crawl_result` 和 `content_lead`，但产品基线已将 `source_content` 定义为标准对象，并明确不建设独立 `crawl_result`。
- 当前 M8 仍使用 `interaction_batch` 和 `interaction_item`，但产品基线已明确不将二者作为核心对象建设。
- `tracked_object` 必须在发布成功或录入外部互动目标时创建，不能等到 M9 才首次出现。
- `task_schemas` 当前仍为 `placeholder_only`，真实业务 Executor 依赖它之前必须先形成正式定义。
- 人类可读契约治理文档和生成的 AI 上下文，与当前机器可读事实存在漂移。

## 5. 变更范围

### 5.1 新增

- 一份覆盖全部 P0/P1 需求和明确排除项的“产品能力到里程碑”映射表。
- 修正后的 M0/M1 补救 CHG 和端到端验收门禁。
- 一套重新编号的 M2 执行路线：现有有效代码只有重新验证后才能复用，并最终关闭完整产品、UI 和运行环境范围。
- 修正后的 M3-M10 候选 CHG、依赖门禁、标准对象、真实集成门禁和人工验收要求。
- 针对废弃对象残留及里程碑/契约治理一致性的自动静态检查。

### 5.2 修改

- 综合 PRD 以及详细文档第二章至第八章中仍存在的旧术语和跨章节归属冲突。
- 工程架构中对真实 Desktop、Agent 和任务持久化交付节点描述不清的部分。
- 完整修订 `delivery/MASTER_IMPLEMENTATION_PLAN.md`，包括当前状态、继承证据、候选 CHG、依赖关系和退出条件。
- 人类可读契约映射、机器可读治理说明、发布证据描述和生成的 AI 上下文。

### 5.3 删除

- 从当前产品设计和实施计划中删除以下对象的运行态使用：`content_lead`、独立 `crawl_result`、`interaction_batch`、`interaction_item`、`production_signal`。
- 删除任何将纯脚手架 Desktop 检查或内存任务基础设施描述为“生产级端到端完成”的说法。

历史 Git 证据以及迁移/替换说明表继续保留；这里的删除只针对当前有效的运行设计。

### 5.4 本 CHG 明确不做

- 不实现或修改 Cloud、Agent、Desktop、Web、MySQL Schema、调度器、对象存储、代理、Cookie、发布、互动或打包的运行时行为。
- 不在本对齐 CHG 中把 M0、M1、M2 或任何后续里程碑标记为 `DONE`。
- 在接口提供方尚未发布正式契约前，不激活占位状态的 `task_schemas`。
- 不删除历史提交、Git 历史中的已完成 CHG 证据或有效的 C1-C6 运行时代码。
- 不新增顶层 M11 业务里程碑。

## 6. 已确认决策

| 编号 | 决策 | 状态 |
|---|---|---|
| D-01 | 在 Master Plan 中重新打开 M0/M1。M0 负责建立可独立构建和运行的真实组件；M1 负责完成具有持久化能力、无 Mock、可人工验收的 Cloud-Agent-Desktop-Web 端到端环境。 | 已确认 |
| D-02 | 历史 M0/M1 提交继续作为继承证据，但脚手架检查、echo 构建/打包命令、模拟 Desktop 服务和内存 Registry 不能满足修订后的退出门禁。 | 已确认 |
| D-03 | M2 按新编号重新规划并重新执行。现有 C1-C6 代码可在核查后复用，但历史 PASS 不会自动关闭新的产品级 CHG。 | 已确认 |
| D-04 | 标准内容发现流程为：定时任务使用 `crawl_strategy -> crawl_task`，即时查询不创建定时抓取任务；选中的结果进入 `source_content -> material`。不建设独立 `crawl_result` 或 `content_lead`。 | 已确认 |
| D-05 | 互动流程使用 `tracked_object -> interaction_task -> 账号级 task`；批量选择只是一次操作，不建设 `interaction_batch`，也不建设 `interaction_item`。 | 已确认 |
| D-06 | 不建设 `production_signal`。生产提示和重复风险视图从正式业务事实与 `platform_metric_snapshot` 派生。 | 已确认 |
| D-07 | 一个 Cloud 用户最多绑定一棵 BitBrowser 主账号树；同一个 `main_user_id` 可以由多个 Cloud 用户/运营共享；授权以 Cloud 的 Profile 分配为准，`profile_user_id` 只保留为审计元数据。 | 已确认 |
| D-08 | M6 在获得有效发布成功结果后创建或复用 `tracked_object`；M8 为外部互动目标创建或复用 `tracked_object`；M9 只负责采集和聚合指标。 | 已确认 |
| D-09 | 真实 Desktop/Tauri/Local Agent 集成是 M0/M1 的前置要求，也是更早业务验收的依赖；M10 负责最终安装包、签名、更新、诊断和恢复，而不是到 M10 才首次进行真实 Desktop 集成。 | 已确认 |
| D-10 | 保留 M0-M10 顶层路线；通过修正 CHG 拆分和门禁补齐完整性，不新增 M11。 | 已确认 |

## 7. 待确认问题

无。

## 8. 实施任务

每个任务必须遵循：

```text
先得到失败的验证结果
→ 进行最小范围的基线或计划修正
→ 重新验证
→ 检查 Diff
→ 记录 Evidence
→ 更新 Checkpoint
→ 在 Workspace 仓库独立提交
```

| 任务 | 目标 | 状态 | 验证方式 |
|---|---|---|---|
| T-01 | 激活独立对齐 CHG，并记录已经确认的核查结论与决策。 | 已完成 | 扫描唯一 Active CHG；检查 `evidence/baseline-audit-20260715.md`。 |
| T-02 | 统一产品术语、对象归属和跨章节状态规则。 | 已完成 | 扫描旧对象残留，并进行产品交叉引用检查。 |
| T-03 | 修正真实 Desktop、持久化任务基础设施和正式 Schema 门禁的工程/契约治理说明。 | 已完成 | 检查架构与 Contract Map 一致性。 |
| T-04 | 将 M0/M1 重写为真实组件和端到端环境里程碑，并重置其状态与证据语义。 | 待执行 | 根据当前代码事实核对退出门禁。 |
| T-05 | 用重新编号的完整产品执行路线替换 M2。 | 待执行 | 第三章能力映射中不得存在未覆盖 P0/P1 项。 |
| T-06 | 修正 M3-M10 的流程、对象、依赖、缺失 CHG 和验收门禁。 | 待执行 | 交叉核对第四章至第八章与架构，并扫描禁用对象。 |
| T-07 | 对齐 Ledger、人类/机器可读契约治理、发布描述和生成的 AI 上下文。 | 待执行 | 运行 Workspace 治理脚本并验证唯一 Active CHG。 |
| T-08 | 运行完整 Workspace 回归，记录 Diff/覆盖证据，准备用户审阅和关闭。 | 待执行 | 运行 `verify_m0_config.py`、Workspace 测试、新对齐检查器和 `git diff --check`。 |

## 9. 仓库检查表

### 9.1 `wt-media-workspace`

- [ ] 已统一产品基线术语和对象归属。
- [ ] 已修正工程与契约治理边界。
- [ ] 已将 M0/M1 重置为真实端到端门禁。
- [ ] 已完整重规划并重新编号 M2。
- [ ] 已修正并交叉核对 M3-M10。
- [ ] 已增加静态检查器和证据。
- [ ] 已对齐 Ledger、生成上下文和 Checkpoint。

### 9.2 `wt-media-cloud`

- [x] 本 CHG 不修改；运行时实现延后到后续独立 CHG。

### 9.3 `wt-media-agent`

- [x] 本 CHG 不修改；运行时实现延后到后续独立 CHG。

### 9.4 `wt-media-desktop`

- [x] 本 CHG 不修改；运行时实现延后到后续独立 CHG。

## 10. 验收矩阵

| 编号 | 验收要求 | 验证方式 | 状态 |
|---|---|---|---|
| AC-01 | 只有 CHG-20260715-001 处于 Active；全部已批准决策已经记录，并且没有阻塞问题。 | 扫描 Active 目录、Ledger 和当前上下文。 | 通过 |
| AC-02 | M0/M1 完成必须同时具备真实独立构建能力，以及具有持久化能力、无 Mock 的 Cloud-Agent-Desktop-Web 端到端人工验收环境。 | 使用架构基线复核 Master 退出门禁。 | 待验证 |
| AC-03 | M2 必须包含用户管理、媒体账号、Profile/窗口管理、代理管理、Cookie/账号检测、开户、运行环境绑定、敏感任务保护、UI 和真实验收。 | 使用第三章能力映射核对。 | 待验证 |
| AC-04 | M3-M10 只能使用标准对象，并确保 `tracked_object`、task schemas、调度器、对象存储和 Desktop 等能力在第一个消费者之前交付。 | 跨里程碑依赖和禁用对象扫描。 | 待验证 |
| AC-05 | 产品、工程、契约治理和 Master Plan 对 BitBrowser 主/子账号身份及 Cloud 授权的描述必须一致。 | 扫描 D-07 引用和相关术语。 | 待验证 |
| AC-06 | 每个适用里程碑都必须具有自动测试、真实依赖、UI/人工、恢复/安全和独立提交门禁。 | 里程碑验收映射。 | 待验证 |
| AC-07 | Workspace 自动验证通过，并且 Diff 不包含运行时仓库修改。 | Workspace 完整回归和仓库状态检查。 | 待验证 |

## 11. 证据

- 已有：`evidence/baseline-audit-20260715.md`
- 计划生成：`evidence/product-milestone-crosswalk.md`
- 计划生成：`evidence/verification-summary.md`
- 计划生成：`evidence/diff-summary.md`

Evidence 只记录事实和验证结果；正式需求仍保存在稳定基线和本变更记录中。

## 12. 当前检查点

已完成：

- CHG-020 已按照原 C1-C6 基础范围关闭，并完成各仓库独立提交。
- 用户已经确认 D-01 至 D-10：重新打开 M0/M1、重新规划并执行 M2、统一标准对象并保留 M0-M10 顶层路线。
- 已完成基线核查并创建独立对齐 CHG。
- 已创建与 `change.md` 逐项对应的中文审阅版 `change.zh-CN.md`。
- T-02 已在产品基线中统一 `source_content`、发布取消统计、账号组语义、`tracked_object` 归属以及共享 BitBrowser 主账号树的授权规则。
- T-03 已对齐工程架构、人类可读 Contract Map 和 Release Matrix 规划说明，明确真实 Desktop、任务/Agent 持久化、Scheduler/Object Storage 顺序和正式任务 Schema 门禁。

当前：

- 正在执行 T-04：重建 M0/M1 Master Plan。

下一步：

- 重置 M0/M1 状态语义，并定义真实组件和端到端退出门禁。

阻塞项：

- 无。

最近验证：

- 2026-07-15，CHG-020 最终关闭矩阵在本 CHG 激活前已通过。
- Active CHG 扫描和生成的 AI 上下文均唯一指向 CHG-20260715-001，没有阻塞问题。
- 中文审阅版的 D/T/AC 编号与 `change.md` 保持一一对应。
- 产品旧术语扫描后，废弃对象只保留在明确排除、迁移说明或历史引用语境中。
- `python3 scripts/verify_m0_config.py` 已通过，混合的 active/placeholder 契约状态已得到一致说明。

## 13. 完成门禁

- [ ] 变更范围已全部完成。
- [x] 没有阻塞中的 `Q-xx`。
- [ ] 验收矩阵全部通过。
- [ ] 自动测试通过，或例外已经说明。
- [ ] 需要的人工审阅证据已经记录。
- [ ] Diff 已检查，不存在范围外修改。
- [x] 运行时仓库只在范围明确列出时才允许修改；本 CHG 未修改运行时仓库。
- [ ] 必要的稳定基线已更新。
- [ ] 受影响仓库已独立提交。

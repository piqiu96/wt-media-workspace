# CHG-20260715-008: M1-R1 正式通用 task 模型、状态、错误和 task_schemas

## 1. Basic Information

- Level: M
- Status: IN_PROGRESS
- Created: 2026-07-15
- Current repository: `wt-media-workspace`
- Affected repositories:
  - `wt-media-cloud`
  - `wt-media-agent`
  - `wt-media-desktop`

## 2. Change Goal

在 M0 真实工程组件基础上，建立正式通用 task 模型（状态、错误）、task_schemas 定义和跨仓库兼容版本锁定，为 M1-R2～R8 的持久化、Agent Runner、Desktop 集成和端到端恢复闭环提供类型基础。

本 CHG 只关闭 M1-R1。

## 3. Baseline References

- Master route: `wt-media-workspace/delivery/MASTER_IMPLEMENTATION_PLAN.md`
- M0 closure: Decision 0005, `0.1.0-m0-accepted` release
- Contract map: `wt-media-workspace/config/contract-map.yaml`
- Inherited evidence: CHG-008～CHG-014（Contract 兼容、注册心跳、noop task、Local API/SSE、Desktop 控件、三端脚手架集成）

## 4. Current Facts

- `task_schemas` 当前为 `placeholder_only`，formal_definition = inactive
- Cloud、Agent、Desktop 上已有 noop task 的历史实现，但 task 模型、状态枚举和 task_schemas 仍是占位
- M0 已确认三端可独立构建、启动、停止
- MySQL 本地实例在 `127.0.0.1:3306`，用户 root，库 `wt-media-cloud` 已有表但无 schema_migrations（M0 遗留，本 CHG 需决定处理方式）

## 5. Scope

### Add

- 正式通用 task 模型（Cloud 端）：状态机、错误类型、核心字段
- Cloud 发布 `task_schemas` Contract（正式版本、JSON Schema / Protobuf）
- Agent 端 task schema 兼容版本锁定
- Desktop 端 task schema 引用锁定
- Contract Map 中 `task_schemas` 改为 active

### Modify

- `contract-map.yaml`：task_schemas 状态从 placeholder_only → active
- `release-matrix.yaml`：添加 M1-R1 已验证版本
- 历史 noop task 实现适配新 task 模型（若需要）

### Delete

- 无

### Explicitly Not Doing

- MySQL 持久化（M1-R2）
- Agent Runner 和 SQLite 检查点（M1-R3）
- Local Agent HTTP/SSE 集成（M1-R4）
- Desktop Tauri 进程生命周期管理（M1-R5）
- Cloud Web 登录和任务 UI（M1-R6）
- 端到端中断恢复验证（M1-R7/R8）

## 6. Confirmed Decisions

| ID | Decision | Status |
|---|---|---|
| D-01 | task_schemas 由 Cloud 正式发布，Agent 和 Desktop 锁定兼容版本。 | CONFIRMED |
| D-02 | 已有 `wt-media-cloud` 数据库在本 CHG 中补齐 schema_migrations，保留历史数据。若迁移不兼容则重建隔离库后重新迁移。 | CONFIRMED |
| D-03 | 保留 noop task 作为验证类型的业务 executor，但不扩展为正式 task 业务。 | CONFIRMED |

## 7. Pending Questions

None.

## 8. Implementation Tasks

| Task | Goal | Status | Verification |
|---|---|---|---|
| T-01 | Start Gate for M1-R1. | PENDING | `evidence/start-gate.md`. |
| T-02 | 设计并实现 Cloud 端通用 task 模型（状态机、核心字段、错误类型）。 | PENDING | Go 单元测试 + Contract 测试。 |
| T-03 | Cloud 发布正式 `task_schemas` Contract（JSON Schema / Protobuf）。 | PENDING | Contract 一致性验证。 |
| T-04 | Agent 端锁定 task schema 兼容版本，适配历史 noop task。 | PENDING | Agent 单元测试 + Contract 兼容性端点。 |
| T-05 | Desktop 端锁定 task schema 引用。 | PENDING | `contracts.lock.json` 验证。 |
| T-06 | 更新 `contract-map.yaml`，task_schemas → active。 | PENDING | Workspace 配置检查。 |
| T-07 | 补齐或重建 `wt-media-cloud` 数据库 schema_migrations。 | PENDING | 空库迁移重复验证。 |
| T-08 | 整体验收和 Workspace 提交。 | PENDING | 验收矩阵全部 PASS、Diff 检查、各仓库独立提交。 |

## 9. Repository Checklist

### wt-media-workspace

- [ ] Active CHG and Ledger point to CHG-20260715-008.
- [ ] Master Plan M1 status set to `IN_PROGRESS`.
- [ ] Contract map updated.
- [ ] Decision records written.
- [ ] Workspace commit made.

### wt-media-cloud

- [ ] Task model implemented.
- [ ] task_schemas Contract published.
- [ ] Migration path for `wt-media-cloud` database resolved.

### wt-media-agent

- [ ] task schema version locked.
- [ ] Historical noop task adapted.

### wt-media-desktop

- [ ] task schema reference locked.

## 10. Acceptance Matrix

| AC | Requirement | Verification | Status |
|---|---|---|---|
| AC-01 | 正式 task 模型定义状态机、核心字段、错误类型。 | Go 单元测试 + code review. | PENDING |
| AC-02 | Cloud 发布 `task_schemas` Contract，formal_definition = active。 | Contract Map 一致性验证。 | PENDING |
| AC-03 | Agent 兼容 Cloud 发布的 task schema 版本。 | Contract 兼容性端点。 | PENDING |
| AC-04 | Desktop 锁定 task schema 引用版本。 | `contracts.lock.json` 检查。 | PENDING |
| AC-05 | `contract-map.yaml` 中 task_schemas 为 active。 | Workspace 配置测试。 | PENDING |
| AC-06 | 已有数据库迁移路径可重复验证。 | 空库迁移 + 重复迁移 PASS。 | PENDING |

## 11. Evidence

待记录：
- `evidence/start-gate.md`
- `evidence/cloud-task-model.md`
- `evidence/task-schemas-contract.md`
- `evidence/agent-schema-lock.md`
- `evidence/desktop-schema-lock.md`
- `evidence/database-migration.md`
- `evidence/contract-map-update.md`
- `evidence/verification-summary.md`

## 12. Current Checkpoint

Completed:
- M0 已关闭（M0 → DONE，人工验收通过）。
- M1 已激活（M1 → IN_PROGRESS）。

Current:
- M1-R1 即将开始。

Next:
- 执行 T-01～T-08。

Blocked:
- None.

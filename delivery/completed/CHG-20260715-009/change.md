# CHG-20260715-009: M1-R2 MySQL task、幂等、租约和 Agent Registry 持久化

## 1. Basic Information

- Level: M
- Status: IN_PROGRESS
- Created: 2026-07-15
- Current repository: `wt-media-cloud`
- Affected repositories:
  - `wt-media-cloud`
  - `wt-media-agent`

## 2. Change Goal

将 M1-R1 的正式 task 模型从内存实现迁移到 MySQL 持久化存储，同时将 Agent Registry 从内存实现迁移到 MySQL。确保 task、租约、幂等键和 Agent Registry 在 Cloud 重启后不丢失。

## 3. Baseline References

- Master Plan: `wt-media-workspace/delivery/MASTER_IMPLEMENTATION_PLAN.md`
- M1-R1 task model: Cloud `e2f7687`

## 4. Current Facts

- TaskStore 当前完全在内存中（`map[string]Task` + `sync.Mutex`）
- Agent Registry 完全在内存中（`map[string]AgentNode` + `sync.Mutex`）
- MySQL 连接已在 `internal/infra/database/mysql.go` 中可用
- `internal/modules/migration/runner.go` 可用
- `000_bootstrap_existing.sql` 已创建

## 5. Scope

### Add

- MySQL migration: `006_tasks.sql` — tasks 表（task_id PK、task_type、status、idempotency_key UNIQUE、agent_id、lease_expires_at、progress、message、error_code、created_at、updated_at）
- MySQL migration: `007_agent_registry.sql` — agent_nodes 表（agent_id PK、status、capabilities、registered_at、last_heartbeat_at）
- `MySQLTaskStore` 实现 `TaskStore` 接口
- `MySQLRegistry` 实现 `Registry` 接口

### Modify

- Cloud app.go 初始化使用 MySQL 持久化存储替代内存存储
- Agent Registry 兼容性检查保持

### Delete

- 无

### Explicitly Not Doing

- SQLite Agent 检查点（M1-R3）
- Local Agent HTTP/SSE（M1-R4）
- Desktop Tauri 集成（M1-R5）

## 6. Confirmed Decisions

| ID | Decision | Status |
|---|---|---|
| D-01 | TaskStore 和 Registry 同时保留内存 fallback（MySQL 不可用时降级）。 | CONFIRMED |

## 7. Pending Questions

None.

## 8. Implementation Tasks

| Task | Goal | Status |
|---|---|---|
| T-01 | MySQL migration: tasks 表 | PENDING |
| T-02 | MySQL migration: agent_nodes 表 | PENDING |
| T-03 | MySQLTaskStore 实现 | PENDING |
| T-04 | MySQLRegistry 实现 | PENDING |
| T-05 | app.go 使用 MySQL 持久化 | PENDING |
| T-06 | 测试验证 | PENDING |

## 9. Acceptance Matrix

| AC | Requirement | Status |
|---|---|---|
| AC-01 | tasks 表创建成功，幂等键有 UNIQUE 约束 | PENDING |
| AC-02 | agent_nodes 表创建成功 | PENDING |
| AC-03 | Cloud 重启后 task 和 registry 状态不丢失 | PENDING |
| AC-04 | 所有现有 task API 端点正常工作 | PENDING |

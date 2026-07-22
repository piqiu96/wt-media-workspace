# Task 1：用户领域与真实 MySQL 迁移证据

> 日期：2026-07-22

## 提交

- `d623bcb`：数值用户 ID、三角色、运营分组迁移基础；
- `d16e37d`：新库/旧库 Bootstrap、审计与敏感权限纠偏；
- `9fc4c8a`：迁移安全、权限边界、原子审计与验收缺口收口。

## 自动验证

| 验证 | 实际结果 | 状态 |
|---|---|---|
| `go test ./internal/modules/migration -count=1` | 迁移运行器、Bootstrap 和 M2-A1 迁移结构测试通过 | PASS |
| `go test ./... -count=1` | Cloud 全包通过 | PASS |
| `git diff --check` | 无空白错误 | PASS |

## 真实 MySQL 8.4

| 场景 | 期望 | 实际结果 | 状态 |
|---|---|---|---|
| 全新空库 | 从 0 应用全部迁移 | `13 applied, 13 total` | PASS |
| 已有 001～011 结构但无 Ledger | Bootstrap 识别历史结构，只执行自身与 012 | `2 applied, 13 total`；最终 Ledger 13 条 | PASS |
| 合法旧用户及关联数据 | 用户、游戏范围、会话、审计引用无损迁移 | 用户 2、范围 1、会话 1、审计 1、有效审计 actor 引用 1 | PASS |
| 旧管理员仍带游戏范围 | 在任何 012 持久副作用前阻断 | MySQL `3819`；旧角色、范围行数保持，`operation_teams` 未创建，012 未登记 | PASS |

## 结论

自增 UID、角色迁移和全部已知用户引用具备可重复的新库/旧库迁移路径。危险遗留数据明确失败，不静默删除或伪造修复。

# T-11 过期登录会话清理

日期：2026-10-23
CHG：CHG-20261023-101
Cloud 提交：`146f267`（`chg/CHG-20261023-101`）

## 范围与语义

`user_sessions` 在 068 增加 `expires_at` 后没有任何删除路径，登录只插入、注销只标失效，行会永久增长。本任务新增调度作业 `session-cleanup`：

- 每轮删除 `expires_at < now - session_cleanup_retention` 的行，分批执行；默认间隔 1h、保留 7 天、批量 500。
- 不按 `invalidated_at` 过滤。未过期的失效行保留到过期：被替换的旧 Desktop 需要继续收到 `AUTH_DESKTOP_REPLACED`，提前删除会退化成通用的会话无效。
- 已过期行再保留 7 天作为审计痕迹后删除。
- 同一轮所有批次共用一个 cutoff，边界行留到下一轮。

## 代码与配置

| 位置 | 内容 |
| --- | --- |
| `migrations/20261023_072_user_sessions_expires_at_index.sql` | 新增 `idx_user_sessions_expires_at (expires_at)` |
| `internal/modules/identity/repository/session_cleanup.go` | `DELETE FROM user_sessions WHERE expires_at < ? LIMIT ?` |
| `internal/modules/identity/service/session_cleanup.go` | 透传 |
| `internal/jobs/session_cleanup.go` | 批处理循环、批间取消检查、非正批量拒绝；失败自己记日志（调度器会吞掉作业错误） |
| `internal/bootstrap/jobs.go` | `discovery-scheduler` 进程注册 `session-cleanup` |
| `config/scheduler/scheduler.toml`、`config_online/scheduler/scheduler.toml` | `session_cleanup_interval='1h'`、`session_cleanup_retention='168h'`、`session_cleanup_batch_size=500` |
| `internal/config/config.go` | 三个新键，均须 > 0；本配置系统没有代码级默认值 |

## 测试读数

定向命令：`go test ./internal/jobs/... ./internal/modules/identity/... ./internal/config/... ./internal/infra/database/migration/...` → 全部 `ok`。

覆盖：

- 批处理 2/2/1 → 3 次调用、共 5 行、cutoff 不变；满批后必须确认空批才停；中途报错返回已删数量；批间取消返回 `context.Canceled`；批量 0/-1 不调用删除函数。
- SQL 精确匹配 `DELETE FROM user_sessions WHERE expires_at < ? LIMIT ?`，参数 `(cutoff, 500)`；0 行视为成功；错误透传。
- 配置读取 `1h/168h/500`；三个键分别为 0、负值、0 时启动校验失败。
- 迁移 072 只含 `ALTER TABLE user_sessions ... ADD KEY`；禁止 `DELETE FROM user_sessions`、`DROP`、`CREATE TABLE`、`MODIFY COLUMN`、`ADD COLUMN`。

全量：`./scripts/test.sh` → Go 71 包 `ok`、Web 77 文件 / 710 用例、control 12/12，退出 0。

## 开发库实跑

迁移：`./scripts/migrate.sh` → `migration ok: 1 applied, 74 total`，`applied 20261023_072_user_sessions_expires_at_index`。

读回：

- `schema_migrations`：`20261023_072_user_sessions_expires_at_index`。
- `SHOW INDEX FROM user_sessions WHERE Key_name='idx_user_sessions_expires_at'`：`Non_unique=1`、`Seq_in_index=1`、`Column_name=expires_at`。

清理前后（`NOW(6)`）：

| 项目 | 清理前 | 清理后 |
| --- | --- | --- |
| 总行数 | 675 | 406 |
| 早于 `now - 168h` 可删 | 269 | 0 |
| 保留（不早于 cutoff） | 406 | 406 |
| 其中最近 7 天过期（保留带） | 55 | 55 |
| 有效会话（未失效且未过期） | 12（Desktop 1 / Web 11） | 12（Desktop 1 / Web 11） |

一次性程序 `.cache/t11-cleanup/main.go`（gitignored）：`bootstrap.InitializeMigration()` 后调用 `jobs.RunSessionCleanup(context.Background())`。

- 第一次：输出 `session-cleanup ok`；`logs/job.log` 记录 `session cleanup finished module=jobs.session_cleanup deleted=269 cutoff=2026-10-16T13:33:45Z`。
- 第二次：输出 `session-cleanup ok`，未新增完成日志（删除 0 行时不记），计数保持 406/0/12。

`DELETE ... LIMIT ?` 由真实 MySQL 驱动执行成功，不需要退化为字符串拼接。

## 副作用与边界

- `deleteUser` 的引用计数包含 `user_sessions`。清理后，仅因历史 session 被阻止删除的用户可能变为可删；`audit_logs` 等引用仍会阻止，属预期。
- 当前没有管理端“历史登录记录”页面，清理不改变任何用户可见的当前状态。
- 保留带里的 55 行仍算“已过期”，清理后不会归零。
- 开发环境不启动 `discovery-scheduler`，只验证同一作业函数的一次性调用；常驻 tick 未验证（与 T-10 的 `task-recovery` 相同）。
- 发布顺序：先应用 072，再发布带作业的二进制；`ALTER TABLE ... ADD KEY` 在 MySQL 8 在线执行。

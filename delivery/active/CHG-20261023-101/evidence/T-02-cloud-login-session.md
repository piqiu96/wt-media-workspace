# T-02 Cloud 登录与会话状态证据

日期：2026-10-23
CHG：CHG-20261023-101
Cloud 提交：`0907c40 feat(identity): make user_sessions the single login fact source`

## 范围

- `20261023_068_identity_session_state.sql`：`user_sessions.expires_at`、`invalidated_reason`、活跃会话索引；回填与重复 Desktop 会话收敛。
- `Session` 增加 `ExpiresAt` / `InvalidatedReason`；`LoginOptions` 增加 `ReplaceSessionID`。
- Web 多会话并存；Desktop 同用户单活跃会话，冲突返回 `DESKTOP_LOGIN_CONFLICT`，确认需 `replace_existing=true` 且匹配当前 `active_session_id`。
- 认证区分 `AUTH_DESKTOP_REPLACED`、`AUTH_SESSION_INVALIDATED`、`AUTH_SESSION_EXPIRED`、`AUTH_SESSION_INVALID`。
- 密码修改、管理员重置、停用、强制下线批量失效；登出只失效当前行。
- `POST /api/v1/users/:user_id/force-logout`；`ApiError.code` / `recovery_action`。
- 删除登录时“同用户名已有会话即免密成功”的早退。

## 单测与全量 Go 测试

命令：

```bash
cd /Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud
go test ./internal/modules/identity/... ./internal/middleware/... ./internal/shared/api/... -count=1
go test ./... -count=1
```

结果：

- 定向包：identity 及其 dto/model/repository/service、middleware、shared/api 全部 `ok`。
- 全量：`ok` 73 个包，`no test files` 12 个包，`FAIL` 0 行（日志 `/tmp/cloud-go-test-t02.log`）。
- 覆盖场景：
  - 两次 Web 登录并存且各自可认证。
  - Desktop + Web 并存。
  - Desktop 冲突取消后旧会话仍有效；错误或过期 `replace_session_id` 再次冲突；正确确认后旧 Desktop 返回 `ErrDesktopReplaced`，Web 不受影响。
  - `replace_session_id` 在 `replace_existing=false` 时不能替换活跃会话；`replace_existing=true` 但缺少 ID 也冲突。
  - 两个并发 Desktop 确认只有一个成功，另一个得到冲突。
  - 会话到期返回 `ErrSessionExpired`；到期后新 Desktop 登录无需替换确认。
  - 修改密码、停用、强制下线使全部会话失效并记录对应 `invalidated_reason`；重新启用不复活旧会话。
  - 登出只失效当前会话。
  - 登录冲突与 `AUTH_DESKTOP_REPLACED` 的 HTTP 409/401、`error.code`、`details.active_session_id`、`recovery_action`、文案。
  - force-logout 未认证路由返回 401。
- Repository SQL mock 覆盖：Web 插入事务、Desktop 替换的用户行锁/旧行失效/新行插入、冲突回滚且不插入、token hash 读取过期与失效原因、批量失效 SQL。

## 迁移实跑

### 开发库 `wt_media_cloud`

迁移前：

```text
schema_migrations: 69 行，最大 20261017_067_compose_strategy_status_default
user_sessions 列: id,token_hash,client_type,created_at,invalidated_at,user_id
重复活跃 Desktop 用户: 0
会话行: 654（desktop 54，web 600）
users 认证状态列（auth_version/desktop_login_version/active_session_id）: 0
```

首次 `./scripts/migrate.sh` 在 068 的窗口函数别名上报 MySQL 8.4 语法错误（`row_number` 为保留字），DDL 已部分执行。将别名改为 `rn`，删除本次新增的两列后重跑。

重跑结果：

```text
migration ok: 1 applied, 70 total
applied 20261023_068_identity_session_state identity_session_state
```

迁移后读回：

```text
version = 20261023_068_identity_session_state
expires_at nullable = NO
invalidated_reason nullable = YES
idx_user_sessions_user_client_active = (user_id, client_type, invalidated_at, expires_at)
expires_at IS NULL = 0
重复活跃 Desktop 用户 = 0
users 认证状态列 = 0
```

### Scratch 重复会话 fixture

新建 `wt_media_cloud_m2f_scratch.user_sessions`，写入用户 1 的两条活跃 Desktop、一条 Web，用户 2 的一条已过期 Desktop 和一条活跃 Desktop，直接执行 068 迁移文件。

实际结果：

```text
s1 desktop expires 2026-10-31 invalidated_reason=superseded
s2 desktop expires 2026-11-01 invalidated_reason=NULL
w1 web     expires 2026-11-02 invalidated_reason=NULL
s3 desktop expires 2026-10-01 invalidated_reason=NULL   （已过期，不参与收敛）
s4 desktop expires 2026-11-09 invalidated_reason=NULL
expires_at nullable = NO
活跃 Desktop 每用户最大行数 = 1
```

判定：PASS。重复活跃 Desktop 保留 `created_at` 最新一行，其余标记 `superseded`；过期行不受影响；`expires_at` 回填为 `created_at + 30 天`。

## 未覆盖 / 后续

- 真实 HTTP 登录、Desktop Tauri Origin、两个 Web 会话的真实协议回归在 T-10 执行。
- `ApiError.retryable=false` 因 `omitempty` 不输出；统一错误契约在 T-03/T-05 落定时一并处理。

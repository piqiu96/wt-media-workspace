# T-03 Cloud Agent Token 与设备/节点退场证据

日期：2026-10-23
CHG：CHG-20261023-101
Cloud 提交：`b95d18a feat(local-agent): issue session-bound tokens and retire the device model`

## 范围

- `internal/shared/agenttoken`：HMAC-SHA256 无状态 Token，格式 `v1.<payload>.<sig>`；claims `ver/sub/sid/scope/iat/exp/jti`；`exp` 直接取传入的 Desktop session `expires_at`，无独立 TTL；固定 `v1`，拒绝空段/多段/非 base64url 签名。
- `POST /api/v1/local-agent/agent-token`：只接受 desktop 用户 session；web session 返回 `DESKTOP_LOGIN_REQUIRED`；签名器未配置或审计写入失败时 500，不返回空凭证；审计只记录 `session_id`，不记录 Token。
- `internal/modules/localagent`：`RequireAgent` 严格档/上报档。拒绝时 `c.Abort()`，处理函数不会在失败凭证后运行。严格档要求 `sid` 仍是当前有效 Desktop session、用户 enabled；上报档只验签名/scope/exp。
- `AuthenticateAgentSession`：抢占返回 `ErrDesktopReplaced`；web/未知/改密失效/过期/停用返回 `ErrDesktopLoginRequired`。
- 用户 API 中间件：携带有效 Agent Token 访问 → 403 `AGENT_SCOPE_FORBIDDEN`；Agent 路由不接受用户 session。
- 路由认证档：`tasks/claim` 严格；`tasks/:id/report|get`、`file-transfer` heartbeat/progress/complete、`sensitive-permits/*/renew|finish` 上报档；`tasks/:id/cancel|retry` 用户 session；`sensitive-tasks/:id/preflight` 严格。
- 退场：`runtimebinding` 模块整包删除；`cloudagent` 的 `agent_nodes` registry（register/heartbeat）删除；`users.device_*`、节点凭证、`file_transfer_tasks.assigned_*`、permit 的 node/credential 全部删除。claim/report 的 `agent_id` 只作为审计标签，从 Token 派生 `user-<id>`，不再读请求体。
- `20261023_071_remove_agent_device_model.sql` + `agent_device_model_test.go`：删除顺序（子表/FK/索引先于父表）、无 `CREATE TABLE`、`ALTER TABLE users` 块无 `ADD`。
- 契约：file-transfer 的 `nodeBearer` → `agentBearer`；`local_transfer_node_unavailable` 从错误码契约移除（5 个名称保留）；下载描述改为用户范围、不按设备。
- 文档性清理：`CreateDownload` 注释改为用户范围；`config/README.md` 登记 `agent_token.toml`、`WT_MEDIA_AGENT_TOKEN_SECRET` 与 ≥32 字符启动校验。

## 行为修正

`AuthenticateAgentSession` 遇到多条有效 Desktop 行时原本映射 `DESKTOP_LOGIN_REQUIRED`。计划 §2.3 规定“存在其他有效 Desktop session，或存在多条有效 Desktop session → `AUTH_DESKTOP_REPLACED`（失败关闭）”，该状态只可能来自迁移残留或丢失的并发，登录无法产生；已改为 `ErrDesktopReplaced`，并用直接写入 store 的用例固定。

## 定向单测

命令：

```bash
cd /Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud
go test ./internal/modules/localagent/ ./internal/modules/identity/... ./internal/middleware/ ./internal/modules/cloudagent/... ./internal/modules/filetransfer/... ./internal/modules/profileguard/... ./internal/shared/agenttoken/ ./internal/shared/api/ -count=1
```

结果：全部 `ok`。新增用例：

| 文件 | 用例 | 证明 |
| --- | --- | --- |
| `localagent/auth_test.go` | 7 个 | 缺失/过期凭证中断链；严格档抢占拒绝、`sid` 必须匹配当前 session、通过时携带用户与 session；上报档抢占后通过且完全不查询 session |
| `localagent/handler_test.go` | 5 个 | 签发的 `exp` 等于 session 过期；web 拒绝且不审计；无 session 401；签名器缺失 500；审计失败 500 并记录 session |
| `shared/agenttoken/token_test.go` | 6 个 | `exp` 绑定 session；到期前仍有效、到期即失效；篡改/换密钥拒绝；格式拒绝；ver/scope 拒绝 |
| `identity/service/agent_session_test.go` | 2 个 | 抢占与改密/过期/停用/未知分离；多条有效 Desktop 行失败关闭为 replaced |
| `middleware/identity_test.go` | 1 个（新增） | Agent Token 访问用户 API → 403 `AGENT_SCOPE_FORBIDDEN` |
| `cloudagent/router_surface_test.go` | 1 个（新增） | claim/get/report → `AUTH_AGENT_TOKEN_INVALID`；cancel/retry → `AUTH_SESSION_INVALID` |
| `filetransfer/handler_test.go` | 路由表 | 会话族与执行器族分别返回各自 401 code |
| `profileguard/handler_test.go` | 3 条路由 | 空凭证均 401 `AUTH_AGENT_TOKEN_INVALID` |
| `migration/agent_device_model_test.go` | 1 个 | 071 删除片段齐全、顺序正确、无新增表 |

变异验证（改生产代码 → 用例必须红，已逐一恢复）：

| 变异 | 结果 |
| --- | --- |
| 删除 `desktop_replaced` 分支，回落到通用失效 | `agent_session_test.go:42` 红 |
| 多条 Desktop 行改回 `ErrDesktopLoginRequired` | `agent_session_test.go:91` 红 |
| 签发端点接受 web session | `handler_test.go:118` 红（200） |
| 签发时把 `sid` 写成不同值 | `handler_test.go:103` 红（claims 不符） |

## 全量测试

```bash
go test ./... -count=1     # 日志 /tmp/chg101-cloud-tests-final.log
go vet ./...
```

- `go test`：exit 0；`ok` 70 包，`FAIL` 0 行，`no test files` 12 包。
- `go vet ./...`：exit 0。
- `gofmt`：本任务改动的文件全部干净。仓内 5 个与本分支无关的既有未格式化文件（`production/model/model.go`、`production/model/task.go`、`production/repository/store_mysql.go`、`production/repository/task_mysql_test.go`、`production/service/material_query.go`）保持原样。

## 迁移实跑

### 开发库副本（有设备/节点数据的 fixture）

`mysqldump wt_media_cloud` → scratch 库 `wt_media_cloud_chg101_mig071`（停在第 068 版），再以临时配置运行 `./scripts/migrate.sh`。

迁移前读数：

```text
local_agent_nodes=92  local_agent_binding_tickets=108  browser_profile_runtime_presence=40  agent_nodes=0
users.device_id 非空=1  sensitive_browser_tasks.node_id 非空=7  sensitive_profile_permits.node_id 非空=5
file_transfer_tasks: assigned_device_id 非空=66  assigned_node_id 非空=66  claimed_by_node_id 非空=95
```

结果：`migration ok: 1 applied, 71 total`。

迁移后读回：

```text
信息架构中已无 local_agent_nodes / local_agent_binding_tickets /
  browser_profile_runtime_presence / agent_nodes = 0 行
users.device* 列 = 0；sensitive_* 的 node_id / credential_hash 列 = 0
指向已删表的 FK = 0
file_transfer_tasks: claimed_by、attempt_id 存在；assigned_node_id / assigned_device_id 不存在
索引: idx_file_transfer_tasks_requested=(requested_by,status,created_at) 存在；
      idx_file_transfer_tasks_assigned_node 不存在
行数保持: file_transfer_tasks=116  sensitive_browser_tasks=7  sensitive_profile_permits=5  users=3
schema_migrations 含 20261023_071_remove_agent_device_model
```

### 空 scratch schema（001→071 全链）

空库 `wt_media_cloud_chg101_scratch` 上从零应用全部迁移：

```text
71 条迁移全部 applied（最后一条 20261023_071_remove_agent_device_model）
表数=32  schema_migrations=71  file_transfer_tasks.attempt_id 存在  已删表=0
```

## 旧事实扫描

```bash
git grep -n -E 'local_agent_nodes|local_agent_binding_tickets|browser_profile_runtime_presence|agent_nodes|assigned_device_id|assigned_node_id|claimed_by_node_id|device_public_key|device_last_verified|runtimebinding|runtime-report|current-login|CheckLocalTrust|ResolveTrustedLocalNode|AuthenticateNodeCredential|device_unbound|local_transfer_node_unavailable' -- '*.go' ':!internal/infra/database/migration/*'
```

- 分母：342 个已跟踪 `.go` 文件（排除迁移测试包）；命中 **0**。
- 阳性对照：同一模式在 `migrations/20261023_071_remove_agent_device_model.sql` 命中 6 行 —— 模式本身会匹配，0 是真实清空。
- 迁移测试与历史迁移中保留旧表名属预期（历史迁移正文不改）。
- `web/` 内仍有 `deviceBinding.js`、`work-env-status.js`、`downloadFacts.js`、`DownloadCentreDrawer.vue`、`PersonalInfoPage.vue` 的旧设备/节点判断与 `local_transfer_node_unavailable`/`device_unbound` 文案；这是 T-08 的范围，本任务不动 Web。
- `docs/superpowers/` 为历史规划材料，按治理不回改。

## 未覆盖 / 风险

- Agent（T-07）与 Desktop/Web（T-08）尚未迁移到新协议；旧 Agent 在新 Cloud 上按设计失败关闭，真实 Agent 回归在 T-10 统一执行。
- 069（Profile 双作用域）、070（Task Runtime）尚未写；071 已在 068 副本与空链上实跑。runner 对未应用版本按文件名顺序补齐，069/070 落地后会在开发库再跑一遍并复测全链。
- 本任务未启动服务做真实 HTTP 协议回归（例如 Desktop 换 Token、旧 Desktop 的 401 表现）；计划中的真实回归归 T-10。
- 签名密钥轮换使全部 Agent Token 立即失效，属无状态设计的已登记代价。

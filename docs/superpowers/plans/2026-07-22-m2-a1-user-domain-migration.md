# M2-A1 用户领域模型迁移实施计划

> **For Codex:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task.

**Goal:** 在不丢失现有用户及其关联数据的前提下，将 Cloud 用户领域迁移为自增 UID、管理员/高级运营/普通运营、扁平运营分组和“用户/分组范围 ∩ 授权游戏”权限模型，并交付可在真实 MySQL、API 和 Web 独立验收的 M2-A1 闭环。

**Architecture:** `identity` 模块拥有 `UserID`、角色、运营分组和统一 `AccessScope`；所有现有 `user_id` 外键统一迁移为 `BIGINT UNSIGNED`。`media_accounts` 与 `browser_profiles` 保存创建时的 `team_id` 快照以保证转组后历史归属不漂移。代理没有个人归属，A1 不虚构代理归属字段；代理权限在 M2-C 基于真实 Profile/账号关系接入。

**Tech Stack:** Go 1.24、CloudWeGo Hertz、MySQL 8.4、Vue 3、TDesign Vue Next、Vitest、Go `testing`、`go-sqlmock`。

---

## 执行边界

- 关联 Milestone：`delivery/milestones/M2-account-runtime.md#m2-a-用户权限会话与运行环境可信闭环`。
- 关联 CHG：`delivery/active/CHG-20260722-021/change.md`。
- 本计划只交付 M2-A1；不实现确认式会话替换、Desktop、BitBrowser 绑定，也不实现 M2-B～E。
- 当前 `wt-media-cloud/internal/modules/proxy/service.go` 与 `web/dist-*` 已有未提交修改，本计划不覆盖、不回退、不纳入提交。
- 每个任务先写失败测试，再写最小实现，再运行局部测试；每个仓库独立提交。

## Task 0：修复迁移 Bootstrap 的新库/旧库兼容路径

**Files:**

- Modify: `wt-media-cloud/migrations/000_bootstrap_existing.sql`
- Modify: `wt-media-cloud/internal/modules/migration/runner.go`
- Modify: `wt-media-cloud/internal/modules/migration/runner_test.go`

### Step 1：写迁移运行器失败测试

增加两类回归：

- Bootstrap 迁移在旧表存在时可以登记已有版本，运行器刷新 `schema_migrations` 后跳过已登记版本；
- 全新数据库没有对应业务表/列时，Bootstrap 不得提前登记 `20260714_001`～`20260721_011`。

运行：

```bash
env GOCACHE=/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud/.cache/go-build \
  go test ./internal/modules/migration -run 'TestApplyRefreshesVersionsAfterBootstrap|TestBootstrapExistingMigrationIsConditional' -count=1
```

预期：新增测试先因当前运行器使用旧的已应用版本集合、Bootstrap 无条件登记而失败。

### Step 2：实现最小修复

- `000_bootstrap_existing.sql` 对每个历史版本使用 `information_schema.tables` 或 `information_schema.columns` 独立判断对应完整业务表/列是否存在；
- `Apply` 每应用一个迁移后重新读取已应用版本，允许 Bootstrap 安全标记后续历史版本；
- 不改变普通迁移的顺序和错误语义。

### Step 3：验证局部回归

```bash
env GOCACHE=/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud/.cache/go-build \
  go test ./internal/modules/migration -count=1
```

预期：PASS。

### Step 4：用临时 MySQL 8.4 验证两条路径

- 新库：从空库运行全量迁移，`users`、`operation_teams` 及所有后续表存在；
- 旧库：先构造 `20260714_001`～`20260721_011` 结构和脱敏用户/引用数据，再执行 Bootstrap 与 `20260722_012`，验证行数、外键和登录映射不丢失。

### Step 5：提交 Bootstrap 修复

```bash
git add migrations/000_bootstrap_existing.sql internal/modules/migration/runner.go internal/modules/migration/runner_test.go
git commit -m "fix(migration): support fresh and legacy databases"
```

## Task 1：锁定 UID 迁移映射和数据库约束

**Files:**

- Create: `wt-media-cloud/internal/modules/migration/user_team_model_test.go`
- Create: `wt-media-cloud/migrations/20260722_012_user_team_model.sql`
- Modify: `wt-media-cloud/migrations/README.md`

### Step 1：写迁移结构失败测试

在 `user_team_model_test.go` 读取新迁移并断言：

- 创建 `operation_teams`；
- `users.id` 最终为 `BIGINT UNSIGNED AUTO_INCREMENT`；
- 原字符串 ID 保留为唯一且可空的 `legacy_id`；
- `technician` 被迁移为 `admin`；
- 以下字段迁移为数值外键：
  - `user_game_scopes.user_id`
  - `user_sessions.user_id`
  - `audit_logs.actor_user_id`
  - `media_accounts.user_id`
  - `media_account_tags.user_id`
  - `browser_profiles.user_id`
  - `profile_sync_scans.user_id`
  - `local_agent_binding_tickets.user_id`
  - `local_agent_nodes.user_id`
  - `browser_profile_runtime_presence.user_id`
  - `sensitive_browser_tasks.user_id`
  - `sensitive_profile_permits.user_id`
- `media_accounts.team_id` 与 `browser_profiles.team_id` 是创建时团队快照并受外键保护。

运行：

```bash
env GOCACHE=/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud/.cache/go-build \
  go test ./internal/modules/migration -run TestUserTeamModelMigration -count=1
```

预期：因迁移文件尚未存在而失败。

### Step 2：实现前向迁移

迁移顺序固定为：

1. 创建 `operation_teams`；
2. 为现有非 `technician` 用户创建并分配“迁移默认分组”；
3. 在 `users` 增加自增 `uid`、`team_id`，将 `technician` 改为 `admin`；
4. 为全部关联表增加数值 shadow user column，按 `users.legacy id → users.uid` 回填；
5. 为 `media_accounts`、`browser_profiles` 回填 `team_id` 快照；
6. 删除旧外键和依赖旧 `user_id` 的索引，交换 shadow column；
7. 将旧 `users.id` 重命名为 `legacy_id`，将 `uid` 重命名为主键 `id`；
8. 重建唯一键、查询索引和外键；
9. 加入角色/分组约束：`admin` 必须无分组，另外两种角色必须有且仅有一个分组；
10. 保留 `legacy_id` 作为迁移映射和人工回退依据，新用户写入 `NULL`。

迁移必须在任何破坏性列交换前完成非空、重复、孤儿引用检查；检查失败时以 SQL 错误停止，不能继续交换列。

### Step 3：补迁移回退说明

在 `migrations/README.md` 记录：

- MySQL DDL 不承诺事务回滚；
- 生产执行前必须备份；
- `users.legacy_id` 是恢复字符串 ID 关系的映射源；
- 回退顺序与前向迁移相反，禁止在未验证映射完整性时删除新列。

### Step 4：运行迁移测试

```bash
env GOCACHE=/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud/.cache/go-build \
  go test ./internal/modules/migration -run 'TestUserTeamModelMigration|TestM2MigrationFiles' -count=1
```

预期：PASS。

### Step 5：提交 Cloud 迁移切片

```bash
git add migrations/20260722_012_user_team_model.sql migrations/README.md internal/modules/migration/user_team_model_test.go
git commit -m "feat(identity): add numeric user and team migration"
```

## Task 2：迁移 Identity 领域类型与分组生命周期

**Files:**

- Modify: `wt-media-cloud/internal/modules/identity/service.go`
- Modify: `wt-media-cloud/internal/modules/identity/service_test.go`
- Modify: `wt-media-cloud/internal/modules/identity/store_mysql.go`
- Modify: `wt-media-cloud/internal/modules/identity/store_mysql_test.go`

### Step 1：写领域失败测试

新增测试覆盖：

- `UserID`、`TeamID` 为数值类型且新用户 ID 由 Store 返回；
- 首个用户为 `admin`，不再创建 `technician`；
- `admin` 的 `TeamID` 必须为空且 `GameIDs` 为空；
- `operator`、`senior_operator` 必须引用存在的团队并至少有一个授权游戏；
- 只有管理员能创建、重命名、删除团队和管理用户；
- 有用户、`media_accounts.team_id` 或 `browser_profiles.team_id` 引用的团队删除返回冲突；
- 空团队可以删除；
- 用户转组只更新用户当前团队，不重写历史对象 `team_id`；
- 创建、重命名、删除团队和用户权限变更写脱敏审计。

运行：

```bash
go test ./internal/modules/identity -run 'TestAdmin|TestTeam|TestUserAccess' -count=1
```

预期：编译或断言失败。

### Step 2：实现领域类型和 Store 接口

在 `identity` 中增加：

```go
type UserID int64
type TeamID int64

const (
    RoleAdmin          Role = "admin"
    RoleSeniorOperator Role = "senior_operator"
    RoleOperator       Role = "operator"
)
```

`User`/`PublicUser` 增加 `TeamID *TeamID`、`TeamName string`；`Session.UserID`、`AuditEvent.ActorUserID` 及 Store 方法统一使用 `UserID`。`CreateUser` 不再生成字符串用户 ID，MySQL Store 使用 `LastInsertId()` 回填。

### Step 3：实现团队生命周期

增加 `OperationTeam`、`CreateTeam`、`ListTeams`、`RenameTeam`、`DeleteTeam`。删除前由 Store 同时检查用户、媒体账号和浏览器窗口引用；冲突返回明确的 `ErrTeamInUse`，不能先删后补救。

### Step 4：实现新用户约束

- `BootstrapAdmin` 替换 `BootstrapTechnician`；
- 管理员创建/修改用户时统一验证角色、团队、游戏；
- 修改角色、团队、游戏、状态或密码后使目标用户现有会话失效；
- 禁止管理员把自己停用或删除；
- 用户有会话或业务历史时禁止物理删除，无历史用户允许删除。

### Step 5：运行 Identity 测试

```bash
go test ./internal/modules/identity -count=1
```

预期：PASS。

### Step 6：提交 Identity 领域切片

```bash
git add internal/modules/identity/service.go internal/modules/identity/service_test.go internal/modules/identity/store_mysql.go internal/modules/identity/store_mysql_test.go
git commit -m "feat(identity): add admin and operation teams"
```

## Task 3：统一权限交集并迁移跨模块 UserID

**Files:**

- Modify: `wt-media-cloud/internal/modules/identity/service.go`
- Modify: `wt-media-cloud/internal/modules/identity/service_test.go`
- Modify: `wt-media-cloud/internal/modules/mediaaccount/service.go`
- Modify: `wt-media-cloud/internal/modules/mediaaccount/store_mysql.go`
- Modify: `wt-media-cloud/internal/modules/mediaaccount/service_test.go`
- Modify: `wt-media-cloud/internal/modules/mediaaccount/routes.go`
- Modify: `wt-media-cloud/internal/modules/mediaaccount/routes_test.go`
- Modify: `wt-media-cloud/internal/modules/profilebinding/service.go`
- Modify: `wt-media-cloud/internal/modules/profilebinding/store_mysql.go`
- Modify: `wt-media-cloud/internal/modules/profilebinding/service_test.go`
- Modify: `wt-media-cloud/internal/modules/profilebinding/routes.go`
- Modify: `wt-media-cloud/internal/modules/profilebinding/routes_test.go`
- Modify: `wt-media-cloud/internal/modules/runtimebinding/service.go`
- Modify: `wt-media-cloud/internal/modules/runtimebinding/store_mysql.go`
- Modify: `wt-media-cloud/internal/modules/runtimebinding/service_test.go`
- Modify: `wt-media-cloud/internal/modules/profileguard/service.go`
- Modify: matching `*_test.go` files required by compilation

### Step 1：写权限矩阵失败测试

为统一判定增加表驱动测试：

| Actor | Owner | Team | Game | Result |
|---|---:|---:|---|---|
| admin | 任意 | 任意 | 任意 | allow |
| senior_operator | 他人 | 同组 | 已授权 | allow |
| senior_operator | 他人 | 跨组 | 已授权 | deny |
| senior_operator | 他人 | 同组 | 未授权 | deny |
| operator | 本人 | 同组 | 已授权 | allow |
| operator | 他人 | 同组 | 已授权 | deny |
| operator | 本人 | 同组 | 未授权 | deny |

同时断言 deny 时不执行 Store mutation、不创建任务、不调用外部操作入口。

### Step 2：实现 `AccessScope`

在 `identity` 提供单一判定入口：

```go
func (u PublicUser) CanAccess(ownerID UserID, teamID *TeamID, gameID string) bool
```

管理员直接允许；高级运营要求团队相同后再检查游戏；普通运营要求本人后再检查游戏。其他模块不得再复制角色判断。

### Step 3：为账号和 Profile 保存团队快照

- `mediaaccount.Account`/`AccountRecord` 增加 `TeamID TeamID`；创建时从 actor 当前团队写入，查询和修改统一调用 `CanAccess`；
- `profilebinding.BrowserProfile` 增加 `TeamID TeamID`；扫描确认/创建 Profile 镜像时写入当前团队；
- 用户转组不更新既有账号和 Profile 的 `team_id`；新建对象使用新团队；
- 管理员可显式指定目标用户，系统从目标用户读取团队，不能由请求直接伪造 `team_id`。

### Step 4：迁移其余 UserID 编译边界

将 runtime binding、profile guard、session/auth context 以及 task payload 中的 Cloud 用户 ID 改为数值类型；BitBrowser 的 `main_user_id`、`profile_user_id` 和业务对象字符串 ID 保持字符串，不得混淆。

### Step 5：明确代理边界

A1 不给代理增加 `owner_user_id` 或 `team_id`。代理列表和变更的团队/游戏权限在 M2-C 根据实际 Profile/账号关系实现；本任务只保证代理路由能编译并使用 `RoleAdmin` 新名称。

### Step 6：运行跨模块测试

```bash
go test ./internal/modules/identity ./internal/modules/mediaaccount ./internal/modules/profilebinding ./internal/modules/runtimebinding ./internal/modules/profileguard ./internal/modules/proxy -count=1
```

预期：PASS。

### Step 7：提交权限切片

```bash
git add internal/modules/identity internal/modules/mediaaccount internal/modules/profilebinding internal/modules/runtimebinding internal/modules/profileguard internal/modules/proxy
git commit -m "feat(authz): enforce team and game access scope"
```

提交前使用 `git diff --cached --name-only` 确认未暂存原有 `internal/modules/proxy/service.go` 修改；如该文件无需为角色改名而改动，不得暂存。

## Task 4：更新 API、Contracts 与一次性密码结果

**Files:**

- Modify: `wt-media-cloud/internal/modules/identity/routes.go`
- Modify: `wt-media-cloud/internal/modules/identity/routes_test.go`
- Modify: `wt-media-cloud/internal/app/app.go`
- Modify: `wt-media-cloud/internal/app/identity_test.go`
- Modify: `wt-media-cloud/contracts/business-enums/v1/identity.yaml`
- Modify: `wt-media-cloud/contracts/business-schemas/v1/identity.yaml`
- Modify: `wt-media-cloud/contracts/cloud-api/v1/identity.openapi.yaml`
- Modify: `wt-media-cloud/contracts/business-schemas/v1/media-account.yaml`
- Modify: `wt-media-cloud/contracts/cloud-api/v1/media-accounts.openapi.yaml`
- Modify: `wt-media-cloud/contracts/business-schemas/v1/browser-profile.yaml`
- Modify: `wt-media-cloud/contracts/cloud-api/v1/browser-profiles.openapi.yaml`
- Modify: `wt-media-cloud/contracts/cloud-agent-api/v1/runtime-binding.openapi.yaml`

### Step 1：写 API 失败测试

覆盖：

- 团队创建、列表、重命名、删除；
- 用户列表按 UID、用户名、角色、团队、状态和游戏筛选；
- 用户创建、修改角色/团队/游戏、启停、删除；
- 管理员重置密码；
- 创建和重置响应只在本次响应返回 `one_time_password`，后续用户查询永不返回；
- 非管理员访问管理接口返回 403；
- 非数字 path UID 返回 400；
- 密码和 hash 不进入审计、日志或常规用户响应。

### Step 2：实现路由

新增：

- `GET/POST /api/v1/operation-teams`
- `PATCH/DELETE /api/v1/operation-teams/:team_id`
- `DELETE /api/v1/users/:user_id`

更新现有用户路由接收数值 UID 和 `team_id`。创建/重置成功响应可返回本次请求中的明文密码，但只在该响应对象中存在，不写 Store、不写审计、不写日志。

### Step 3：更新 Contracts

- 所有 Cloud `user_id` 改为 `integer/int64`；
- Identity 角色改为 `admin/senior_operator/operator`；
- PublicUser 增加 `team_id`、`team_name`；
- media account 与 browser profile 增加 `team_id`；
- runtime binding 中 Cloud `user_id` 改为 integer，BitBrowser identity 字段仍为 string；
- 增加团队和一次性密码响应 schema。

### Step 4：更新 Bootstrap

配置变量名称保持向后兼容，但内部调用改为 `BootstrapAdmin`，错误信息和测试使用“initial admin”语义。

### Step 5：运行 API 与 Contract 相关测试

```bash
go test ./internal/modules/identity ./internal/app ./internal/modules/mediaaccount ./internal/modules/profilebinding ./internal/modules/runtimebinding -count=1
```

预期：PASS。

### Step 6：提交 API/Contract 切片

```bash
git add internal/modules/identity/routes.go internal/modules/identity/routes_test.go internal/app contracts
git commit -m "feat(api): expose user and team administration"
```

## Task 5：交付 Cloud Web 用户与分组管理

**Files:**

- Create: `wt-media-cloud/web/src/apps/cloud/pages/users/usersApi.js`
- Create: `wt-media-cloud/web/src/apps/cloud/pages/users/usersApi.test.js`
- Create: `wt-media-cloud/web/src/apps/cloud/pages/users/UsersPage.test.js`
- Modify: `wt-media-cloud/web/src/apps/cloud/pages/users/UsersPage.vue`
- Modify: `wt-media-cloud/web/src/modules/accounts/pages/AccountsPage.vue`
- Modify: `wt-media-cloud/web/src/session.test.js`

### Step 1：写 Web 失败测试

测试页面和 API client：

- 显示 UID、用户名、角色中文名、分组、游戏范围、状态；
- 支持用户名、角色、分组、游戏和状态筛选；
- 管理员可创建团队、重命名空/已有团队、删除空团队并看到引用冲突；
- 创建/编辑用户时管理员不显示团队和游戏必填，另外两类角色必须选择团队和至少一个游戏；
- 支持角色/分组/游戏修改、启停、删除、重置密码；
- 创建和重置后显示一次性密码复制结果，关闭后页面状态清空；
- 页面不存在 `technician` 文案；
- 账号页面管理员目标用户逻辑使用 `admin`，不再使用 `technician`。

运行：

```bash
npm test --prefix web -- --run src/apps/cloud/pages/users
```

预期：失败。

### Step 2：抽取 API client

统一解析 `{errcode,message,data,logid}`，错误提示优先使用服务端 `message`，避免页面继续使用裸 `fetch` 和通用“加载失败”。

### Step 3：实现用户与团队页面

保持一个“用户与权限”页面：顶部用户筛选和新建用户，侧边/弹窗管理扁平运营分组。所有写操作成功后重新读取服务端结果，不用前端本地假更新。

### Step 4：实现一次性密码展示

创建/重置成功后打开结果弹窗，提供复制按钮；关闭弹窗立即清除内存中的 `one_time_password`，刷新页面不能恢复。

### Step 5：运行 Web 测试与构建

```bash
npm test --prefix web
npm run build:cloud --prefix web
```

预期：PASS。构建产生的 `web/dist-*` 不纳入本 CHG 提交，因为执行前已有未提交构建产物。

### Step 6：提交 Web 切片

```bash
git add web/src/apps/cloud/pages/users web/src/modules/accounts/pages/AccountsPage.vue web/src/session.test.js
git commit -m "feat(web): manage users and operation teams"
```

## Task 6：真实 MySQL、权限矩阵与治理收口

**Files:**

- Create: `wt-media-workspace/delivery/active/CHG-20260722-021/evidence/task-1-identity-migration.md`
- Create: `wt-media-workspace/delivery/active/CHG-20260722-021/evidence/task-2-team-lifecycle.md`
- Create: `wt-media-workspace/delivery/active/CHG-20260722-021/evidence/task-3-scope-matrix.md`
- Create: `wt-media-workspace/delivery/active/CHG-20260722-021/evidence/task-4-user-management.md`
- Create: `wt-media-workspace/delivery/active/CHG-20260722-021/evidence/task-5-m2-a1-acceptance.md`
- Modify: `wt-media-workspace/delivery/active/CHG-20260722-021/change.md`
- Modify: `wt-media-workspace/delivery/LEDGER.md`

### Step 1：运行完整自动测试

```bash
./scripts/test.sh
```

预期：Go 与 Web 测试全部 PASS。

### Step 2：在真实 MySQL 副本执行迁移

使用脱敏测试库：

```bash
WT_MEDIA_MYSQL_DSN='测试库DSN' ./scripts/migrate.sh
```

迁移前后核对：

- 用户行数不变；
- 每张关联表行数不变；
- 所有新 `user_id` 都能连接到 `users.id`；
- 原 `technician` 数量等于新 `admin` 数量；
- 非管理员都有团队，管理员无团队；
- 旧用户可继续登录。

真实 DSN 不写入 Evidence。

### Step 3：启动 Cloud/Web 并验证 API

验证：管理员创建团队和三种用户；高级运营同组/跨组/跨游戏矩阵；普通运营本人/他人/跨游戏矩阵；禁用、转组、密码重置和删除受限流程。

### Step 4：验证历史归属

创建账号和 Profile 后将用户转组，再验证：

- 历史对象 `team_id` 不变；
- 新对象使用新团队；
- 旧团队因历史引用不能删除；
- deny 场景无数据库写入、无 task、无外部副作用。

### Step 5：写 Evidence

每份 Evidence 只记录：命令、脱敏输入、期望、实际、PASS/FAIL、对应提交。不得记录密码、Cookie、代理凭据、token、验证码或 DSN。

### Step 6：更新 Checkpoint 和 Ledger

只有自动测试与真实 MySQL/API/Web 验收均通过时，才能把 A1 记为完成；不得把 M2-A 或 M2 记为完成。人工产品验收未完成时，Checkpoint 写明等待人工验收。

### Step 7：提交 Workspace Evidence

```bash
git add delivery/active/CHG-20260722-021 delivery/LEDGER.md docs/superpowers/plans/2026-07-22-m2-a1-user-domain-migration.md
git commit -m "docs(delivery): record M2-A1 implementation evidence"
```

提交前不得暂存 `.DS_Store`、历史 reports 或其他无关未跟踪文件。

## 最终验证命令

```bash
cd /Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud
env GOCACHE=/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud/.cache/go-build go test ./...
npm test --prefix web
npm run build:cloud --prefix web

cd /Users/aqiuye/Develop/workspace/wt-media/wt-media-workspace
python3 scripts/verify_delivery_governance.py
python3 scripts/verify_product_master_alignment.py
python3 scripts/verify_skills.py
python3 -m unittest discover -s tests -v
```

只有命令实际返回成功并完成真实 MySQL/API/Web 验收，才可声明 M2-A1 完成。

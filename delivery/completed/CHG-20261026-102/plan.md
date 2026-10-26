# CHG-20261026-102 实施计划

## 任务理解

在已签收的 M3 上补齐“团队公共内容池 + 角色职责 + Desktop 共用入口”：

- 普通运营能查看、导入、忽略／恢复、转素材本团队所有游戏的公共内容，游戏筛选多选并初次默认本人负责游戏；
- 普通运营不能创建、编辑、启停、执行挖掘策略，也不能重试／确认挖掘任务异常；高级运营限本团队，管理员明确目标团队后跨团队；
- 高级运营、管理员可登录 Desktop 并进入 M3–M5 共用 Cloud 页面，M2 本机浏览器操作和本机 Agent 仍只对普通运营开放；
- 所有拒绝在服务端发生，前端隐藏按钮只作配合。

## 当前事实与约束

- 内容池与挖掘策略已有 `game_id` 列和团队列，**不需要新增业务列**；`source_contents` 写库保留忽略状态，重复发现不覆盖。
- 挖掘策略／任务写操作当前没有任何角色门禁；现有服务测试普遍用 `operator` 调创建、执行、删除，必须改成高级运营并新增拒绝用例。
- 内容列表只解析 `team_id`，没有 `game_ids`；策略／任务列表没有 `team_id`。
- 非管理员 `/api/v1/games` 只返回本人负责且启用的游戏，不能满足“可改选本团队其他游戏”；游戏本身是全局字典。
- Desktop 登录当前只允许 `operator`；Agent Token 签发只校验 Desktop 会话，不校验角色；Rust 本机命令没有角色判断。
- 前端多个页面直接调用 `/games`，非管理员拿不到完整游戏目录，其它游戏名称显示为 `-`。
- 本轮只改 Cloud 与 Workspace；Desktop 仓预计无 Rust 代码变更，只做构建与入口验证。若验证发现本机命令仍可从界面触达，停止并回 Workspace 扩范围。

## 已定实施口径

| 编号 | 口径 |
| --- | --- |
| D-1 | 游戏目录用现有 `/api/v1/games` 增加可选 `scope=all`：非管理员也只返回启用的全局游戏；不新增端点、不改默认行为。 |
| D-2 | 普通运营可**读**策略／任务列表，不能写；人工 ID／链接／关键词发现属于内容导入，保持可用；重试／确认属于任务异常处置，仅高级运营和管理员。 |
| D-3 | 策略创建：高级运营自动本团队；管理员必须显式带 `team_id`，缺省返回 400；任务与策略列表管理员可带 `team_id` 过滤，不带为全部团队。 |
| D-4 | Desktop：三角色可登录；四条 M2 路由（账号、开户、浏览器窗口、代理）标记 `localOnly`，菜单隐藏、路由拦截；非普通运营不启动本机 Agent、不申请 Agent Token；Cloud 签发 Agent Token 时服务端只放行 `operator`。 |
| D-5 | `game_id` 必填、默认 `other`：来源创建、批量导入、策略创建／更新统一补默认值；新增 repeat-safe migration 确保 `operation_games` 存在 `other`。 |
| D-6 | 内容池／挖掘 API 目前不在正式 OpenAPI 合同内；本 CHG 记录为已知合同缺口，不新建合同、不改跨仓协议。 |

## 任务清单

### T-01 服务端角色与团队门禁

范围：

- `Cloud/internal/modules/contentpool/service/discovery.go`：新增 `canManageDiscovery` / `requireManager`；创建、更新、启停、删除、执行策略，重试、确认任务异常先过角色门禁；管理员创建策略缺目标团队时返回明确错误。
- `Cloud/internal/modules/contentpool/service/list_query.go`：`StrategyListQuery`、`CrawlTaskListQuery` 增加 `TeamID`。
- `Cloud/internal/modules/contentpool/handler.go`：策略／任务列表解析 `team_id`；创建策略按角色决定团队来源；新增“请选择目标团队”错误映射。
- 既有测试改为高级运营；新增普通运营全部写入口被拒、高级运营跨团队被拒、管理员缺团队被拒、管理员带团队成功。

验收：

- 普通运营伪造写请求返回 403，数据库无新增／无状态变化；
- 高级运营只能读写本团队；管理员可按目标团队操作；
- 普通运营仍可读列表、人工导入和执行内容处理。

### T-02 内容池游戏多选与默认游戏

范围：

- `Cloud/internal/modules/contentpool/dto/dto.go`、`repository/filter.go`、`service/store_adapter.go`、`repository/store_mysql.go`：`Filter` 增加 `GameIDs []string`，SQL 生成 `s.game_id IN (...)`。
- `Cloud/internal/modules/contentpool/handler.go`：解析逗号分隔／重复的 `game_ids`，去空、限长；非法输入返回 400。
- `Cloud/internal/modules/contentpool/service/service.go`、`discovery.go`：来源创建、导入、策略创建／更新统一补 `other`。
- `Cloud/migrations/20261026_073_ensure_other_game.sql`：`INSERT IGNORE` 保证默认游戏存在。
- 测试：多选命中、空选返回全部、团队边界不被游戏筛选突破、默认 `other`、SQL 条件单测。

验收：

- `GET /content-pool?game_ids=hy,sjz` 只返回两游戏内容；不带时返回团队全部；
- 伪造 `team_id` 不能借游戏筛选读其他团队；
- 新建来源／导入／新建策略未带游戏时落为 `other`。

### T-03 游戏目录与前端筛选／角色按钮

范围：

- `Cloud/internal/modules/identity/service/service.go`、`operations.go`、`handler.go`：新增 `ListAllGames`，`GET /games?scope=all`；测试非管理员返回全部启用游戏、仍排除停用游戏。
- `Cloud/web/src/apps/cloud/pages/users/usersApi.js`、`shared/api/discovery.js`：透传 `scope`、`team_id`。
- `ContentPoolPage.vue`：新增当前用户、管理员团队筛选、游戏多选；初次默认本人 `game_ids`；游戏名称用完整目录映射；管理员切换团队后重置游戏筛选并重载。
- `DiscoveryStrategiesPage.vue`：当前用户与 `canManage`；普通运营隐藏新建／编辑／删除／启停／执行；管理员团队筛选与创建目标团队必选；列表增加团队列。
- `CrawlTasksPage.vue`：当前用户与 `canManage`；普通运营隐藏重试／确认；管理员团队筛选；列表团队列。
- 更新 `ContentPoolPage.test.js`、`DiscoveryPages.test.js` 等源码／参数断言；新增游戏默认值与团队参数断言。

验收：

- 普通运营页面能看到本团队其他游戏内容、游戏可多选、初次默认本人游戏；看不到策略写操作；
- 管理员能选择目标团队和多个游戏；
- 页面请求参数与 API 读回一致。

### T-04 Desktop 三角色登录与 M2 本机边界

范围：

- `Cloud/web/src/utils.js`：`canUseDesktop` 放开三角色；新增 `canUseLocalAgent`（仅 operator）。
- `Cloud/web/src/apps/desktop/router.ts`：账号、开户、浏览器窗口、代理四条路由加 `meta.localOnly`。
- `Cloud/web/src/apps/desktop/main.ts`：认证后按角色启动／停止本机 Agent；`localOnly` 路由非普通运营重定向到内容池。
- `Cloud/web/src/layout/AppLayout.vue`：Desktop 下非普通运营隐藏本机路由与桌面环境，隐藏 `WorkEnvPill`。
- `Cloud/web/src/modules/auth/pages/LoginPage.vue`：删除“管理员和高级运营不能登录”的分支；仅普通运营获取 Agent Token；非普通运营登录后停止本机 Agent。
- `Cloud/web/src/modules/auth/pages/PersonalInfoPage.vue`：非普通运营不读取／显示本机 Agent 与比特账号绑定。
- `Cloud/internal/modules/localagent/handler.go`：签发 Agent Token 仅 `operator`；测试新增高级运营、管理员被拒。
- 测试：重写 `desktopRoleGuard.test.js`，补 `routerParity.test.js` 的路由 meta 断言、`localSettingsWiring.test.js` 的守卫断言。

验收：

- 高级运营／管理员能登录 Desktop 并打开内容池、策略、任务页面；
- 直接输入 `/accounts`、`/browser-windows`、`/proxies`、`/account-opening` 被拦回内容池，菜单不可见；
- 高级运营／管理员换 Agent Token 返回 403；普通运营原流程不变；
- 记录“本机命令只由产品界面隔离、Rust 未加角色判断”的边界说明。

### T-05 真实证据与门禁

范围：

- Cloud：`go test ./...`、`npm test --prefix web`、`scripts/verify/test-control.sh`。
- Workspace：`PYTHONDONTWRITEBYTECODE=1 python3 scripts/wt.py test repo --repo wt-media-workspace`（PyYAML venv）。
- 开发栈：启动 Cloud API 与 Web，使用三个角色真实登录；对内容池游戏筛选、策略写入口、任务异常入口发真实请求并读库；Cloud Web 页面按角色读回按钮与筛选。
- Desktop：按需构建 `.generated/frontend`／安装包，验证新前端进入产物；GUI 人工确认交由用户，记录到 evidence。
- 证据文件：`evidence/T-01-role-gates.md` … `evidence/T-05-acceptance.md`，含命令、预期、实际、PASS/FAIL、提交引用。

验收：

- 每个 `Done When` 都有真实请求／数据库／页面读数，不只用单测；
- 拒绝请求无业务写入、无外部抓取；
- Cloud Web 与 Desktop 共用页面授权一致；
- PR CI 通过后合入。

## 明确不修改

- 不改 `source_content` 团队唯一键、忽略语义、重复发现逻辑。
- 不做 M4-J 素材库归位、个人下载口径（CHG-104）。
- 不做负责人链路、任务／成片负责人快照（CHG-103）。
- 不做自动选材候选来源切换与并发验证（CHG-105）。
- 不新建内容池／挖掘 OpenAPI 合同，不改 Desktop Rust 本机命令。
- 不重开 M3／M2 已签收结论，不新建第二套内容池。

## 冲突与未确认项

- 无阻塞问题。D-4 的 Rust 边界为本 CHG 采用的最小方案：产品界面＋服务端 Token 双拦截；若人工验收认为必须在 Rust 命令层再加角色判断，另立范围，不在本 CHG 内临时扩。
- 普通运营可读策略／任务列表：PRD 只禁止“修改、启停、执行、处置异常”，未禁止查看，按可读处理。
- 管理员的“默认该团队全部游戏”以“不选游戏即全部”实现，不预填每个游戏 ID。

## 提交边界

- Cloud：T-01、T-02、T-03、T-04 各自独立提交；T-05 只加必要修复，不混入重构。
- Workspace：plan、evidence、状态与里程碑更新独立提交。
- Desktop：无代码提交；构建产物不入库。
- 每个仓独立 PR，PR 描述引用 `CHG-20261026-102`；不直推 main。

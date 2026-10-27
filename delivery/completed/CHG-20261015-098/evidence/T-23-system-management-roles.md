# T-23 系统管理与 Desktop 角色导航

日期：2026-10-27（Asia/Shanghai）
结论：PASS（机器腿）。系统管理三页按角色可见、团队人数服务端化、游戏管理高级运营只读已实现并通过单元测试与两个前端构建；真实页面（含 MySQL 上的 `user_count`）由 T-26 三账号走查读回。

## 提交

| 仓 | 分支 | 提交 |
| --- | --- | --- |
| wt-media-cloud | `chg/CHG-20261015-098-round3` | `bf94da0`（identity + 导航/守卫/页面 + 合同） |
| wt-media-workspace | `chg/CHG-20261015-098-docs` | 本文件所在提交（ADR-0023 追加、第三章 §3.2.8、contract-map） |

## 一、落地口径

| 页面 | operator | senior_operator | admin |
| --- | --- | --- | --- |
| 用户管理 | 不可见 | 不可见 | 可读写 |
| 运营团队 | 不可见 | 可见只读（含人数） | 可读写 |
| 游戏管理 | 不可见 | 可见只读（全部状态，无关联情况/关联详情） | 可读写 |
| 桌面环境（本地日志 / 本机设置） | 可见 | 可见 | 不可见 |
| 社媒账号 | 可见（本地操作按归属，T-24） | 可见（本人账号可本地操作，他人只读，T-24） | 可见只读（T-24） |
| 开户 / 浏览器窗口 / 代理 | 可见（Desktop） | 不可见 | 不可见 |

判据写在 `wt-media-cloud/web/src/shared/utils/roles.js`：`SYSTEM_MANAGEMENT_PATHS`、`canViewSystemPath`、`canUseDesktopEnv`、`isAdminRole`。`AppLayout.vue`、Cloud `main.ts`、Desktop `main.ts` 三处解析同一张表。

## 二、服务端

| 项 | 实现 | 验证 |
| --- | --- | --- |
| 团队人数 | `OperationTeam.UserCount`；`teamColumns` 用同一条 SELECT 的标量子查询 `(SELECT COUNT(*) FROM users u WHERE u.team_id = t.id)`，`findTeam` 与 `listTeams` 共用 | `TestListTeamsReportsMembershipCount`：甲组 2、乙组 1，关键字过滤后计数不丢 |
| 游戏管理视图 | `Service.ListManagementGames`：senior + admin，返回全部状态、不填 `ReferenceSummary`；operator 403。handler 的 `scope` 增加 `management` | `TestListManagementGamesShowsEveryStatusWithoutReferenceSummaries`：senior 看到启用+停用且无摘要；operator `ErrForbidden` |
| 管理员口径 | `GamesPage` 请求 `scope=all`，仍带关联摘要（`listGames` 对 admin 附加 summary） | 同一用例覆盖 senior 分支；admin 分支由既有 `listGames` 用例覆盖 |

命令与读数：

```
$ go test -count=1 ./internal/modules/identity/...
ok  .../identity       1.020s
ok  .../identity/dto   0.366s
ok  .../identity/model 0.760s
ok  .../identity/repository 1.265s
ok  .../identity/service 8.028s

$ go build ./... ; go vet ./internal/modules/identity/...     # 无输出
```

## 三、前端

- `AppLayout.vue`：删除 `adminOnlyPaths` / `desktopHiddenPaths`；`localOnlyPaths` 只剩 `/account-opening`、`/browser-windows`、`/proxies`，且仅在 Desktop 隐藏；系统管理按 `canViewSystemPath` 隐藏；桌面环境改由 `canUseDesktopEnv`（运营+高级运营，不含管理员）。
- Cloud `main.ts`：系统管理路径的角色守卫（`/users` 仅 admin；`/operation-teams`、`/games` senior+admin）。
- Desktop `router.ts`：新增 `users`、`operation-teams`、`games`，组件直接 `import("../cloud/pages/users/*.vue")`；`accounts` 去掉 `meta.localOnly`。
- Desktop `main.ts`：`LocalLogs` / `LocalSettings` 读会话后把非桌面环境角色退回 `/content-pool`（无会话仍可打开排障）；登录后新增系统管理路径守卫。
- `TeamsPage.vue`：列表直接用服务端 `user_count`，不再调 `listUsers`；`canManage`（仅 admin）控制「新增团队」与操作列。
- `GamesPage.vue`：`scope = canManage ? 'all' : 'management'`；列与「新增游戏」按 `canManage` 增减，`openReferences` 对非管理员直接返回。

## 四、合同与文档

| 文件 | 变更 |
| --- | --- |
| `contracts/cloud-api/v1/identity.openapi.yaml` | `2026.10.23.1 → 2026.10.27.5`；`OperationTeam.user_count`；新增 `GET /api/v1/games`（`scope=all\|management`）与 `Game` / `GameReferenceSummary` / `GameListResponse` |
| `contracts/business-schemas/v1/identity.yaml` | `2026.10.23.1 → 2026.10.27.4`；`OperationTeam.user_count` |
| `config/contract-map.yaml` | `cloud_api 2026.10.27.5`、`business_schemas 2026.10.27.4` |
| `docs/contracts/contract-map.md` | 新增「System management revision」段，并登记游戏写接口仍未声明这一既有缺口 |
| `docs/decisions/0023-...md` | 追加 2026-10-27 系统管理 / 桌面环境 / 账号本地操作按归属决议 |
| `docs/product/prd/详细文档/第三章_用户与账号管理.md` | 新增 §3.2.8 |

合同修订值与活源对比（目录内最大值）：

```
$ grep -rh "^  version:" contracts/cloud-api/v1/*.yaml | sort | tail -1
  version: 2026.10.27.5
$ grep -rh "^revision:" contracts/business-schemas/v1/*.yaml | sort | tail -1
revision: "2026.10.27.4"
$ python3 scripts/verify/verify_m0_config.py
Workspace config verification ok
$ python3 scripts/verify/verify_m2_acceptance.py
M2 static cross-repository acceptance matrix ok
```

## 五、测试读数

| 项 | 读数 |
| --- | --- |
| `npx vitest run`（`wt-media-cloud/web`） | **86 文件 / 778 测试全绿**（T-22 收尾为 85 / 768；新增 `shared/utils/roles.test.js` 4 条、`TeamsAndGamesPage.test.js` +3、`desktopRoleGuard.test.js` +3） |
| `npm run build:desktop` | 成功（7.43s），Desktop 三个系统页与 Cloud 组件同文件打包 |
| `npm run build:cloud` | 成功（6.91s） |
| `routerParity.test.js` | 共享 path 比较改为「解析后的文件」；系统管理由「桌面端不得出现」改为「两端同一组件文件」，三条都断言 `desktop === cloud` |
| `desktopRoleGuard.test.js` | `LOCAL_ONLY_PATHS` 3 条、分母 3；新增桌面环境与系统管理守卫断言、社媒账号无 `localOnly` |
| `localSettingsWiring.test.js` | loader 计数 20 → 23；切片端点改 `const localOnlyPaths`（原 `adminOnlyPaths` 已删除），并加端点失效守卫 |

## 六、覆盖边界（未覆盖项）

- **MySQL 上的 `user_count` 未被单测执行**：service 用例走 memory store；标量子查询只由 T-26 真实页面读回验证（团队人数与数据库计数一致）。
- **Desktop 打包产物的菜单视觉**：本机不能程序化驱动 GUI，三角色菜单与禁用态由用户按打包产物确认；机器只验路由、源码与构建。
- **游戏写接口**（POST/PATCH/DELETE `/games`、`/games/{id}/references`）仍未写入合同，是本次变更前就存在的缺口；本轮只补了页面所用到的 `GET /games`，未扩大缺口也未顺手补写。
- **角色能力矩阵中仍待裁定的四项**（Cloud Web 本地页对 senior/admin 可见、管理员读任意账号 Cookie、账号云端编辑/标签/绑定窗口的 senior 范围、内容池团队公共池）不在 T-23 内解决，见 `2026-10-27-round3-role-capability-matrix.md`。

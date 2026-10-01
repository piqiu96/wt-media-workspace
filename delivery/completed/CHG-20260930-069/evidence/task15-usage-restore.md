# 任务 15 证据：我的素材关系的读回与恢复（后端 + 契约，无迁移）

日期：2026-09-30　仓库：`wt-media-cloud`（提交 `fdec6d4`）　范围：后端 + 契约

任务 14 把「使用状态」列与「恢复使用」按钮画了出来，但服务端只有 `active` 一侧：
列表把已放弃的关系滤掉，恢复也没有端点，点下去拿到的是一个真实的 404（见任务 14
证据 §7「已知的中断状态」）。本任务把这个中断接上。

## 1. 来源

用户走查七轮提示词（任务 13 那条消息里的 `## 给 Codex 的执行提示词`）第「五、六、十
一、十五」节，加上澄清问题的裁定「1、上传素材这个功能暂时先不做 2、其他的前后端一起
改 3、使用状态 tab 计数不用做 4、按钮按照超过 5 个才有更多按钮出现 5、放弃/移除的行，
应该需要有恢复的按钮」。

## 2. 动手前核实的事实（不是推断）

1. **Business Schema 不用改。** 计划里写「`MaterialUsage` 已是 `active / removed`，不
   改」——逐字核实过：`contracts/business-schemas/v1/content-production.yaml:88` 的
   `status: {type: string, enum: [active, removed]}`、`:91` 的 `removed_at` 带说明
   「关系仍是 active 时该键不出现」，`contracts/business-enums/v1/content-production.yaml:5`
   的 `material_usage_statuses: [active, removed]`。三处都已是两态，改动只在 OpenAPI。
2. **库列也已经够用。** `material_usages.status VARCHAR(16) NOT NULL DEFAULT 'active'` +
   `CHECK (status IN ('active','removed'))`、`removed_at DATETIME(6) NULL`，自 M4-A 起就
   是这个形状 —— 本任务**没有迁移**，`scripts/migrate.sh` 跑出「0 applied, 43 total」。
3. **「已中断」仍然没有取值。** 用户此前给的视觉图里 tab 是「已中断 (0)」，但库里没有
   第三档、Business Schema 也没有。本任务不猜、不新增 enum（登记在 `change.md` §3）。

## 3. 先红

命令：`go test ./internal/modules/production/...`

- `handler`：`POST /api/v1/material-usages/5/restore status = 404, want 401`（路由不存在）；
  `TestRestoreUsageRouteAnswersThroughTheEmpty204Helper`：`handler.go has no RestoreMaterialUsage`。
  这两条是**有判别力的红**。
- `repository` / `service`：`undefined: listUsages`、`undefined: restoreUsageByID`、
  `*memoryStore does not implement Store` —— 这是改名造成的编译红，**本身什么都证明不了**
  （任何拼写错误都会这样红）。所以红之后没有直接动手，而是把每一条新断言都做了变异对照，
  见 §6。

## 4. 实现

- `repository/store_mysql.go`：
  - `ListActiveUsages` → `ListUsages`，SQL 去掉 `AND status = 'active'`，两类关系行都返回
    （`removed_at` 原本就在列清单里，随行带出）；
  - 排序 `updated_at DESC, id DESC` → `created_at DESC, id DESC`。理由有两条，方向一致：
    页面上那一列就叫「加入时间」，而按 `updated_at` 排的话，刚被放弃/刚被恢复的行会当场
    跳到列表最上面 —— 用户正要再点它一次。**这条不在 `change.md` §5 第 15 条里**，是本
    轮加的判断，记在这里以免被当成既成事实读。
  - 新增 `RestoreUsageByID` / `restoreUsageByID`：
    `UPDATE material_usages SET status = 'active', removed_at = NULL, updated_at = ? WHERE id = ? AND user_id = ? AND status = 'removed'`。
- `service/service.go`：`Store` 接口同步改名并加 `RestoreUsageByID`；新增
  `RestoreUsage(actor, usageID)`，检查顺序与 `RemoveUsage` 一致（先按 `user_id` 找关系 →
  再查素材范围 → 再判 team），已经是使用中的关系直接返回成功。
- `service/store_adapter.go`、`service/operations.go`：适配器与包级包装各一条。
- `handler.go`：`RestoreMaterialUsage`，成功走 `api.NoContentEmpty(c)`（与它撤销的那条
  DELETE 同一个答复）。
- `router.go`：`POST /api/v1/material-usages/:usage_id/restore`。
- `contracts/cloud-api/v1/content-production.openapi.yaml`：`version 2026.09.30.1 →
  2026.09.30.2`；新增该路径（204 / 403 / 404）；`/api/v1/my-materials` 的 summary 从
  「active material usages」改成「material usages, in both states」，并补 `description`
  说明已放弃的行也会返回、`material` 嵌在每条 usage 上。改后用 ruby 解析确认 8 条路径
  与 `operationId: restoreMaterialUsage` 都在。

**前端一行没改**：`shared/api/materials.js` 的 `restoreUsage(usageId)` 与页面的
`restore`/`giveUp` 都是任务 14 落的，本任务只是让它们背后真的有东西。

## 5. 与计划的偏差（一处，明确登记）

`change.md` §5 第 15 条第 3 步写「受影响 0 行时按「已是他人的行 / 已恢复」**区分错误**」。
实现里这两条的区分是「404 / 成功」而不是「错误 / 另一种错误」：

- 他人的行、不存在的行 → `FindUsageForUser`（带 `user_id`）根本找不到 → `ErrUsageNotFound`
  → 404 `15006`。两者**故意不可区分**，否则可以按 id 猜别人有没有这行（与既有
  `TestFindUsageForUserDoesNotDistinguishSomeoneElsesRowFromNoRow` 同一条规矩）。
- 已恢复（行已经是 `active`）→ **204 成功**。点「恢复使用」要的就是这个状态；最常见的
  第二次询问是列表重载前的双击，报错等于在一个成功的动作上弹失败提示。
- 因此 repository 的恢复语句**不返回 bool**：0 行能描述的唯一结果就是「它已经在使用中」，
  那正是调用方要的。保留 bool 会得到一个没有人分支的返回值。

## 6. 变异对照（每条新断言都要能红）

绿之后逐条把实现改坏、确认断言真的变红，再还原（还原后 `go test -count=1` 复跑全绿，
无残留）：

| 变异 | 结果 |
|---|---|
| `listUsages` 把 `AND status = 'active'` 加回去 | `TestListUsagesScopesTheQueryToTheUserAndKeepsBothRelationStates` FAIL |
| 恢复语句写成 `removed_at = removed_at`（不清空） | `TestRestoreUsageByIDOnlyTakesBackARowTheUserGaveUp` FAIL |
| 删掉 `restoreUsageByID` 的 scope 前置检查 | `TestRestoreUsageByIDRefusesAnIncompleteScope` 第一臂 FAIL（`error = nil`） |
| 把 scope 检查挪到 Exec **之后** | 同一条第二臂 FAIL（`sent a statement, want a refusal before the database`） |
| `ListMyMaterials` 在 service 里过滤非 active 行 | `TestListMyMaterialsKeepsTheGivenUpRelationWithItsOwnState` FAIL |
| `RestoreUsage` 去掉素材范围检查 | `TestRestoreUsageChecksTheMaterialScopeBeforeRestoration` FAIL（`err=<nil> restored=5`） |
| 去掉路由注册 | `TestRegisterRoutesBindsMaterialEndpoints` FAIL（404, want 401） |

第三条到第四条这一对是特意做的：`TestRestoreUsageByIDRefusesAnIncompleteScope` 先注册一条
`ExpectExec(".*")` 通配期望，然后断言它**没有被消费**。只断言 `err != nil` 的写法在这里是
空转——mock 对没被期望的 Exec 同样会返回错误，于是「先写后校验」这种改坏方式会绿着过。

## 7. 后绿与读数

- `gofmt -l internal/`：空；`go vet ./internal/modules/production/...`：无输出。
- `go test -count=1 ./...`：**66 包 ok / 0 FAIL**（与任务 12/13 的分母一致）。
- `npx vitest run`（cwd = `web/`）：**46 文件 / 389 用例全绿**。本任务未改任何前端文件，
  与任务 14 那一批是同一批文件，读数一致。
- `npm run build:cloud` 与 `npm run build:desktop`：均 exit 0（仅既有 chunk 体积提示）。
- 以上全部在最后一次改动之后重跑。

## 8. 真实往返（`up --force-restart` 后，对着本机 Cloud + MySQL）

环境：`./scripts/m2b-local-acceptance.sh up --force-restart` → Cloud `pid 27203`（`go run`
重新编译，跑的是本次提交的代码）、Agent `pid 27211`、BitBrowser via Agent PASS、迁移
「0 applied, 43 total」。会话：`admin`（user 1）与 `operator01`（user 3，密码 `operator01`）。

| # | 动作 | 结果 |
|---|---|---|
| 1 | `GET /my-materials`（admin） | 3 行，全部 `active`、无 `removed_at` |
| 2 | `DELETE /material-usages/3` | `http=204`，`size_download=0`（真 204、无 body） |
| 3 | 库里读 id=3 | `removed`，`removed_at=2026-09-30 19:29:04.980418` |
| 4 | `GET /my-materials` | **仍是 3 行**，id=3 带 `status: removed` 与 `removed_at`，且**嵌的 material 还在** |
| 5 | `DELETE /material-usages/2`（最旧的一行）再读列表 | 顺序仍是 3、2、1（= `created_at DESC`）。按旧的 `updated_at` 排，刚改过的 2 会跳到第一行 |
| 6 | `POST /material-usages/3/restore`、`/2/restore` | 各 `http=204`、`bytes=0` |
| 7 | 库里读 id=2、3 | 两个都 `active`，**`removed_at` 均为 `NULL`**（不看 API 的 `omitempty`，直接读列） |
| 8 | `GET /my-materials` | 3 行全 `active`、`removed_at` 不出现 |
| 9 | `operator01` 放弃自己的 id=8 → admin 去恢复它 | `404 {"errcode":15006,...}`，且库里那行**原样不动**（仍 `removed`、`removed_at` 未变） |
| 10 | `operator01` 恢复自己的 id=8 | `204`，库 `active` / `removed_at NULL` |
| 11 | admin 恢复已是使用中的 id=3（双击的第二下） | `204`（幂等，不是错误） |
| 12 | `POST /material-usages/999999/restore` | `404 15006` |
| 13 | 不带会话 | `401 11001` |
| 14 | `/material-usages/abc/restore`、`/0/restore` | `400 15004`「我的素材关系 ID 无效」 |

收尾核对：`select count(*) total, sum(status='active') active, ...` → **9 行 / 9 active /
0 removed / 0 有 `removed_at`**，与本任务动手前读到的一致（走查用的开发数据放回原样，
没有留下被放弃的行）。

## 9. 边界

- 不碰数据库结构（无迁移）；不动权限模型、业务语义、既有端点的行为。
- 不做：使用状态 tab 与计数、来源列、来源平台筛选、已中断、文件异常、上传素材
  （见 `change.md` §3）。
- 「加入合成」仍跳 `/compose`（ComingSoon），本任务不给它造端点。

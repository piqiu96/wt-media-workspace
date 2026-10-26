# T-06 角色范围与服务端裁决

## 方法与覆盖边界

本机检出没有 `admin` / `senior01` 的登录口令；本 CHG 不修改账号口令、状态，也不以他人会话代登录。因此：

- 普通运营 `operator01`：真实 HTTP 会话 + 真实 MySQL，读数见 `T-06-team-scope-and-filters.md`、`T-06-usage-facts.md`。
- 高级运营 / 管理员：用仓库内真实 `production` service 的角色用例验证；handler 对这两类角色没有额外分支，只把会话解析出的 actor 交给 service，错误映射由 `composeTaskErrorFor` 统一表覆盖。
- **未以高级运营 / 管理员会话发起 HTTP 请求**。这是覆盖边界，不冒充三角色实测。

## 真实团队数据（管理员读模型的对象）

`SELECT team_id, COUNT(*) FROM materials GROUP BY team_id`，2026-10-26 实测：

| 团队 | 素材数 |
| --- | --- |
| 1 | 59 |
| 6 | 8 |
| 8 | 18 |
| 9 | 18 |
| 10～21 其余团队 | 68 |
| 合计 | 171 |

普通运营 `operator01`（团队 1）`GET /materials` 读回 59 条、`game_ids=hy|sjz|other` 分别 14/19/26 条、`team_id=8` 返回 403 `15002`——真实 HTTP 已证明团队边界与“游戏只做筛选”（见前两份证据）。管理员的目标团队读取由同一查询的 `m.team_id` 条件承载；管理员未指定团队时该条件不出现，返回跨团队全集。

## 高级运营

| 断言 | 方式 | 结果 |
| --- | --- | --- |
| 本团队所有游戏，不受负责游戏收窄 | `TestListMaterialsLetsASeniorReadEveryGameOfTheirTeam`：actor `GameIDs=[game-a]`、请求不带游戏；断言下发的 `TeamID=本人团队` 且 `GameIDs` 为空 | PASS |
| 指定其他团队被拒且不查询 store | 同用例：`TeamID=8` → `ErrForbidden`，`factsIDs` 保持空 | PASS |
| 姓名明细只给高级运营/管理员 | `TestListMaterialsDecoratesTheViewersRelationAndTheTeamsUsage`：普通运营 `operators` 为空，高级运营收到姓名 | PASS |
| 重试是高级运营能力 | `TestRetryComposeTaskRequiresSeniorRoleAndTakesEveryFailureButUncertain`：普通运营 403、高级运营可重试 cancelled／非 uncertain failed | PASS |
| `execution_uncertain` 不可重试 | 同用例：`ErrComposeTaskNotRetryable`，任务行保持 failed/execution_uncertain | PASS |
| HTTP 409／15217／`compose_task_not_retryable` | `TestComposeTaskErrorCarriesTheFrozenPairs` 增加该错误对；`contracts/cloud-error-codes/v1/content-production.yaml` 登记 `http_status: 409` | PASS |

## 管理员

| 断言 | 方式 | 结果 |
| --- | --- | --- |
| 按目标团队读取 | `TestListMaterialsLetsAnAdminChooseTheTargetTeam`：请求 `TeamID=8`，下发同一个团队且 `UserID=管理员` | PASS |
| 未指定团队时跨团队读取 | `TestListMaterialsLetsAnAdminReadAcrossTeamsWhenNoTeamIsNamed`：下发的 `TeamID` 为空 | PASS |
| 跨团队可见性 | `TestGetMaterialScopesVisibilityByTeamNotGame`：管理员跨团队可读；高级运营/普通运营跨团队 `ErrForbidden`；普通运营读同团队其他游戏可读 | PASS |
| 姓名明细 | 同一装饰用例的管理员分支：收到两名已知负责人姓名 | PASS |

## 未覆盖

- 没有以高级运营 / 管理员会话调用 `GET /materials`、`GET /materials/{id}`、`POST /compose-tasks/{id}/retry` 的真实 HTTP 记录。上面列出的角色分支、团队选择和 SQL 条件均有自动化用例与真实团队数据佐证，但“登录后由服务端会话注入 actor”这一层没有实机读数。
- 若后续提供高级运营 / 管理员测试口令（mode-600 临时文件），可在收尾前补这三条 HTTP 读数，不需改代码。

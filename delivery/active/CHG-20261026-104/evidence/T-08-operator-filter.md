# T-08 负责人筛选修订

日期：2026-10-27

## 用户反馈与根因

高级运营在合成任务／成片管理看不到团队成员作为负责人选项，只能看到“我的／团队全部”。

代码事实：

- `ComposeTasksPage.vue` / `MyOutputsPage.vue` 给高级运营注入 `mine`、`team` 两个伪选项，并在挂载时把筛选默认成 `mine`；`/compose-operators` 返回的成员姓名排在伪选项之后。
- 任务／成片列表给所有非管理员加 `filter.GameIDs = actor.GameIDs`；`canReadComposeTask` / `canReadComposeOutput` 也先按本人负责游戏判断。只要任务／成片属于高级运营本人未负责的游戏，即使下拉里能选到成员，也读不到其任务／成片。

## 修订

### 页面

| 文件 | 修订 |
| --- | --- |
| `web/src/modules/compose/pages/ComposeTasksPage.vue` | 负责人选项只来自 `/compose-operators` 团队成员（含本人）；去掉 `mine` / `team` 伪选项与默认 `mine`；不再发送 `operator_scope`；负责人筛选可清空 |
| `web/src/modules/compose/pages/MyOutputsPage.vue` | 同上 |

未选择负责人时不发参数；选中成员只发 `operator_id`；管理员仍先选团队。

### 服务

| 文件 | 修订 |
| --- | --- |
| `internal/modules/production/service/operator.go` | 高级运营空 `operator_scope` 的默认值改为 `team`；显式 `mine` / `team` / `operator_id` 仍兼容 |
| `internal/modules/production/service/task.go` | 只有普通运营下发 `GameIDs`；`canReadComposeTask` 对高级运营在团队校验后直接放行，普通运营仍校验负责游戏与本人任务 |
| `internal/modules/production/service/output.go` | 只有普通运营下发 `GameIDs`；`canReadComposeOutput` 对高级运营在团队校验后直接放行，普通运营仍校验负责游戏与本人成片 |

管理员未改动；策略负责人“须负责该游戏”的硬匹配规则未改动；`operator_scope` 参数保留兼容，页面不再发送，合同不新增参数、不改响应结构。

## 自动验证

### Cloud Go

命令（Cloud 仓根）：

```text
go test ./internal/modules/production/...
go test ./...
```

实际：`go test ./...` 72 个包 ok、0 FAIL（另有 11 个包无测试文件）；production 子集全通过。

关键用例与读数：

| 用例 | 断言 | 结果 |
| --- | --- | --- |
| `TestComposeListScopePerRole` | 高级运营空 scope：`TeamID=7, OperatorID=0, IncludeUnowned=0`；显式 `mine`：`11/11`；显式 `team`：`0/0`；指定成员：`OperatorID=9`；跨团队仍拒绝 | PASS |
| `TestListComposeTasksScopesByRole` | 高级运营默认／`team`／指定成员三臂下发的 `GameIDs` 均为空；普通运营仍为 `["delta"]` | PASS |
| `TestComposeTaskSeniorReadsEveryGameOfTheirTeam` | 同团队 `omega` 游戏、负责人为他人：可读；团队 8 同游戏：`ErrComposeTaskNotFound` | PASS |
| `TestListComposeOutputsSeniorSeesTeamScopeNotOnlyOwn` | 高级运营空 scope 下发 `TeamID=7, OperatorID=0, GameIDs=[]` | PASS |
| `TestComposeOutputSeniorReadsEveryGameOfTheirTeam` | 同团队另一游戏成片可读；团队 8 成片不可读 | PASS |
| `TestComposeOperatorOptionsKeepOnlyEnabledTeamResponsiblePeople` | 团队目录不指定游戏时返回高级运营本人 11 与运营 9、14 | PASS |

### Cloud Web

命令（必须在 `web/` 下）：

```text
npm test -- --run
```

实际：`79` 个测试文件、`729` 个用例全部通过。

关键断言：

- `ComposeTasksPage.test.js` / `MyOutputsPage.test.js`：负责人选项只由 `operatorOptions` 映射；不出现 `value: 'mine'` / `value: 'team'`；不出现默认 `mine`；不出现 `params.operator_scope`；选中成员只发 `operator_id`。
- 目标文件单跑：`ComposeTasksPage.test.js` 31 个用例、`MyOutputsPage.test.js` 6 个用例通过。

## 真实页面走查

待用户按 CHG-104 人工验收清单 A5／A8 执行：

- `senior01` 负责人下拉含本人与 `operator01`，无“我的／团队全部”。
- 未选择时列表含团队 1 全部游戏的任务／成片（任务 329 与 312/303/299；成片 72/73）。
- 选中 `operator01` / `senior01` 后按成员收窄。
- 任务 312 可读可重试，任务 329 仍不可重试。

走查环境事实（2026-10-27 00:57 审计记录）：管理员把 `senior01` 的负责游戏改为 `hy,sjz`，并停用 `other` 游戏；团队 1 的历史任务 329/330 仍在。本次任务／成片列表按团队返回，不按游戏启停过滤；素材库游戏筛选项来自启用游戏，清空后仍列出 `other` 素材。

走查结果由用户回报后补入本节。

## 覆盖边界

- 本机没有 `senior01` 登录口令，未以高级运营会话发起真实 HTTP；角色分支由 production service 用例覆盖，页面行为待用户走查。
- 普通运营范围未改变：仍固定本人并保留负责游戏，既有真实 HTTP 读数见 `T-06-team-scope-and-filters.md`。

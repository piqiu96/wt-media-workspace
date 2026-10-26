# T-04 高级运营团队范围与移除创建者门禁

Cloud 提交：`f9c3114`

## 代码变更

- `service/strategy.go`
  - `inGameScope`：高级运营在团队匹配后直接通过，不再要求 `actor.GameIDs` 含策略游戏；管理员、普通运营分支不变。
  - `List`：高级运营只设 `filter.TeamID`，不再设 `filter.GameIDs`；普通运营仍保留 `GameIDs` 与 `OperatorID`。
  - `Get`/`Update`/`Copy`/`SetStatus` 走 `managed`，`RunNow`/`ListRuns`/`RunHistory`/`Batch` 走 `canReadStrategy`，均经 `inGameScope` 继承同一团队范围。
  - `resolveComposeOperator` / `composeOperatorAvailable` 未改：策略负责人仍须启用、属于该团队且负责该游戏。
- `repository/schedule_mysql.go`：删除创建者状态查询与 `creator_disabled` 跳过分支；运行只保留 `operator_unavailable` 人员门禁，`created_by` 仍写策略创建者。
- `service/strategy_test.go`、`service/compose_scheduler_test.go`、`repository/schedule_pool_live_test.go`：改写并新增用例。

## 用例

| 层级 | 用例 | 断言 |
| --- | --- | --- |
| service | `TestStrategySeniorManagesEveryGameOfTheirTeam` | 高级运营可为团队内其他游戏的策略建策略；跨团队创建仍 `ErrStrategyForbidden` 且无写入 |
| service | `TestStrategySeniorScopeIsTheTeamNotTheirOwnGames` | 高级运营 List 不带 `GameIDs`、可读其他游戏策略、无游戏分配仍可读；普通运营仍被游戏范围拒绝；跨团队 NotFound，List 按本人团队过滤 |
| service | `TestComposeBatchViewScopesReadbackAndCarriesCounts`、`TestComposeScheduleRunsScopedReadback`、`TestComposeScheduleRunHistoryScopesAndPassesFilters` | 高级运营 `GameIDs=["other"]` 可读团队内策略的 batch/runs/history；跨团队 NotFound |
| service | `TestComposeRunNowUsesTheSeniorTeamScope` | 高级运营可对团队内其他游戏的策略 `RunNow`；跨团队 NotFound |
| service | `TestStrategyOperatorReadsAvailableTeamStrategyButCannotWrite` | 普通运营仍设 `TeamID`、`GameIDs`、`OperatorID`，且不能写 |
| live | `TestLiveComposeScheduleReadsTheTeamPoolWithoutPersonalUsages`（T-04 段） | 事务内禁用创建者后运行策略：`CreatedCount=1`、无 `creator_disabled` 跳过、任务 `created_by` 仍为被禁用创建者 |

## 真实 DB 读数

命令（2026-10-27 03:24，本机 `wt_media_cloud`）：

```text
WT_MEDIA_TEST_LIVE_DB=1 WT_MEDIA_CLOUD_HOME=$PWD \
  go test ./internal/modules/production/repository/ \
  -run TestLiveComposeScheduleReadsTheTeamPoolWithoutPersonalUsages -count=1 -v
```

| 观测 | 实测 |
| --- | --- |
| 团队素材池 | `strategy=62 team=1 material=162 candidates=60 created=1` |
| 跨游戏跳过 | 45 条 `other_game` |
| 禁用创建者仍生产 | `disabled creator strategy=63 created=1 task_created_by=1` |
| 人工路径保留 usage | `manual task=348 usage=1 material=153` |

事务回滚后复核：用户 1 `enabled`；`compose_strategies=0`、`compose_tasks=0`、`compose_schedule_runs=0`、`material_usages=44`，与运行前一致。

## 变异对照

1. 临时删除 `inGameScope` 的高级运营分支（恢复为只按 `GameIDs` 判断）后，`go test ./internal/modules/production/service/` 恰有 6 条用例失败：

   ```text
   --- FAIL: TestComposeBatchViewScopesReadbackAndCarriesCounts
   --- FAIL: TestComposeScheduleRunsScopedReadback
   --- FAIL: TestComposeScheduleRunHistoryScopesAndPassesFilters
   --- FAIL: TestComposeRunNowUsesTheSeniorTeamScope
   --- FAIL: TestStrategySeniorManagesEveryGameOfTheirTeam
   --- FAIL: TestStrategySeniorScopeIsTheTeamNotTheirOwnGames
   ```

2. 临时在 `schedule_mysql.go` 重新加入创建者状态门禁后，同一 live 用例失败：

   ```text
   disabled creator run={... CandidateCount:0 CreatedCount:0 Skipped:[{MaterialID:0 Reason:creator_disabled}] ...}
   --- FAIL: TestLiveComposeScheduleReadsTheTeamPoolWithoutPersonalUsages
   ```

两处变异均已还原，Cloud 工作树 `git status --short` 为空。

## 门禁

- `go build ./...`：通过。
- `go test ./...`：exit 0；72 包 ok，0 FAIL，11 包无测试文件。
- Cloud Web（`web/` 下 `npm test -- --run`）：80 文件 / 737 用例全部通过。

## 覆盖边界

- `TestLiveStrategyRulesRoundTripAndImmediateRun`：仍 FAIL 于 `operator_unavailable`，夹具策略未设 `OperatorID`。该缺口自 CHG-103 起存在（T-02 时同样失败），T-07 统一改造，不计入本 Task。
- `TestLiveComposeScheduleDueAndRepeatScan`：仍 SKIP（本机 `compose_strategies` 为 0 条），T-07 建真实夹具后执行。
- PRD 第五章第 392/436 行已写“高级运营创建和维护本团队全部游戏策略、启停及主动执行”，与新行为一致，本 Task 不改产品文档；T-08 统一同步剩余文档。
- 负责人“须负责该游戏”的硬匹配未放宽，与用户 2026-10-27 裁定一致（只放宽管理范围与列表筛选）。

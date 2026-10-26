# T-03 候选切换到策略团队素材池

Cloud 提交：`ac3a776`

## 代码变更

- `listComposeScheduleCandidates` 改为 `materials m JOIN source_contents sc WHERE m.team_id = ?`，不再 `JOIN material_usages`，也不再按 `sc.game_id` 过滤；`sc.game_id` 仍随行返回，`composeCandidateSkipReason` 的 `other_game` 口径不变，`candidate_count` 仍是团队全量候选数。
- `scheduleCandidate` 删除 `UsageID`；自动建任务不再写 `material_usage_id`（列为 NULL），不再出现“替某人加入素材”的副作用。
- `createForUsage`（人工“我的素材”入口）保持写非空 usage。
- `schedule_live_test.go` 的策略选取去掉“创建者必须有 usage”，改为“策略有可用负责人”，并断言自动任务的 `material_usage_id` 必须为 NULL。

## 新增 live 用例读数

命令：

```text
WT_MEDIA_TEST_LIVE_DB=1 WT_MEDIA_CLOUD_HOME=$PWD \
  go test ./internal/modules/production/repository/ \
  -run TestLiveComposeScheduleReadsTheTeamPoolWithoutPersonalUsages -count=1 -v
```

实测（2026-10-27，本机 `wt_media_cloud`）：

| 断言 | 实测 |
| --- | --- |
| 候选人 = 团队全部素材 | `candidates=60`（团队 1：`hy` 15 + `other` 26 + `sjz` 19） |
| 创建者与负责人均未加入仍入选 | 选中素材 162，创建者 `admin`(1)、负责人 `operator`(3) 在该素材上 usage 均为 0 |
| 跨团队不入选 | 其他团队素材 ID 不在候选集 |
| 同团队跨游戏记 `other_game` | 一次运行记录 46 条 `other_game` |
| 自动任务归属与 usage | 任务 `operator_id=3`、`created_by=1`、`material_usage_id IS NULL`；运行后 creator/operator 在该素材上的 usage 仍为 0 |
| `previously_run` | 同 (策略,素材) 换 key 再跑，`CreatedCount=0` 且该素材记 `previously_run` |
| `material_unavailable` | 直接调用 skip 判定，`status=paused` 返回 `material_unavailable` |
| 人工路径保留 usage | `createForUsage` 建任务 338，`material_usage_id=1`（素材 153） |

事务回滚后复核：`compose_strategies=0`、`compose_tasks=0`、`compose_schedule_runs=0`、`material_usages=44`（与运行前一致）。

## 变异对照

把候选查询临时改回“创建者(用户 1)必须有 usage”的 `EXISTS` 条件后，同一用例失败：

```text
candidates=8 want every one of the team's 60 materials
```

说明该用例能区分“团队素材池”和旧的“创建者个人素材”；改动已还原。

## 门禁

- `go build ./...`：通过。
- `go test ./...`：exit 0；72 包 ok，0 FAIL。

## 覆盖边界

- `TestLiveComposeScheduleDueAndRepeatScan`：仍 **SKIP**（本机 `compose_strategies` 为 0 条，选取不到“有可用负责人的活动策略”）；用例本身已改为新语义，T-07 建真实夹具后会实际执行。
- `TestLiveStrategyRulesRoundTripAndImmediateRun`：仍 **FAIL** 于 `operator_unavailable`，夹具策略未设 `OperatorID`。这是 CHG-103 起就存在的既有 live 用例缺口（T-02 时同样失败，与本 Task 无关），T-07 统一改造；不作为本 Task 的通过项。

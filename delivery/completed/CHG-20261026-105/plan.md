# CHG-20261026-105 实施计划

## 1. 当前事实与约束

- `repository/schedule_mysql.go:421` 的候选查询是 `material_usages mu JOIN materials m JOIN source_contents sc`，条件为 `mu.user_id = strategy.CreatedBy`；自动任务在 `:328` 把 `candidate.UsageID` 写入 `compose_tasks.material_usage_id`。创建者未加入的素材永远不会成为候选。
- `schedule_mysql.go:270-275` 还有 `creator_disabled` 跳过分支：策略创建者被禁用时，即使负责人有效也不建任务。
- `compose_tasks.material_usage_id` 与 `composite_outputs.material_usage_id` 当前 `NOT NULL` 且模型为 `int64`，自动任务没有个人 `material_usage` 可写。
- `service/strategy.go:122-126` 对非管理员按 `actor.GameIDs` 收窄策略列表，`inGameScope` 要求高级运营同时匹配团队与本人负责游戏；这与“高级运营管理本团队所有游戏策略”不一致。
- `service/compose_scheduler.go` 的 `Batch` 在 `FindRun` 无结果时返回零值 run；OpenAPI 没有 `GET /compose-strategies/{id}/runs/tasks`。
- `contracts/business-schemas/v1/content-production.yaml` 的 `material_scope` 仍是 `[creator_usages]`；历史 `schedule_json` 保留旧值，不重写。
- 团队 1 / `hy` 的所有 ready 素材都已有 `admin`(1) 或 `operator01`(3) 的 `material_usage`；T-01 需用内容池真实 `Materialize` 路径生成一条无任何 usage 的素材夹具（来源 906，`like_count` 258365 在 `hy` 内唯一）。

## 2. 明确不修改

- 不新建 `compose_pool`、batch 表或系统用户；不把创建者/负责人工作集关系作为自动候选条件。
- 不改人工“我的素材”入口与 `createForUsage`：人工任务仍写非空 `material_usage_id`。
- 不改负责人“须负责该游戏”的硬匹配；不开放他人本机文件、BitBrowser、Profile、Cookie。
- 不改 `material` 入库、视频准备状态机、`file_transfer_task` 合同；M6 发布不在范围。
- 不重写历史 `schedule_json` 的 `creator_usages`，只在合同中保留兼容并注明新写入为 `team_materials`。

## 3. 结构决策

1. 迁移 075 把两表 `material_usage_id` 改为 `BIGINT UNSIGNED NULL`，保留外键；Go 模型改 `*int64`，JSON tag 不加 `omitempty`（键在、值可为 `null`）；扫描用 `sql.NullInt64` 中转。
2. 候选查询只按策略 `team_id` 取 `materials`（**不把 `sc.game_id` 加进 WHERE**），保留“团队全量候选 + `other_game` 跳过”语义与 `candidate_count`；删除 `material_usages` join。
3. 移除 `creator_disabled` 门禁；创建者只保留为 `created_by` 审计来源。`operator_unavailable` 仍是唯一人员门禁。
4. 高级运营策略范围改为本团队（`inGameScope` 只校验团队，`List` 不再按 `actor.GameIDs` 收窄）；普通运营与管理员不变。
5. `/runs/tasks` 在无 run 时返回 404，不返回零值 run；合同补 `ComposeBatchView`/`ComposeBatchCounts`。

## 4. 任务

| Task | 内容 | 验证 | 提交边界 |
| --- | --- | --- | --- |
| T-01 | 激活：移到 active、`PLANNED → IMPLEMENTING`、LEDGER/planned README/里程碑同步、`wt chg start`；用真实 `Materialize` 生成来源 906 的素材夹具并记录 | `pgrep` 无旧 worker/scheduler；夹具 `status=available`、`video_status=not_downloaded`、创建者/负责人 usage 均为 0；激活记录一致 | Workspace 记录 |
| T-02 | 迁移 075：两表 `material_usage_id` 可空、保留外键；模型 `*int64`；`createForUsage` 写 `&usage.ID`；`execution.go` 指针传递；`output.go` 判空；trace/`ComposeOutputDetail.vue` 空值显示 `—`；更新直接扫 `material_usage_id` 的 live 用例与硬编码 `NOT NULL` 的迁移测试 | 迁移应用与 `SHOW COLUMNS` 读回；Go 全量（含 `wire_test.go` 键集）；Vitest null-trace；`verify_m0_config.py` | Cloud 后端/合同/Web + Workspace 映射 |
| T-03 | 候选切换：`schedule_mysql.go` 只按策略团队取 `materials`，删 `UsageID` 与 `material_usages` join；自动任务 `material_usage_id=NULL`；保留 status/`previously_run`/额度/优先级/跳过原因 | repository 用例：创建者与负责人均未加入仍有候选；跨团队不入选；跨游戏记 `other_game`；paused/delisted 记 `material_unavailable`；已有任务记 `previously_run`；manual 路径仍有非空 usage | Cloud 后端 |
| T-04 | 门禁与范围：删除 `creator_disabled` 查询与分支；`inGameScope` 高级运营只校验团队；`List` 不再按负责游戏收窄；`Get`/`RunNow`/`ListRuns`/`RunHistory`/`Batch` 继承团队范围；不改 `resolveComposeOperator` | 高级运营可读/建/运行本团队非本人负责游戏的策略；普通运营/跨团队仍拒绝；禁用创建者的到期策略仍建任务且 `created_by` 不变；无 `creator_disabled` 跳过；失效负责人仍记 `operator_unavailable` | Cloud 后端 + Workspace 文档 |
| T-05 | 合同缺口：OpenAPI 增加 `GET /compose-strategies/{id}/runs/tasks`（`schedule_slot` 必填 RFC3339）、`ComposeBatchView`/`ComposeBatchCounts`、`material_usage_id` nullable；`Batch` 无 run 返回 404；Business Schema `material_scope` 改 enum `[team_materials, creator_usages]`；bump revision 与 contract-map | OpenAPI 解析；`verify_m0_config.py`；handler/service 返回 run/tasks/counts 与无 run 404；`material_usage_id: null` 通过 schema；旧 `creator_usages` 仍被接受 | Cloud 合同 + Workspace 映射 |
| T-06 | 真实定时全链：fixture 策略（团队 1/`hy`/负责人 `operator01`、创建者 `admin`）设 `next_run_at`；独立 `compose-scheduler` + Cloud `worker`（源准备）+ `compose-worker`（真实 FFmpeg、对象存储）；规则只选中夹具来源 | 真实 DB/API/对象 Stat/FFprobe：任务 `trigger_type=scheduled`、`operator_id=3`、`created_by=1`、两表 `material_usage_id IS NULL`；成片 `pending_publish`；创建者/负责人无新增 usage；源文件准备完成 | Workspace 证据 |
| T-07 | 立即执行与并发回归：真实 HTTP `POST /run-now`；同 `request_key` 重放同一 run；同 (策略,素材) 换 key 得 `previously_run`；双 scheduler（含重启）只建一个任务；双 worker 抢同一素材各领一次并产出两个不同成片；回归额度、部分失败、旧任务重试、人工入口、跨团队/跨游戏/负责人失效 | 真实进程与 DB 计数；重复扫描 0 新增；两成片对象不同；go test 全量；证据记录进程与耗时 | Workspace 证据 |
| T-08 | 文档与收尾：PRD §5.6.1/§5.7、工程规格、ADR-0023 2026-10-27 追加决议、M5 里程碑 M5-F 与 §3/§8、MASTER §3；CHG 记录、evidence、PR、CI、merge、DONE、归档；只有 M5-F 置 DONE，M5 总体保持 IN_PROGRESS | 文档同步检查、`wt chg verify`、PR CI、LEDGER 无 105、四仓干净 | Workspace 记录 |

## 5. 验证命令

```text
Cloud: go test ./internal/modules/production/... -count=1
Cloud: go test ./...
Cloud web（web/ 下）: npm test -- --run
Workspace: python3 scripts/verify/verify_m0_config.py
Workspace: python3 scripts/wt.py chg verify CHG-20261026-105
```

真实链路按 T-06/T-07 启动独立 `compose-scheduler`、Cloud `worker`、`compose-worker`；记录进程、DB 读回、对象 Stat/SHA-256/FFprobe 与 API/页面结果。已知 `verify_m1_integration.py` 基线失败（Agent 仓 `cloud_agent_client` 已退役）不计入本 CHG 回归。

## 6. 风险与边界

- **候选池变大**：跨游戏素材仍记 `other_game`，不得从 `candidate_count` 中悄悄拿掉而改变口径。
- **历史数据**：旧任务/成片的 `material_usage_id` 保持原值；只有新自动任务为 NULL，不回填。
- **live 测试**：`schedule_live_test.go` 直接扫 `material_usage_id`，NULL 会报错；`schedule_process_live_test.go`、`strategy_rules_live_test.go`、`batch_live_test.go` 仍按创建者 usage 造数，不改会静默 skip 或证明旧语义。
- **禁用创建者**：运行不再被其状态阻断，需 ADR/PRD 明写并加回归。
- **并发证据**：必须真实双进程，不以单进程重复调用冒充。
- **里程碑口径**：105 归档只把 M5-F 置 `DONE`；M5 总体保持 `IN_PROGRESS`，直到 CHG-098 验收 M5-AC-13。

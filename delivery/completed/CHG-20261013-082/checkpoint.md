# CHG-20261013-082 Checkpoint

## Completed

- 前置核对：CHG-20261012-081（M4-C2 策略交付）已归档、用户走查通过；Cloud 迁移至 052（无 `compose_task` 表）；执行器 `basic_cut` v1、模板 id=6、策略 API/页面、我的素材模块均就绪。
- CHG 记录已建立（本文件与 `change.md`），范围裁定见 `change.md` §7。
- T-01 迁移 053 + 合同 2026.10.13.2 完成：迁移片段测试红先绿后，四+六份合同 YAML 解析通过，15214~15217 错误码核查空闲后预留。证据见 `evidence/T-01.md`。Cloud commit `21ac3a3`。
- T-02 模型与 Repository 完成：审计事务创建（MaxAttempts 缺省 3）、pending 单条件 UPDATE 取消、范围过滤列表、事务内 active usage 读回；sqlmock 5 例红先绿后。证据见 `evidence/T-02.md`。Cloud commit `1f1eb64`。
- T-03 Service 完成：命令级门（策略可读且 active、模板可用、override 深合并过同一 schema 校验器、request_key/批内约束）先于逐素材处理且零写入；request_key 先于素材校验解析实现重试幂等；usage 校验与插入同事务（`CreateForUsage`）；取消=读取消同一可见性门 + 仅 pending 条件 UPDATE + 取消者审计（`cancelComposeTaskAudited` 取代 T-02 裸取消）；列表 admin 全局/senior 队内/operator 限本人。定向用例 11 组 + sqlmock 4 例红先绿后，具名失败全部零写入。证据见 `evidence/T-03.md`。

- T-04 Handler 与路由完成：`composeTaskErrorFor` 单点映射哨兵→（状态/errcode/冻结名），整命令错误与 per-item 信封共用；四条路由注册；冻结名单入 `content-production.yaml`（revision 2026.10.13.1）。四例红先绿后。证据见 `evidence/T-04.md`。

- T-05 共用页面完成：compose client 四命令；创建对话框（选策略 + schema 覆盖参数 + 打开时生成稳定 request_key）；我的素材勾选列（非 active disabled）+ 行内/批量两个入口 + created/failed 分列提示；合成任务页（服务端筛选、五状态、pending 阶段钉「等待源素材」、DialogPlugin 确认取消、详情含快照全文）；两端 compose 路由换真实页并加 parity 守卫。8 处断言红先绿后。证据见 `evidence/T-05.md`。

- T-06 真实 MySQL/API 验收完成：16 项矩阵全 PASS（幂等对照同 id 零新行、override 合并快照读回、策略改后快照不变、schema 外参数/跨队策略/移出与无 usage/跨队素材/停用策略/取消非 pending 全部具名失败且零写入、列表筛选与 admin 全局、列表↔详情一致、senior game 维度隔离）；审计 4 create + 1 cancel；验收后 compose_tasks 与 compose_task 审计清零、策略 11 config/status 与 usage 8/9/13 还原。两处如实登记：operator+inactive 策略折叠为 15216（canReadStrategy 对 operator 要求 active，admin 命中 15214 分支）；senior01 密码重置回约定值。证据见 `evidence/T-06.md`。本任务无代码变更，不产生 Cloud commit。

- T-07 全量回归与证据收口完成：Go 71 包 ok 0 FAIL（vet 干净）、vitest 58 文件 524 例全 PASS、双构建通过、两仓 diff check 干净（workspace 仅既有 AGENTS.md 改动，未触碰）；change.md §5 五条验收标准逐条对照证据收口于 `evidence/T-07.md`。补测 T-06 矩阵遗漏的两条枚举（P1 模板停用后旧快照不变 + 新创建 15213；P2 同素材换策略各自快照），已并入 `evidence/T-06.md`，二次清零完成。CHG 置 DONE 待用户验收。

## Current

无进行中任务。CHG-20261013-082 七个任务全部完成，等待用户验收（页面人工走查 + §5 确认）后归档。

## Next

用户验收通过后：CHG 归档（移出 delivery/active、LEDGER 更新），随后按里程碑顺序进入 M4-C5（合成任务执行）。

## Blockers

None.

## Recent verification

- `go test ./internal/modules/... -count=1` 全 PASS；`go build ./...` / `go vet` 通过。
- diff check：Cloud 仅 4 个 compose-task 文件变更，无范围外改动。
- `go test ./internal/modules/production/ -count=1` 全 PASS；路由⇄合同比对一致。
- `npx vitest run` 58 文件 524 例全 PASS；`npm run build:desktop` / `npm run build` 通过。
- `verify_delivery_governance.py` PASS（exit 0）。T-03 工作区提交时 Milestone 行带括号注记未匹配校验器正则，已把注记移入 Closure anchor 行修复；此前 T-01/T-02 提交携带同一问题但未记录治理结论。
- T-06：真实 API 16 项矩阵全 PASS；清零后复测 compose_tasks 0 行、compose_task 审计 0 条、usage 8/9/13 active、策略 11 active 且 config 还原。
- T-07：`go vet ./...` 干净、`go test ./... -count=1` 71 包 ok 0 FAIL；web/ 下 `npx vitest run` 58/524 全 PASS；`npm run build` 6.80s / `npm run build:desktop` 6.69s 通过；治理 exit 0。

# CHG-20261013-082 Checkpoint

## Completed

- 前置核对：CHG-20261012-081（M4-C2 策略交付）已归档、用户走查通过；Cloud 迁移至 052（无 `compose_task` 表）；执行器 `basic_cut` v1、模板 id=6、策略 API/页面、我的素材模块均就绪。
- CHG 记录已建立（本文件与 `change.md`），范围裁定见 `change.md` §7。
- T-01 迁移 053 + 合同 2026.10.13.2 完成：迁移片段测试红先绿后，四+六份合同 YAML 解析通过，15214~15217 错误码核查空闲后预留。证据见 `evidence/T-01.md`。Cloud commit `21ac3a3`。
- T-02 模型与 Repository 完成：审计事务创建（MaxAttempts 缺省 3）、pending 单条件 UPDATE 取消、范围过滤列表、事务内 active usage 读回；sqlmock 5 例红先绿后。证据见 `evidence/T-02.md`。Cloud commit `1f1eb64`。
- T-03 Service 完成：命令级门（策略可读且 active、模板可用、override 深合并过同一 schema 校验器、request_key/批内约束）先于逐素材处理且零写入；request_key 先于素材校验解析实现重试幂等；usage 校验与插入同事务（`CreateForUsage`）；取消=读取消同一可见性门 + 仅 pending 条件 UPDATE + 取消者审计（`cancelComposeTaskAudited` 取代 T-02 裸取消）；列表 admin 全局/senior 队内/operator 限本人。定向用例 11 组 + sqlmock 4 例红先绿后，具名失败全部零写入。证据见 `evidence/T-03.md`。

- T-04 Handler 与路由完成：`composeTaskErrorFor` 单点映射哨兵→（状态/errcode/冻结名），整命令错误与 per-item 信封共用；四条路由注册；冻结名单入 `content-production.yaml`（revision 2026.10.13.1）。四例红先绿后。证据见 `evidence/T-04.md`。

## Current

T-05：共用页面——「我的素材」多选创建入口（选策略 + schema 渲染可覆盖参数）+「合成任务」页（列表/筛选/详情/排队中取消）。

## Next

T-06 真实 MySQL/API 验收 → T-07 全量回归。

## Blockers

None.

## Recent verification

- `go test ./internal/modules/... -count=1` 全 PASS；`go build ./...` / `go vet` 通过。
- diff check：Cloud 仅 4 个 compose-task 文件变更，无范围外改动。
- `go test ./internal/modules/production/ -count=1` 全 PASS；路由⇄合同比对一致。
- `verify_delivery_governance.py` PASS（exit 0）。T-03 工作区提交时 Milestone 行带括号注记未匹配校验器正则，已把注记移入 Closure anchor 行修复；此前 T-01/T-02 提交携带同一问题但未记录治理结论。

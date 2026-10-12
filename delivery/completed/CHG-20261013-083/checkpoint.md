# CHG-20261013-083 Checkpoint

## Completed

- 前置核对：CHG-20261013-082（M4-C3）已归档（用户授权不等待单项验收，2026-10-14 晨统一验收）；`cmd/compose-worker`（M4-C4 验证壳）、`compose.Runner/Workspace/Lock`、执行器注册表、`filetransfer` 模块（`compose_input_prepare`）与 material_prepare 投影均在；`compose_task` 迁移 053 已应用。
- CHG 记录已建立（本文件与 `change.md`），范围裁定见 `change.md` §7。
- T-01 完成：迁移 054（composite_outputs + compose_tasks.cancel_requested）红先绿后并已应用 dev 库（1 applied, 56 total）；openapi cancel 语义修订 + ComposeTask.cancel_requested + 错误码 revision 2026.10.14.1；migration/production 两包测试全绿。证据见 `evidence/T-01.md`。Cloud commit `151baed`。
- T-02 完成：生命周期 Repository（领取 FOR UPDATE SKIP LOCKED + 条件翻转、续租/进度、running 取消请求+确认、CommitComposeOutput 同事务成片、requeue/终态失败、过期租约扫描）11 例 sqlmock；ComposeTask.CancelRequested 与 CompositeOutput 模型落位。证据见 `evidence/T-02.md`。Cloud commit `eb3ad0a`。
- T-03 完成：执行状态机 `RunComposeAttempt`（快照预校验→输入就绪门→执行→校验上传→同事务提交）10 组用例；业务/临时失败分类、取消检查、孤儿清理；变异对照补「能红」证明。证据见 `evidence/T-03.md`。Cloud commit `be295ad`。
- T-04 完成：Worker 运行时——`cmd/compose-worker` 升级为领取循环（`-input` 保留验证模式），心跳续租、cancel_requested 轮询受控终止、wait_input 原地重试不烧 attempt、超时同终止路径（预算尽终态化）、启动+周期恢复扫描（requeue/终态）、6+1 配置旋钮非法拒启（config-check 对真实树 PASS）；两处变异对照可红。证据见 `evidence/T-04.md`。Cloud commit `cb09319`。
- T-05 完成：API——running 取消走 `RequestComposeCancel` 并以 `running + cancel_requested` 应答，终态才 409 15217（文案同步收窄）；openapi 409/stage 描述修订（stage 为 worker 有限枚举，pending 为空）；ComposeTask 投影键集合与 openapi schema 全等比对；红先确认后实现。证据见 `evidence/T-05.md`。Cloud commit `30bb4ff`。
- T-06 完成：真实 MySQL/API/FFmpeg 验收全链路（成片、快照遵循、取消 running、失败无假成片、租约恢复、双实例拒启、数据清零）七探针全 PASS；过程中发现并修复「取消旗标骑进领取」真 bug（红先用例 + 实机确认，Cloud commit `3ea646d`）。残留与披露见 `evidence/T-06.md`（审计行保留、崩溃孤儿目录人工处置、161 源对象重播）。

## Current

无进行中任务。

## Next

无——T-07 完成（Go 71 包全绿、web vitest 524 例全绿、governance verify exit 0），CHG 标记 DONE 并归档至 `delivery/completed/`。用户单项验收并入 2026-10-14 M4 统一验收；下一 CHG084（M4-C6 我的成片）随后开启。

## Blockers

None.

## Recent verification

- `go test ./internal/modules/production/... -count=1` 六包全 PASS；`go build ./...`、`go vet` 通过。

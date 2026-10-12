# CHG-20261013-083 Checkpoint

## Completed

- 前置核对：CHG-20261013-082（M4-C3）已归档（用户授权不等待单项验收，2026-10-14 晨统一验收）；`cmd/compose-worker`（M4-C4 验证壳）、`compose.Runner/Workspace/Lock`、执行器注册表、`filetransfer` 模块（`compose_input_prepare`）与 material_prepare 投影均在；`compose_task` 迁移 053 已应用。
- CHG 记录已建立（本文件与 `change.md`），范围裁定见 `change.md` §7。
- T-01 完成：迁移 054（composite_outputs + compose_tasks.cancel_requested）红先绿后并已应用 dev 库（1 applied, 56 total）；openapi cancel 语义修订 + ComposeTask.cancel_requested + 错误码 revision 2026.10.14.1；migration/production 两包测试全绿。证据见 `evidence/T-01.md`。Cloud commit `151baed`。
- T-02 完成：生命周期 Repository（领取 FOR UPDATE SKIP LOCKED + 条件翻转、续租/进度、running 取消请求+确认、CommitComposeOutput 同事务成片、requeue/终态失败、过期租约扫描）11 例 sqlmock；ComposeTask.CancelRequested 与 CompositeOutput 模型落位。证据见 `evidence/T-02.md`。Cloud commit `eb3ad0a`。
- T-03 完成：执行状态机 `RunComposeAttempt`（快照预校验→输入就绪门→执行→校验上传→同事务提交）10 组用例；业务/临时失败分类、取消检查、孤儿清理；变异对照补「能红」证明。证据见 `evidence/T-03.md`。Cloud commit `be295ad`。

## Current

无进行中任务。

## Next

T-04 Worker 运行时（主循环、并发/超时/租约配置、取消终止、恢复扫描、配置缺失拒启）。

## Blockers

None.

## Recent verification

- `go test ./internal/modules/production/... -count=1` 五包全 PASS；`go build ./...` 通过。

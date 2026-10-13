# CHG-20261013-089 Checkpoint

## Completed

- 规划完成：闭环节点、PRD 依据、重试边界（用户确认三类规则）均见 change.md。
- T-01 合同与迁移：compose_task_attempts 表迁移（20261014_056）、ComposeTaskAttempt 合同与 wire 测试、详情输出 composite_output_id。Cloud 提交 `2e99dfd`，evidence/T-01.md。
- T-02 Worker 尝试记录与两端点：claim/commit/fail/requeue/fail-expired/cancel 全路径写入并关闭尝试行；GET attempts / POST retry 端点、409 compose_task_not_retryable、senior 权限门、人工重试审计。测试全绿，Cloud 独立提交 `7468ff9`，evidence/T-02.md。
- T-03 页面：详情弹窗按「任务状态 → 失败信息 → 快照 → 执行记录 → 成片」重排；重试按钮按错误码分类 + 角色双门，不可重试类只给新建任务引导；成片 ID + 跳转我的成片。页面/client 测试 14 个全绿，Cloud/Desktop 双构建通过，evidence/T-03.md。

## Current

T-03 已完成，准备进入 T-04 回归与交付收口。

## Next

T-04：全量 Go/Web 回归、真实 MySQL 迁移读回；验收记录写入 change.md；归档 CHG089、LEDGER 移除、M4-G → DONE、prepare_ai_workspace --no-active、workspace 提交。真实失败任务的重试链路走查按 change.md 留 M4-H。

## Blockers

None.

## Recent verification

- `go -C /Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud test ./internal/modules/production/...` 全绿（production/repository/service/compose/executor）。
- `go -C ... build ./...` 通过；触及文件 gofmt 无输出。
- diff 检查：Cloud 工作集仅 T-02 范围内 8 文件。

# CHG-20261015-096 Checkpoint

## Completed

- 依据 M5 闭环、CHG095 归档结论和 Cloud 当前代码建立本 CHG；确认当前无其他 Active CHG，Workspace 与 Cloud 工作区起点均干净。
- T-01：数据库级 `next_attempt_at` 和 30 秒～15 分钟指数退避已实现；先红、Repository、真库资格读回与定向 Cloud 回归见 `evidence/T-01.md`。Cloud 提交 `12604a0`。

## Current

- T-01 已独立提交；开始 T-02 错误分类。

## Next

1. T-02：业务/技术/不明确错误分类与取消、失租拒绝重试。
2. T-03～T-04 依次执行，不提前声明机器验收。

## Blockers

- None.

## Recent verification

- T-01：迁移 1 applied；定向 Go 测试和真库资格读回 PASS，见 `evidence/T-01.md`。

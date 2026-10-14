# CHG-20261015-096 Checkpoint

## Completed

- 依据 M5 闭环、CHG095 归档结论和 Cloud 当前代码建立本 CHG；确认当前无其他 Active CHG，Workspace 与 Cloud 工作区起点均干净。
- T-01：数据库级 `next_attempt_at` 和 30 秒～15 分钟指数退避已实现；先红、Repository、真库资格读回与定向 Cloud 回归见 `evidence/T-01.md`。Cloud 提交 `12604a0`。
- T-02：缺失源对象/临时存储/临时引导视频/输出校验/上下文取消分类已收敛；先红后绿和定向回归见 `evidence/T-02.md`。Cloud 提交 `eb89eab`。

## Current

- T-02 已独立提交；当前实施 T-03 临时对象安全处置。

## Next

1. T-03：每次领取隔离临时对象，失败/取消/提交后的清理和恢复扫描。
2. T-04：真进程与对象存储故障注入；不提前声明机器验收。

## Blockers

- None.

## Recent verification

- T-01：迁移 1 applied；定向 Go 测试和真库资格读回 PASS，见 `evidence/T-01.md`。
- T-02：Storage、Production、Jobs 定向 Go 包全部通过，见 `evidence/T-02.md`。

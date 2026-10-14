# CHG-20261015-096 Checkpoint

## Completed

- 依据 M5 闭环、CHG095 归档结论和 Cloud 当前代码建立本 CHG；确认当前无其他 Active CHG，Workspace 与 Cloud 工作区起点均干净。
- T-01：数据库级 `next_attempt_at` 和 30 秒～15 分钟指数退避已实现；先红、Repository、真库资格读回与定向 Cloud 回归见 `evidence/T-01.md`。Cloud 提交 `12604a0`。
- T-02：缺失源对象/临时存储/临时引导视频/输出校验/上下文取消分类已收敛；先红后绿和定向回归见 `evidence/T-02.md`。Cloud 提交 `eb89eab`。
- T-03：代次隔离对象键、已知回滚与未知提交结果的精确处置、staging 删除失败恢复扫描已实现；真库迁移与候选扫描及定向回归见 `evidence/T-03.md`。Cloud 提交 `05a7cf0`。

## Current

- T-03 已独立提交；当前执行 T-04 真依赖验收。

## Next

1. T-04：真 MySQL、Worker、FFmpeg、对象存储和故障注入；不提前声明机器验收。

## Blockers

- None.

## Recent verification

- T-01：迁移 1 applied；定向 Go 测试和真库资格读回 PASS，见 `evidence/T-01.md`。
- T-02：Storage、Production、Jobs 定向 Go 包全部通过，见 `evidence/T-02.md`。
- T-03：迁移 1 applied；真库清理候选读回与 8 个定向 Go 包通过，见 `evidence/T-03.md`。

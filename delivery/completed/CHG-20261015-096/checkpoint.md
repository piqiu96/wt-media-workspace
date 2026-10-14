# CHG-20261015-096 Checkpoint

## Completed

- 依据 M5 闭环、CHG095 归档结论和 Cloud 当前代码建立本 CHG；确认当前无其他 Active CHG，Workspace 与 Cloud 工作区起点均干净。
- T-01：数据库级 `next_attempt_at` 和 30 秒～15 分钟指数退避已实现；先红、Repository、真库资格读回与定向 Cloud 回归见 `evidence/T-01.md`。Cloud 提交 `12604a0`。
- T-02：缺失源对象/临时存储/临时引导视频/输出校验/上下文取消分类已收敛；先红后绿和定向回归见 `evidence/T-02.md`。Cloud 提交 `eb89eab`。
- T-03：代次隔离对象键、已知回滚与未知提交结果的精确处置、staging 删除失败恢复扫描已实现；真库迁移与候选扫描及定向回归见 `evidence/T-03.md`。Cloud 提交 `05a7cf0`。
- T-04：真 Worker 重启退避、真实 FFmpeg 中途取消、对象存储删除故障恢复、双进程领取/旧代次和 C4 批次与调度回归通过；完整证据见 `evidence/T-04.md`。Cloud 提交 `70c93ce`。
- CHG 验收 1–5 逐项通过，已归档至 `delivery/completed/`。

## Current

- Cloud 四个 Task 提交均已落地；M5-C5 机器验收完成。

## Next

1. 按主计划与当前事实建议 M5-C6（结果不明确的人工核对与处置），不在本 CHG 扩展范围。

## Blockers

- None.

## Recent verification

- T-01：迁移 1 applied；定向 Go 测试和真库资格读回 PASS，见 `evidence/T-01.md`。
- T-02：Storage、Production、Jobs 定向 Go 包全部通过，见 `evidence/T-02.md`。
- T-03：迁移 1 applied；真库清理候选读回与 8 个定向 Go 包通过，见 `evidence/T-03.md`。
- T-04：真 Worker、真库、真实 FFmpeg、对象存储故障注入与 C3/C4 回归通过；`go test ./... -count=1` 退出码 0。等待输入时取消旧用例因无合适素材跳过，见 `evidence/T-04.md`。

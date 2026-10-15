# CHG-20261015-097 Checkpoint

## Completed

- CHG096 已归档，Cloud 与 Workspace 工作区干净；用户确认管理员核实旧 FFmpeg 停止、无已提交成片并记录依据后，才可重试原任务。
- 已确定 Cloud 是新增 API 合同和业务状态的提供方，共用 Vue 页面由 Cloud 维护，Agent/Desktop 无运行时代码变更。
- T-01：兼容性 Cloud 合同、管理员明确声明和拒绝状态已固定；合同定向测试通过，见 `evidence/T-01.md`。Cloud 提交 `6ea61c7`。
- T-02：受保护单事务核对/重排、审计、迁移与真库读回完成；证据见 `evidence/T-02.md`。Cloud 提交 `0032eac`。
- T-03：GET/POST API、管理员页面、核对读回与脱敏诊断摘要已接线；Cloud/desktop 共用页面构建和定向测试通过，见 `evidence/T-03.md`。Cloud 提交 `7c335b1`。
- T-04：真库单次与并发处置、核对后旧暂存键真实删除、任务 API 错误摘要脱敏、C3/C4 真库及全量 Go/Web 回归通过；见 `evidence/T-04.md`。Cloud 提交 `d14016a`。
- T-04 脱敏补强：任务 API 的引导视频下载地址改为隐藏投影，执行快照仍保存在数据库；合同版本 `2026.10.15.2`，全量 Go/Web 再次回归通过。Cloud 提交 `fb6371b`。
- CHG097 验收 1–4 逐项通过，已归档至 `delivery/completed/`。

## Current

- M5-C6 机器验收完成，Cloud 四个 Task 提交均已落地。

## Next

1. 按主计划推进 M5-C7 的真实时间全链验收与 M4-H2 用户走查；不在本 CHG 扩展。

## Blockers

- None.

## Recent verification

- 起点 Workspace `2799961`、Cloud `70c93ce`，均为干净工作区；M5-C5 治理校验已通过。
- T-01：OpenAPI 解析与必填声明测试 PASS，Cloud `6ea61c7`。
- T-02：迁移 1 applied、真库单次处置/读回与 Repository/Service 定向测试 PASS，Cloud `0032eac`。
- T-03：Production Go 包、12 个 Vue 定向测试及 Cloud/Desktop 两种构建 PASS，Cloud `7c335b1`。
- T-04：真库并发/核对/清理、真 Worker、C3/C4 回归 PASS；`go test ./... -count=1`、Web 567 项 PASS。等待输入取消旧用例因缺少素材 SKIP，真实中途取消 PASS。

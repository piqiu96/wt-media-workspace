# CHG-20261014-091 Checkpoint

## Completed

- 用户确认 M4-H2 暂缓，与 M5 最终统一走查；M5 交付顺序已修正。
- 用户确认 C1/C2 素材范围为策略创建人的“我的素材”，跳过该策略已生产的素材。
- T-01：计划模式、数量上限、时区校验和下次执行时间计算已实现并通过定向测试，证据见 `evidence/T-01.md`。
- T-02：新迁移已在本地 MySQL 应用；旧策略读回和事务内计划写读回通过，路由、仓库、合同已接入，见 `evidence/T-02.md`。
- T-03：策略页已显示独立计划状态、下次时间、范围与限制；定向测试和双端构建通过，见 `evidence/T-03.md`。
- T-04：Go/Web 回归、Cloud 构建、diff 和 Delivery 校验通过；证据见 `evidence/T-04.md`。
- Cloud 已独立提交 `6124dab`。

## Current

- 无；C1 机器验收完成。

## Next

- 独立提交 Cloud/Workspace 并归档 C1；按用户指令激活 M5-C2。

## Blockers

None.

## Recent verification

- 两仓起始工作区无其他人的未提交更改；Workspace 本轮只更新 M4/M5 Delivery 文档。
- `go test ./internal/modules/production/service -run 'Test(NextComposeRun|ComposeSchedule)' -count=1` PASS。

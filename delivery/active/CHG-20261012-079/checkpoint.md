# Checkpoint: CHG-20261012-079

- CHG: `CHG-20261012-079`（M4-B 合成策略与版本）
- Status: IMPLEMENTING
- Updated: 2026-10-12

## Completed

- CHG070 与 M4-A 的用户签收已记录；M4-C2 范围已从 M4-C3 的任务创建与快照中分开。
- 已核对 Cloud 现状：`production` 仅有 M4-A 素材/使用关系接口，`/compose-strategy` 两端仍为 `ComingSoon.vue`，策略表和合同尚不存在。
- T-01：首个受控模板为 `basic_cut` v1.0，仅允许 16:9 / 9:16 和比例覆盖；字幕、BGM、片尾因没有资源合同而拒绝启用。新增策略当前表和不可变版本表的 Migration。

## Current

执行 T-02：发布策略合同并实现 Cloud Repository、Service、Handler。

## Next

1. 完成 T-02 权限、版本、复制和 API 验证；随后实现共用页面。

## Blocked

- 无待决产品或架构问题；首个受控模板参数作为 T-01 的工程设计收口。

## Recent verification

| 检查 | 结果 |
| --- | --- |
| M4-A 用户走查 | 2026-10-12 用户确认通过；见 `delivery/reports/2026-10-12-m4-a-signoff.md` |
| CHG070 | 2026-10-12 用户确认走查通过并归档 |
| T-01 单测 | `go test ./internal/modules/production/model ./internal/infra/database/migration -count=1` PASS；其中模板非法参数和 Migration 结构测试先失败后通过 |
| T-01 真实数据库 | 尚未执行，T-04 将用 MySQL 验证首次迁移和再次执行 |

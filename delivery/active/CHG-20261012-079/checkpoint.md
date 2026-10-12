# Checkpoint: CHG-20261012-079

- CHG: `CHG-20261012-079`（M4-B 合成策略与版本）
- Status: IMPLEMENTING
- Updated: 2026-10-12

## Completed

- CHG070 与 M4-A 的用户签收已记录；M4-C2 范围已从 M4-C3 的任务创建与快照中分开。
- 已核对 Cloud 现状：`production` 仅有 M4-A 素材/使用关系接口，`/compose-strategy` 两端仍为 `ComingSoon.vue`，策略表和合同尚不存在。
- T-01：首个受控模板为 `basic_cut` v1.0，仅允许 16:9 / 9:16 和比例覆盖；字幕、BGM、片尾因没有资源合同而拒绝启用。新增策略当前表和不可变版本表的 Migration。
- T-02：Cloud 发布策略合同与命名错误；实现策略 Repository、Service、Handler。创建和修改在事务里写版本，修改用 `expected_version` 防止覆盖，列表在 SQL 层按团队和游戏过滤；未知请求字段被拒绝。顺手删去所改契约与 wire 测试开头的历史过程注释。
- T-03：新增共用策略页面 `modules/compose/pages/ComposeStrategyPage.vue` 与 API Client `shared/api/compose.js`，替换两端 `/compose-strategy` 的 ComingSoon 占位。高级运营/管理员可创建、编辑（打开时定格 expected_version）、复制（只发名称）与查看版本；普通运营只读。表单选项全部来自模板目录接口，字幕/BGM/片尾呈禁用态；字段级报错用 FormError，15204 冲突具名处理并重拉列表。routerParity 与列表页规范测试同步钉住两端同页。

## Current

T-03 已完成实现与自动验证，待独立提交。

## Next

1. 提交 T-03（wt-media-cloud）。
2. 执行 T-04：真实 MySQL 迁移、API 角色矩阵读回与页面走查、回归与证据。

## Blocked

- 无待决产品或架构问题；首个受控模板参数作为 T-01 的工程设计收口。

## Recent verification

| 检查 | 结果 |
| --- | --- |
| M4-A 用户走查 | 2026-10-12 用户确认通过；见 `delivery/reports/2026-10-12-m4-a-signoff.md` |
| CHG070 | 2026-10-12 用户确认走查通过并归档 |
| T-01 单测 | `go test ./internal/modules/production/model ./internal/infra/database/migration -count=1` PASS；其中模板非法参数和 Migration 结构测试先失败后通过 |
| T-01 真实数据库 | 尚未执行，T-04 将用 MySQL 验证首次迁移和再次执行 |
| T-02 单测 | `go test ./internal/modules/production/... ./internal/infra/database/migration -count=1` PASS；权限、非法请求、版本冲突、事务回滚均有定向测试 |
| T-02 合同 | Ruby YAML 解析四份 Cloud 合同 PASS；Go wire 测试对照返回字段 PASS |
| T-03 单测 | web/ 下 `npx vitest run` 全量 58 文件 527 测试 PASS；新增测试先红（模块与页面不存在、parity 指向 ComingSoon）后绿 |
| T-03 构建 | `npm run build:cloud`、`npm run build:desktop` PASS；两端 dist 均含 ComposeStrategyPage 分块并带 API 路径与页面标题 |
